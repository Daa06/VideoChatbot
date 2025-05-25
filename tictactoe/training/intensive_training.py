#!/usr/bin/env python3
"""
Intensive Training Script for Tic-Tac-Toe Neural Network
"""

import sys
import os
# Add parent directory to path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

from models.neural_network import TicTacToeAgent
from training.trainer import TicTacToeTrainer

def quick_boost_training():
    """Quick training boost for immediate improvement"""
    
    print("⚡ QUICK TRAINING BOOST")
    print("=" * 30)
    
    agent = TicTacToeAgent(learning_rate=0.003)  # Higher learning rate
    trainer = TicTacToeTrainer(agent)
    
    # Focused training
    print("🎯 Focused Random Training...")
    trainer.train_against_random(episodes=500, batch_size=64)
    
    print("🎯 Focused Self-Play...")
    trainer.train_self_play(episodes=500, batch_size=64)
    
    # Quick evaluation
    eval_results = trainer.evaluate_agent("random", 100)
    print(f"⚡ Quick Results: {eval_results['win_rate']:.1%} win rate vs Random")
    
    agent.save_model("quick_trained_model.pth")
    print("💾 Quick model saved!")
    
    return agent

def intensive_training():
    """Perform intensive training with multiple phases"""
    
    print("🧠 INTENSIVE NEURAL NETWORK TRAINING")
    print("=" * 50)
    
    # Create agent and trainer
    agent = TicTacToeAgent(learning_rate=0.001)
    trainer = TicTacToeTrainer(agent)
    
    print("📚 Phase 1: Extended Random Training")
    print("-" * 30)
    results1 = trainer.train_against_random(episodes=1000, batch_size=32)
    print(f"✅ Phase 1 Complete - Win Rate: {results1['win_rate']:.3f}")
    
    print("\n📚 Phase 2: Extended Self-Play")
    print("-" * 30)
    results2 = trainer.train_self_play(episodes=1000, batch_size=32)
    print(f"✅ Phase 2 Complete - Win Rate: {results2['win_rate']:.3f}")
    
    print("\n📚 Phase 3: Heuristic Challenge")
    print("-" * 30)
    results3 = trainer.train_against_heuristic(episodes=500, batch_size=32)
    print(f"✅ Phase 3 Complete - Win Rate: {results3['win_rate']:.3f}")
    
    print("\n🎯 FINAL EVALUATION")
    print("=" * 30)
    
    # Final evaluation
    eval_random = trainer.evaluate_agent("random", 200)
    eval_heuristic = trainer.evaluate_agent("heuristic", 200)
    
    print(f"\n🏆 FINAL RESULTS:")
    print(f"📊 vs Random: {eval_random['win_rate']:.1%} wins, {eval_random['draw_rate']:.1%} draws")
    print(f"📊 vs Heuristic: {eval_heuristic['win_rate']:.1%} wins, {eval_heuristic['draw_rate']:.1%} draws")
    
    # Save the trained model
    agent.save_model("models/intensive_trained_model.pth")
    print(f"\n💾 Model saved as 'models/intensive_trained_model.pth'")
    
    # Generate training plots
    trainer.plot_training_progress("intensive_training_progress.png")
    print(f"📈 Training plots saved as 'intensive_training_progress.png'")
    
    return agent, trainer

def main():
    print("🎯 Choose Training Mode:")
    print("1. Quick Boost (1000 episodes, ~3 minutes)")
    print("2. Intensive Training (2500 episodes, ~8 minutes)")
    print("3. Custom Training")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            quick_boost_training()
        elif choice == "2":
            intensive_training()
        elif choice == "3":
            custom_episodes = int(input("Enter number of episodes: "))
            agent = TicTacToeAgent()
            trainer = TicTacToeTrainer(agent)
            trainer.train_against_random(episodes=custom_episodes, batch_size=32)
            eval_results = trainer.evaluate_agent("random", 100)
            print(f"Results: {eval_results['win_rate']:.1%} win rate")
        else:
            print("❌ Invalid choice")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Training interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("\n🎉 Training completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 