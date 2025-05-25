import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from typing import List, Tuple
import random

class TicTacToeNet(nn.Module):
    """Neural Network for Tic-Tac-Toe move prediction"""
    
    def __init__(self, input_size=9, hidden_size=128, output_size=9):
        super(TicTacToeNet, self).__init__()
        
        # Network architecture
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc4 = nn.Linear(hidden_size // 2, output_size)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize network weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """Forward pass through the network"""
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x
    
    def predict_move(self, board_state: np.ndarray, valid_moves: List[Tuple[int, int]], 
                     temperature: float = 1.0) -> Tuple[int, int]:
        """Predict the best move given a board state"""
        self.eval()
        
        with torch.no_grad():
            # Convert board to tensor
            board_tensor = torch.FloatTensor(board_state.flatten()).unsqueeze(0)
            
            # Get move probabilities
            move_logits = self.forward(board_tensor).squeeze()
            
            # Apply temperature for exploration
            if temperature > 0:
                move_probs = F.softmax(move_logits / temperature, dim=0)
            else:
                move_probs = F.softmax(move_logits, dim=0)
            
            # Mask invalid moves
            valid_move_probs = torch.zeros_like(move_probs)
            for row, col in valid_moves:
                idx = row * 3 + col
                valid_move_probs[idx] = move_probs[idx]
            
            # Normalize probabilities
            if valid_move_probs.sum() > 0:
                valid_move_probs = valid_move_probs / valid_move_probs.sum()
            else:
                # Fallback to uniform distribution
                for row, col in valid_moves:
                    idx = row * 3 + col
                    valid_move_probs[idx] = 1.0 / len(valid_moves)
            
            # Sample move based on probabilities
            if temperature > 0:
                move_idx = torch.multinomial(valid_move_probs, 1).item()
            else:
                move_idx = torch.argmax(valid_move_probs).item()
            
            return (move_idx // 3, move_idx % 3)

class TicTacToeAgent:
    """AI Agent that uses the neural network to play Tic-Tac-Toe"""
    
    def __init__(self, learning_rate=0.001, device='cpu'):
        self.device = device
        self.network = TicTacToeNet().to(device)
        self.optimizer = optim.Adam(self.network.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
        # Training statistics
        self.training_history = {
            'losses': [],
            'win_rates': [],
            'episodes': []
        }
    
    def get_move(self, board_state: np.ndarray, valid_moves: List[Tuple[int, int]], 
                 temperature: float = 0.1) -> Tuple[int, int]:
        """Get the agent's move"""
        return self.network.predict_move(board_state, valid_moves, temperature)
    
    def train_step(self, states: List[np.ndarray], actions: List[int], rewards: List[float]):
        """Perform one training step"""
        self.network.train()
        
        # Convert to tensors
        state_tensor = torch.FloatTensor(np.array(states)).to(self.device)
        action_tensor = torch.LongTensor(actions).to(self.device)
        reward_tensor = torch.FloatTensor(rewards).to(self.device)
        
        # Forward pass
        q_values = self.network(state_tensor)
        q_values_for_actions = q_values.gather(1, action_tensor.unsqueeze(1)).squeeze()
        
        # Compute loss
        loss = self.criterion(q_values_for_actions, reward_tensor)
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        torch.save({
            'model_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history
        }, filepath)
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        checkpoint = torch.load(filepath, map_location=self.device, weights_only=False)
        self.network.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.training_history = checkpoint.get('training_history', {
            'losses': [], 'win_rates': [], 'episodes': []
        })

class RandomAgent:
    """Random move agent for training opponent"""
    
    def get_move(self, board_state: np.ndarray, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Get a random valid move"""
        return random.choice(valid_moves)

class HeuristicAgent:
    """Heuristic-based agent for medium difficulty"""
    
    def get_move(self, board_state: np.ndarray, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Get move based on simple heuristics"""
        
        # Check for winning move
        for row, col in valid_moves:
            test_board = board_state.copy()
            test_board[row, col] = -1  # Assume this agent is O
            if self._check_win(test_board, -1):
                return (row, col)
        
        # Check for blocking opponent's win
        for row, col in valid_moves:
            test_board = board_state.copy()
            test_board[row, col] = 1  # Assume opponent is X
            if self._check_win(test_board, 1):
                return (row, col)
        
        # Take center if available
        if (1, 1) in valid_moves:
            return (1, 1)
        
        # Take corners
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        available_corners = [move for move in corners if move in valid_moves]
        if available_corners:
            return random.choice(available_corners)
        
        # Take any remaining move
        return random.choice(valid_moves)
    
    def _check_win(self, board: np.ndarray, player: int) -> bool:
        """Check if the player has won"""
        # Check rows
        for row in board:
            if np.sum(row) == player * 3:
                return True
        
        # Check columns
        for col in range(3):
            if np.sum(board[:, col]) == player * 3:
                return True
        
        # Check diagonals
        if np.sum([board[i, i] for i in range(3)]) == player * 3:
            return True
        if np.sum([board[i, 2-i] for i in range(3)]) == player * 3:
            return True
        
        return False 