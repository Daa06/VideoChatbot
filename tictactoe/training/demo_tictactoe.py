#!/usr/bin/env python3
"""
Demo script for Neural Network Tic-Tac-Toe

This script demonstrates the training process and capabilities
of the neural network Tic-Tac-Toe implementation.
"""

import sys
import os
# Add parent directory to path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from game.tictactoe import TicTacToe, Player, GameResult
from models.neural_network import TicTacToeAgent, RandomAgent, HeuristicAgent
from training.trainer import TicTacToeTrainer

def demo_game_logic():
    """Demonstrate basic game logic"""
    print("🎮 Demonstrating Game Logic")
    print("=" * 40)
    
    game = TicTacToe()
    print("Initial board:")
    game.print_board()
    
    # Make some moves
    moves = [(1, 1), (0, 0), (0, 1), (2, 2), (2, 1)]
    for i, (row, col) in enumerate(moves):
        player = "X" if i % 2 == 0 else "O"
        print(f"Player {player} moves to ({row}, {col})")
        game.make_move(row, col)
        game.print_board()
        
        if game.game_over:
            result = game.get_result()
            if result == GameResult.X_WINS:
                print("X wins!")
            elif result == GameResult.O_WINS:
                print("O wins!")
            else:
                print("It's a draw!")
            break
    
    print()

def demo_agents():
    """Demonstrate different AI agents"""
    print("🤖 Demonstrating AI Agents")
    print("=" * 40)
    
    # Test random agent
    print("Random Agent vs Heuristic Agent (10 games):")
    random_agent = RandomAgent()
    heuristic_agent = HeuristicAgent()
    
    random_wins = 0
    heuristic_wins = 0
    draws = 0
    
    for _ in range(10):
        game = TicTacToe()
        
        while not game.game_over:
            current_state = game.get_board_state()
            valid_moves = game.get_valid_moves()
            
            if game.current_player == Player.X:
                move = random_agent.get_move(current_state, valid_moves)
            else:
                move = heuristic_agent.get_move(current_state, valid_moves)
            
            game.make_move(move[0], move[1])
        
        result = game.get_result()
        if result == GameResult.X_WINS:
            random_wins += 1
        elif result == GameResult.O_WINS:
            heuristic_wins += 1
        else:
            draws += 1
    
    print(f"Random Agent (X): {random_wins} wins")
    print(f"Heuristic Agent (O): {heuristic_wins} wins")
    print(f"Draws: {draws}")
    print()

def demo_neural_network_training():
    """Demonstrate neural network training"""
    print("🧠 Demonstrating Neural Network Training")
    print("=" * 40)
    
    # Create agent and trainer
    agent = TicTacToeAgent()
    trainer = TicTacToeTrainer(agent)
    
    print("Training against random opponent (200 episodes)...")
    results_random = trainer.train_against_random(episodes=200, batch_size=32)
    
    print(f"Results vs Random: Win Rate = {results_random['win_rate']:.3f}")
    print()
    
    print("Training against heuristic opponent (200 episodes)...")
    results_heuristic = trainer.train_against_heuristic(episodes=200, batch_size=32)
    
    print(f"Results vs Heuristic: Win Rate = {results_heuristic['win_rate']:.3f}")
    print()
    
    print("Self-play training (200 episodes)...")
    results_self_play = trainer.train_self_play(episodes=200, batch_size=32)
    
    print(f"Results Self-play: Win Rate = {results_self_play['win_rate']:.3f}")
    print()
    
    # Evaluate the trained agent
    print("Evaluating trained agent...")
    eval_random = trainer.evaluate_agent("random", 50)
    eval_heuristic = trainer.evaluate_agent("heuristic", 50)
    
    print(f"Final evaluation vs Random: {eval_random['win_rate']:.3f} win rate")
    print(f"Final evaluation vs Heuristic: {eval_heuristic['win_rate']:.3f} win rate")
    
    # Plot training progress
    print("\nDisplaying training progress...")
    trainer.plot_training_progress("training_progress.png")
    
    return agent, trainer

def demo_human_vs_ai_simulation():
    """Simulate a human vs AI game"""
    print("👤 Simulating Human vs AI Game")
    print("=" * 40)
    
    # Use a pre-trained agent (or train a quick one)
    agent = TicTacToeAgent()
    trainer = TicTacToeTrainer(agent)
    
    # Quick training
    print("Quick training for demo...")
    trainer.train_against_random(episodes=100, batch_size=16)
    
    game = TicTacToe()
    human_is_x = True
    
    print("Starting Human vs AI game simulation...")
    print("(Simulated human moves will be random for demo)")
    game.print_board()
    
    while not game.game_over:
        current_state = game.get_board_state()
        valid_moves = game.get_valid_moves()
        
        if (game.current_player == Player.X and human_is_x) or \
           (game.current_player == Player.O and not human_is_x):
            # Simulated human move (random for demo)
            move = RandomAgent().get_move(current_state, valid_moves)
            player_name = "Human"
        else:
            # AI move
            move = agent.get_move(current_state, valid_moves, temperature=0.0)
            player_name = "AI"
        
        symbol = "X" if game.current_player == Player.X else "O"
        print(f"{player_name} ({symbol}) moves to {move}")
        game.make_move(move[0], move[1])
        game.print_board()
    
    result = game.get_result()
    if result == GameResult.DRAW:
        print("Game ended in a draw!")
    elif (result == GameResult.X_WINS and human_is_x) or \
         (result == GameResult.O_WINS and not human_is_x):
        print("Human wins!")
    else:
        print("AI wins!")
    
    print()

def main():
    """Run the complete demo"""
    print("🎯 Neural Network Tic-Tac-Toe Demo")
    print("=" * 50)
    print("This demo showcases the neural network implementation")
    print("for the bonus task of the Video Chat project.")
    print("=" * 50)
    print()
    
    try:
        # Demo 1: Basic game logic
        demo_game_logic()
        
        # Demo 2: AI agents comparison
        demo_agents()
        
        # Demo 3: Neural network training
        agent, trainer = demo_neural_network_training()
        
        # Demo 4: Human vs AI simulation
        demo_human_vs_ai_simulation()
        
        print("🎉 Demo completed successfully!")
        print("\nTo play the game interactively, run:")
        print("python main.py")
        print("\nThis will open the GUI where you can:")
        print("• Train the neural network with different opponents")
        print("• Play against the AI with adjustable difficulty")
        print("• Watch AI vs AI matches")
        print("• View training progress and save/load models")
        
    except Exception as e:
        print(f"Demo failed with error: {str(e)}")
        print("Make sure all dependencies are installed:")
        print("pip install torch numpy matplotlib")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 