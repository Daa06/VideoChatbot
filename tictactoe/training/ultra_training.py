#!/usr/bin/env python3
"""
ULTRA-INTENSIVE Training Script for Tic-Tac-Toe Neural Network
Target: 80%+ win rate against random opponents
"""

import sys
import os
# Add parent directory to path so we can import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

from models.neural_network import TicTacToeAgent
from training.trainer import TicTacToeTrainer

def ultra_intensive_training():
    """ULTRA-INTENSIVE training with massive episodes"""
    
    print("🔥 ULTRA-INTENSIVE NEURAL NETWORK TRAINING")
    print("🎯 TARGET: 80%+ WIN RATE")
    print("=" * 60)
    
    # Create agent with optimized parameters
    agent = TicTacToeAgent(learning_rate=0.002)  # Higher learning rate
    trainer = TicTacToeTrainer(agent)
    
    print("📚 Phase 1: MASSIVE Random Training")
    print("-" * 40)
    results1 = trainer.train_against_random(episodes=5000, batch_size=64)
    print(f"✅ Phase 1 Complete - Win Rate: {results1['win_rate']:.3f}")
    
    print("\n📚 Phase 2: EXTENDED Self-Play")
    print("-" * 40)
    results2 = trainer.train_self_play(episodes=3000, batch_size=64)
    print(f"✅ Phase 2 Complete - Win Rate: {results2['win_rate']:.3f}")
    
    print("\n📚 Phase 3: MORE Random Training (Fine-tuning)")
    print("-" * 40)
    # Lower learning rate for fine-tuning
    agent.optimizer.param_groups[0]['lr'] = 0.001
    results3 = trainer.train_against_random(episodes=3000, batch_size=64)
    print(f"✅ Phase 3 Complete - Win Rate: {results3['win_rate']:.3f}")
    
    print("\n📚 Phase 4: ADVANCED Self-Play")
    print("-" * 40)
    results4 = trainer.train_self_play(episodes=2000, batch_size=64)
    print(f"✅ Phase 4 Complete - Win Rate: {results4['win_rate']:.3f}")
    
    print("\n📚 Phase 5: FINAL Random Mastery")
    print("-" * 40)
    # Even lower learning rate for precision
    agent.optimizer.param_groups[0]['lr'] = 0.0005
    results5 = trainer.train_against_random(episodes=2000, batch_size=64)
    print(f"✅ Phase 5 Complete - Win Rate: {results5['win_rate']:.3f}")
    
    print("\n🎯 ULTRA EVALUATION (500 games each)")
    print("=" * 40)
    
    # Extensive evaluation
    eval_random = trainer.evaluate_agent("random", 500)
    eval_heuristic = trainer.evaluate_agent("heuristic", 500)
    
    print(f"\n🏆 ULTRA RESULTS:")
    print(f"🔥 vs Random: {eval_random['win_rate']:.1%} wins, {eval_random['draw_rate']:.1%} draws")
    print(f"🛡️ vs Heuristic: {eval_heuristic['win_rate']:.1%} wins, {eval_heuristic['draw_rate']:.1%} draws")
    
    # Check if target achieved
    if eval_random['win_rate'] >= 0.80:
        print(f"\n🎉 TARGET ACHIEVED! {eval_random['win_rate']:.1%} >= 80%")
    else:
        print(f"\n⚠️ Target not reached: {eval_random['win_rate']:.1%} < 80%")
        print("💡 Consider running MEGA training for even better results!")
    
    # Save the ultra-trained model
    agent.save_model("models/ultra_trained_model.pth")
    print(f"\n💾 ULTRA Model saved as 'models/ultra_trained_model.pth'")
    
    # Generate training plots
    trainer.plot_training_progress("ultra_training_progress.png")
    print(f"📈 ULTRA Training plots saved")
    
    return agent, trainer

