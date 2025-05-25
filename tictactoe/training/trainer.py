import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import random
from collections import deque
import time
import sys

from game.tictactoe import TicTacToe, Player, GameResult
from models.neural_network import TicTacToeAgent, RandomAgent, HeuristicAgent

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total: 
        print()

class TicTacToeTrainer:
    """Training system for the Tic-Tac-Toe neural network"""
    
    def __init__(self, agent: TicTacToeAgent):
        self.agent = agent
        self.training_stats = {
            'episodes': [],
            'win_rates': [],
            'draw_rates': [],
            'loss_rates': [],
            'losses': [],
            'avg_game_length': []
        }
    
    def train_against_random(self, episodes: int = 1000, batch_size: int = 32) -> Dict:
        """Train the agent against random opponent"""
        print(f"Training against Random opponent for {episodes} episodes...")
        
        opponent = RandomAgent()
        return self._train_episodes(opponent, episodes, batch_size, "Random")
    
    def train_against_heuristic(self, episodes: int = 1000, batch_size: int = 32) -> Dict:
        """Train the agent against heuristic opponent"""
        print(f"Training against Heuristic opponent for {episodes} episodes...")
        
        opponent = HeuristicAgent()
        return self._train_episodes(opponent, episodes, batch_size, "Heuristic")
    
    def train_self_play(self, episodes: int = 1000, batch_size: int = 32) -> Dict:
        """Train the agent against itself"""
        print(f"Training with Self-play for {episodes} episodes...")
        
        return self._train_self_play_episodes(episodes, batch_size)
    
    def _train_episodes(self, opponent, episodes: int, batch_size: int, opponent_name: str) -> Dict:
        """Train for a number of episodes against a specific opponent"""
        
        wins, draws, losses = 0, 0, 0
        total_loss = 0
        game_lengths = []
        
        # Experience replay buffer
        experience_buffer = deque(maxlen=10000)
        
        for episode in range(episodes):
            # Update progress bar
            if episode % 10 == 0:
                print_progress_bar(episode, episodes, 
                                 prefix=f'{opponent_name} Training:', 
                                 suffix=f'Episode {episode}/{episodes}')
            
            game = TicTacToe()
            states, actions, rewards = [], [], []
            
            # Randomly choose who goes first
            agent_is_x = random.choice([True, False])
            
            while not game.game_over:
                current_state = game.get_board_state()
                valid_moves = game.get_valid_moves()
                
                if (game.current_player == Player.X and agent_is_x) or \
                   (game.current_player == Player.O and not agent_is_x):
                    # Agent's turn
                    move = self.agent.get_move(current_state, valid_moves, temperature=0.3)
                    action_idx = move[0] * 3 + move[1]
                    
                    states.append(current_state.flatten())
                    actions.append(action_idx)
                    
                else:
                    # Opponent's turn
                    move = opponent.get_move(current_state, valid_moves)
                
                game.make_move(move[0], move[1])
            
            # Calculate rewards based on game outcome
            result = game.get_result()
            game_lengths.append(game.move_count)
            
            if result == GameResult.DRAW:
                draws += 1
                reward = 0.1  # Small positive reward for draw
            elif (result == GameResult.X_WINS and agent_is_x) or \
                 (result == GameResult.O_WINS and not agent_is_x):
                wins += 1
                reward = 1.0  # Win reward
            else:
                losses += 1
                reward = -1.0  # Loss penalty
            
            # Assign rewards to all agent moves
            rewards = [reward] * len(states)
            
            # Add experience to buffer
            for state, action, reward in zip(states, actions, rewards):
                experience_buffer.append((state, action, reward))
            
            # Train on batch
            if len(experience_buffer) >= batch_size and episode % 10 == 0:
                batch = random.sample(experience_buffer, batch_size)
                batch_states, batch_actions, batch_rewards = zip(*batch)
                
                loss = self.agent.train_step(list(batch_states), list(batch_actions), list(batch_rewards))
                total_loss += loss
            
            # Log progress
            if (episode + 1) % 100 == 0:
                win_rate = wins / (episode + 1)
                print(f"\nEpisode {episode + 1}/{episodes} - Win Rate: {win_rate:.3f}, "
                      f"Draw Rate: {draws/(episode + 1):.3f}, "
                      f"Avg Game Length: {np.mean(game_lengths):.1f}")
        
        # Final progress bar update
        print_progress_bar(episodes, episodes, 
                         prefix=f'{opponent_name} Training:', 
                         suffix='Complete!')
        
        # Calculate final statistics
        total_games = episodes
        win_rate = wins / total_games
        draw_rate = draws / total_games
        loss_rate = losses / total_games
        avg_loss = total_loss / max(1, episodes // 10)
        avg_game_length = np.mean(game_lengths)
        
        # Update training stats
        self.training_stats['episodes'].append(episodes)
        self.training_stats['win_rates'].append(win_rate)
        self.training_stats['draw_rates'].append(draw_rate)
        self.training_stats['loss_rates'].append(loss_rate)
        self.training_stats['losses'].append(avg_loss)
        self.training_stats['avg_game_length'].append(avg_game_length)
        
        print(f"\n{opponent_name} Training Complete!")
        print(f"Win Rate: {win_rate:.3f}")
        print(f"Draw Rate: {draw_rate:.3f}")
        print(f"Loss Rate: {loss_rate:.3f}")
        print(f"Average Game Length: {avg_game_length:.1f}")
        print(f"Average Loss: {avg_loss:.4f}")
        
        return {
            'win_rate': win_rate,
            'draw_rate': draw_rate,
            'loss_rate': loss_rate,
            'avg_loss': avg_loss,
            'avg_game_length': avg_game_length
        }
    
    def _train_self_play_episodes(self, episodes: int, batch_size: int) -> Dict:
        """Train using self-play"""
        
        wins_x, wins_o, draws = 0, 0, 0
        total_loss = 0
        game_lengths = []
        
        # Experience replay buffer
        experience_buffer = deque(maxlen=10000)
        
        for episode in range(episodes):
            # Update progress bar
            if episode % 10 == 0:
                print_progress_bar(episode, episodes, 
                                 prefix='Self-Play Training:', 
                                 suffix=f'Episode {episode}/{episodes}')
            
            game = TicTacToe()
            states_x, actions_x = [], []
            states_o, actions_o = [], []
            
            while not game.game_over:
                current_state = game.get_board_state()
                valid_moves = game.get_valid_moves()
                
                # Agent plays both sides with different temperatures for variety
                if game.current_player == Player.X:
                    move = self.agent.get_move(current_state, valid_moves, temperature=0.5)
                    action_idx = move[0] * 3 + move[1]
                    states_x.append(current_state.flatten())
                    actions_x.append(action_idx)
                else:
                    move = self.agent.get_move(current_state, valid_moves, temperature=0.3)
                    action_idx = move[0] * 3 + move[1]
                    states_o.append(current_state.flatten())
                    actions_o.append(action_idx)
                
                game.make_move(move[0], move[1])
            
            # Calculate rewards
            result = game.get_result()
            game_lengths.append(game.move_count)
            
            if result == GameResult.DRAW:
                draws += 1
                reward_x = reward_o = 0.1
            elif result == GameResult.X_WINS:
                wins_x += 1
                reward_x, reward_o = 1.0, -0.5
            else:
                wins_o += 1
                reward_x, reward_o = -0.5, 1.0
            
            # Add experiences to buffer
            for state, action in zip(states_x, actions_x):
                experience_buffer.append((state, action, reward_x))
            for state, action in zip(states_o, actions_o):
                experience_buffer.append((state, action, reward_o))
            
            # Train on batch
            if len(experience_buffer) >= batch_size and episode % 10 == 0:
                batch = random.sample(experience_buffer, batch_size)
                batch_states, batch_actions, batch_rewards = zip(*batch)
                
                loss = self.agent.train_step(list(batch_states), list(batch_actions), list(batch_rewards))
                total_loss += loss
            
            # Log progress
            if (episode + 1) % 100 == 0:
                print(f"\nEpisode {episode + 1}/{episodes} - "
                      f"X Wins: {wins_x}, O Wins: {wins_o}, Draws: {draws}, "
                      f"Avg Game Length: {np.mean(game_lengths):.1f}")
        
        # Final progress bar update
        print_progress_bar(episodes, episodes, 
                         prefix='Self-Play Training:', 
                         suffix='Complete!')
        
        # Calculate statistics
        total_games = episodes
        win_rate = (wins_x + wins_o) / (2 * total_games)  # Average win rate
        draw_rate = draws / total_games
        avg_loss = total_loss / max(1, episodes // 10)
        avg_game_length = np.mean(game_lengths)
        
        # Update training stats
        self.training_stats['episodes'].append(episodes)
        self.training_stats['win_rates'].append(win_rate)
        self.training_stats['draw_rates'].append(draw_rate)
        self.training_stats['loss_rates'].append(1 - win_rate - draw_rate)
        self.training_stats['losses'].append(avg_loss)
        self.training_stats['avg_game_length'].append(avg_game_length)
        
        print(f"\nSelf-Play Training Complete!")
        print(f"X Wins: {wins_x}, O Wins: {wins_o}, Draws: {draws}")
        print(f"Average Game Length: {avg_game_length:.1f}")
        print(f"Average Loss: {avg_loss:.4f}")
        
        return {
            'win_rate': win_rate,
            'draw_rate': draw_rate,
            'avg_loss': avg_loss,
            'avg_game_length': avg_game_length
        }
    
    def evaluate_agent(self, opponent_type: str = "random", games: int = 100) -> Dict:
        """Evaluate the trained agent"""
        print(f"\nEvaluating agent against {opponent_type} opponent...")
        
        if opponent_type == "random":
            opponent = RandomAgent()
        elif opponent_type == "heuristic":
            opponent = HeuristicAgent()
        else:
            raise ValueError("Unknown opponent type")
        
        wins, draws, losses = 0, 0, 0
        
        for game_num in range(games):
            # Update progress bar for evaluation
            if game_num % 10 == 0:
                print_progress_bar(game_num, games, 
                                 prefix=f'Evaluating vs {opponent_type}:', 
                                 suffix=f'Game {game_num}/{games}')
            
            game = TicTacToe()
            agent_is_x = random.choice([True, False])
            
            while not game.game_over:
                current_state = game.get_board_state()
                valid_moves = game.get_valid_moves()
                
                if (game.current_player == Player.X and agent_is_x) or \
                   (game.current_player == Player.O and not agent_is_x):
                    move = self.agent.get_move(current_state, valid_moves, temperature=0.0)
                else:
                    move = opponent.get_move(current_state, valid_moves)
                
                game.make_move(move[0], move[1])
            
            result = game.get_result()
            if result == GameResult.DRAW:
                draws += 1
            elif (result == GameResult.X_WINS and agent_is_x) or \
                 (result == GameResult.O_WINS and not agent_is_x):
                wins += 1
            else:
                losses += 1
        
        # Final progress bar update
        print_progress_bar(games, games, 
                         prefix=f'Evaluating vs {opponent_type}:', 
                         suffix='Complete!')
        
        win_rate = wins / games
        draw_rate = draws / games
        loss_rate = losses / games
        
        print(f"Evaluation Results against {opponent_type}:")
        print(f"Win Rate: {win_rate:.3f}")
        print(f"Draw Rate: {draw_rate:.3f}")
        print(f"Loss Rate: {loss_rate:.3f}")
        
        return {
            'win_rate': win_rate,
            'draw_rate': draw_rate,
            'loss_rate': loss_rate
        }
    
    def plot_training_progress(self, save_path: str = None):
        """Plot training progress"""
        if not self.training_stats['episodes']:
            print("No training data to plot")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        episodes = np.cumsum(self.training_stats['episodes'])
        
        # Win rates
        ax1.plot(episodes, self.training_stats['win_rates'], 'g-', label='Win Rate')
        ax1.plot(episodes, self.training_stats['draw_rates'], 'b-', label='Draw Rate')
        ax1.plot(episodes, self.training_stats['loss_rates'], 'r-', label='Loss Rate')
        ax1.set_xlabel('Episodes')
        ax1.set_ylabel('Rate')
        ax1.set_title('Game Outcome Rates')
        ax1.legend()
        ax1.grid(True)
        
        # Training loss
        ax2.plot(episodes, self.training_stats['losses'], 'purple')
        ax2.set_xlabel('Episodes')
        ax2.set_ylabel('Loss')
        ax2.set_title('Training Loss')
        ax2.grid(True)
        
        # Average game length
        ax3.plot(episodes, self.training_stats['avg_game_length'], 'orange')
        ax3.set_xlabel('Episodes')
        ax3.set_ylabel('Moves')
        ax3.set_title('Average Game Length')
        ax3.grid(True)
        
        # Win rate progression
        ax4.plot(episodes, self.training_stats['win_rates'], 'g-', linewidth=2)
        ax4.set_xlabel('Episodes')
        ax4.set_ylabel('Win Rate')
        ax4.set_title('Win Rate Progression')
        ax4.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training progress plot saved to {save_path}")
        
        plt.close()  # Close the figure to prevent display 