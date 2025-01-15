import wandb
import numpy as np
from lib.game_env import BallGameEnv
from lib.dqn_agent import DQNAgent
import torch
import argparse

def train(config):
    wandb.init(project="ball-game-ai", config=config)
    
    env = BallGameEnv(render_mode="human" if config.render else None)
    agent = DQNAgent(env.observation_space, env.action_space)
    
    scores = []
    
    for e in range(config.episodes):
        state = env.reset()
        total_reward = 0
        
        for time in range(config.max_steps):
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            
            if len(agent.memory) > config.batch_size:
                loss = agent.replay(config.batch_size)
                wandb.log({
                    "loss": loss,
                    "epsilon": agent.epsilon
                })
            
            if done:
                break
                
        # 更新目标网络
        if e % config.target_update == 0:
            agent.update_target_model()
            
        scores.append(total_reward)
        avg_score = np.mean(scores[-100:])
        
        wandb.log({
            "episode": e,
            "score": total_reward,
            "avg_score": avg_score
        })
        
        print(f"Episode: {e}/{config.episodes}, Score: {total_reward}, Avg Score: {avg_score:.2f}")
        
        # 保存模型
        if e % config.save_freq == 0:
            torch.save(agent.model.state_dict(), f"models/model_{e}.pth")
            wandb.save(f"models/model_{e}.pth")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--max_steps", type=int, default=1000)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--target_update", type=int, default=10)
    parser.add_argument("--save_freq", type=int, default=100)
    parser.add_argument("--render", action="store_true")
    
    config = parser.parse_args()
    train(config)
