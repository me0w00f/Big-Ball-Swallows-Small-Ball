import torch
from lib.game_env import BallGameEnv
from lib.dqn_agent import DQNAgent
import argparse

def test(model_path, episodes=10, render=True):
    env = BallGameEnv(render_mode="human" if render else None)
    agent = DQNAgent(env.observation_space, env.action_space)
    # 使用 weights_only=True 来避免警告
    agent.model.load_state_dict(torch.load(model_path, weights_only=True))
    agent.epsilon = 0  # 测试时不需要探索
    
    for e in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action = agent.act(state)
            state, reward, done, _ = env.step(action)
            total_reward += reward
            
        print(f"Episode: {e+1}, Score: {total_reward}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--render", action="store_true")
    
    args = parser.parse_args()
    test(args.model, args.episodes, args.render)