def mega_training():
    """MEGA training - even more intensive"""
    
    print("🚀 MEGA NEURAL NETWORK TRAINING")
    print("🎯 TARGET: 85%+ WIN RATE")
    print("=" * 60)
    
    # Create agent with even more optimized parameters
    agent = TicTacToeAgent(learning_rate=0.003)
    trainer = TicTacToeTrainer(agent)
    
    print("📚 MEGA Phase 1: ENORMOUS Random Training")
    print("-" * 40)
    results1 = trainer.train_against_random(episodes=10000, batch_size=128)
    print(f"✅ MEGA Phase 1 Complete - Win Rate: {results1['win_rate']:.3f}")
    
    print("\n📚 MEGA Phase 2: MASSIVE Self-Play")
    print("-" * 40)
    results2 = trainer.train_self_play(episodes=8000, batch_size=128)
    print(f"✅ MEGA Phase 2 Complete - Win Rate: {results2['win_rate']:.3f}")
    
    print("\n📚 MEGA Phase 3: ULTIMATE Random Mastery")
    print("-" * 40)
    agent.optimizer.param_groups[0]['lr'] = 0.001
    results3 = trainer.train_against_random(episodes=7000, batch_size=128)
    print(f"✅ MEGA Phase 3 Complete - Win Rate: {results3['win_rate']:.3f}")
    
    print("\n🎯 MEGA EVALUATION (1000 games)")
    print("=" * 40)
    
    eval_random = trainer.evaluate_agent("random", 1000)
    eval_heuristic = trainer.evaluate_agent("heuristic", 1000)
    
    print(f"\n🏆 MEGA RESULTS:")
    print(f"🔥 vs Random: {eval_random['win_rate']:.1%} wins")
    print(f"🛡️ vs Heuristic: {eval_heuristic['win_rate']:.1%} wins, {eval_heuristic['draw_rate']:.1%} draws")
    
    agent.save_model("models/mega_trained_model.pth")
    trainer.plot_training_progress("mega_training_progress.png")
    print(f"\n💾 MEGA Model saved!")
    
    return agent, trainer

def custom_intensive_training():
    """Custom training with user-defined parameters"""
    
    print("🎯 CUSTOM INTENSIVE TRAINING")
    print("=" * 40)
    
    try:
        episodes = int(input("Enter total episodes (recommended: 10000+): "))
        learning_rate = float(input("Enter learning rate (recommended: 0.002): "))
        batch_size = int(input("Enter batch size (recommended: 64-128): "))
        
        agent = TicTacToeAgent(learning_rate=learning_rate)
        trainer = TicTacToeTrainer(agent)
        
        # Split training into phases
        phase1_episodes = episodes // 2
        phase2_episodes = episodes - phase1_episodes
        
        print(f"\n🔥 Phase 1: {phase1_episodes} episodes vs Random")
        trainer.train_against_random(episodes=phase1_episodes, batch_size=batch_size)
        
        print(f"\n🔥 Phase 2: {phase2_episodes} episodes Self-Play")
        trainer.train_self_play(episodes=phase2_episodes, batch_size=batch_size)
        
        # Evaluation
        eval_results = trainer.evaluate_agent("random", 500)
        print(f"\n🏆 CUSTOM RESULTS: {eval_results['win_rate']:.1%} win rate")
        
        agent.save_model("models/custom_trained_model.pth")
        print("💾 Custom model saved!")
        
        return agent
        
    except ValueError:
        print("❌ Invalid input!")
        return None

def main():
    print("🎯 Choose INTENSIVE Training Mode:")
    print("1. ULTRA Training (15,000 episodes, ~5-10 minutes)")
    print("2. MEGA Training (25,000 episodes, ~10-15 minutes)")
    print("3. Custom Intensive Training")
    print("4. Quick Test (1000 episodes)")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            ultra_intensive_training()
        elif choice == "2":
            mega_training()
        elif choice == "3":
            custom_intensive_training()
        elif choice == "4":
            # Quick test
            agent = TicTacToeAgent(learning_rate=0.003)
            trainer = TicTacToeTrainer(agent)
            trainer.train_against_random(episodes=1000, batch_size=64)
            eval_results = trainer.evaluate_agent("random", 200)
            print(f"Quick Results: {eval_results['win_rate']:.1%} win rate")
            agent.save_model("models/quick_test_model.pth")
        else:
            print("❌ Invalid choice")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Training interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("\n🎉 INTENSIVE Training completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 