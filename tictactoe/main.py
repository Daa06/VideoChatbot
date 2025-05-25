#!/usr/bin/env python3
"""
Neural Network Tic-Tac-Toe Game

This is the bonus task implementation for the Video Chat project.
It features a neural network that learns to play Tic-Tac-Toe through
reinforcement learning with different training modes.

Features:
- Neural network trained with PyTorch
- Multiple difficulty levels (Easy/Medium/Hard)
- Training against Random, Heuristic, and Self-play opponents
- Real-time training visualization
- Human vs AI and AI vs AI game modes
- Model save/load functionality
- Training progress plots

Usage:
    python main.py
"""

import sys
import os

# Add the parent directory to the path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.game_interface import TicTacToeGUI

def main():
    """Main entry point for the Tic-Tac-Toe application"""
    
    print("🧠 Neural Network Tic-Tac-Toe")
    print("=" * 40)
    print("Starting the graphical interface...")
    print("\nFeatures:")
    print("• Train neural network against different opponents")
    print("• Play against AI with adjustable difficulty")
    print("• Watch AI vs AI matches")
    print("• View training progress and statistics")
    print("• Save and load trained models")
    print("\nEnjoy the game!")
    print("=" * 40)
    
    try:
        # Create and run the GUI application
        app = TicTacToeGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Goodbye!")
        
    except Exception as e:
        print(f"\nError starting the application: {str(e)}")
        print("Make sure you have all required dependencies installed:")
        print("- torch")
        print("- numpy")
        print("- matplotlib")
        print("- tkinter (usually comes with Python)")
        
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 