import wandb
import numpy as np
from lib.game_env import BallGameEnv
from lib.dqn_agent import DQNAgent
import torch
import argparse
import os
import platform
import psutil
import GPUtil

def get_system_info():
    """获取系统信息"""
    system_info = {
        "OS": platform.platform(),
        "Python": platform.python_version(),
        "CPU": platform.processor(),
        "Memory_Total": f"{psutil.virtual_memory().total / (1024**3):.2f}GB",
        "Memory_Available": f"{psutil.virtual_memory().available / (1024**3):.2f}GB",
        "PyTorch": torch.__version__,
    }
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            system_info["GPU"] = gpus[0].name
            system_info["GPU_Memory"] = f"{gpus[0].memoryTotal}MB"
    except:
        system_info["GPU"] = "Not Available"
    
    return system_info

def train(config):
    # 初始化wandb，包含系统信息
    wandb.init(
        project="ball-game-ai",
        config=config,
        settings=wandb.Settings(_disable_stats=True),
        tags=["optimized-rewards"],
        notes="Training with optimized reward system",
    )
    
    # 记录系统信息
    wandb.config.update(get_system_info())
    
    # 创建训练表格
    training_table = wandb.Table(columns=[
        "Episode", "Game Score", "Avg Game Score", 
        "Episode Reward", "Avg Reward", "Accuracy",
        "Loss", "Epsilon"
    ])
    
    env = BallGameEnv(render_mode="human" if config.render else None)
    agent = DQNAgent(env.observation_space, env.action_space)
    
    episode_scores = []
    episode_rewards = []
    
    for e in range(config.episodes):
        state = env.reset()
        episode_reward = 0
        steps = 0
        correct_actions = 0
        
        for t in range(config.max_steps):
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            
            if reward > 0:
                correct_actions += 1
            
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            episode_reward += reward
            steps += 1
            
            # 每100步记录一次训练数据
            if len(agent.memory) > config.batch_size and t % 100 == 0:
                loss = agent.replay(config.batch_size)
                if loss is not None:
                    wandb.log({
                        "training_loss": round(float(loss), 4),
                        "epsilon": round(float(agent.epsilon), 4)
                    })
            
            if done:
                break
        
        # 更新目标网络
        if e % config.target_update == 0:
            agent.update_target_model()
        
        # 计算关键指标
        game_score = int(env.player.get_score())  # 游戏实际得分
        episode_scores.append(game_score)
        episode_rewards.append(episode_reward)
        avg_score = np.mean(episode_scores[-100:])
        avg_reward = np.mean(episode_rewards[-100:])
        accuracy = round(correct_actions / steps if steps > 0 else 0, 4)
        
        # 记录每轮的关键指标
        metrics = {
            "game/score": game_score,
            "game/avg_score": round(float(avg_score), 2),
            "training/episode_reward": round(float(episode_reward), 2),
            "training/avg_reward": round(float(avg_reward), 2),
            "training/accuracy": accuracy,
            "training/epsilon": round(float(agent.epsilon), 4),
            "system/memory_used": psutil.Process().memory_info().rss / 1024**2,  # MB
            "system/cpu_percent": psutil.cpu_percent(),
        }
        
        if hasattr(agent, 'last_loss'):
            metrics["training/loss"] = round(float(agent.last_loss), 4)
        
        wandb.log(metrics)
        
        # 更新训练表格
        training_table.add_data(
            e, game_score, round(float(avg_score), 2),
            round(float(episode_reward), 2), round(float(avg_reward), 2),
            f"{accuracy:.2%}", 
            round(float(agent.last_loss), 4) if hasattr(agent, 'last_loss') else "N/A",
            round(float(agent.epsilon), 4)
        )
        
        # 打印训练信息
        print(f"\nEpisode: {e}/{config.episodes}")
        print(f"Game Score: {game_score}, Avg Score: {avg_score:.2f}")
        print(f"Episode Reward: {episode_reward:.2f}, Avg Reward: {avg_reward:.2f}")
        print(f"Accuracy: {accuracy:.2%}, Epsilon: {agent.epsilon:.4f}")
        if hasattr(agent, 'last_loss'):
            print(f"Loss: {agent.last_loss:.4f}")
        print("-" * 50)
        
        # 保存模型
        if e % config.save_freq == 0:
            torch.save(agent.model.state_dict(), f"models/model_{e}.pth")
    
    # 保存训练表格
    wandb.log({"training_history": training_table})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train the Ball Game AI agent')
    parser.add_argument("--episodes", type=int, default=2000,
                       help="Number of episodes to train (default: 2000)")
    parser.add_argument("--max_steps", type=int, default=1500,
                       help="Maximum steps per episode (default: 1500)")
    parser.add_argument("--batch_size", type=int, default=64,
                       help="Training batch size (default: 64)")
    parser.add_argument("--target_update", type=int, default=100,
                       help="Number of episodes between target network updates (default: 100)")
    parser.add_argument("--save_freq", type=int, default=200,
                       help="Number of episodes between model saves (default: 200)")
    parser.add_argument("--render", action="store_true",
                       help="Enable visual rendering during training")
    parser.add_argument("--save_dir", type=str, default="models",
                       help="Directory to save models (default: models)")
    
    config = parser.parse_args()
    
    # 创建保存模型的目录
    os.makedirs(config.save_dir, exist_ok=True)
    
    train(config)
