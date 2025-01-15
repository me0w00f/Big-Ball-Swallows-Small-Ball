import matplotlib.pyplot as plt
import pandas as pd
import wandb
import argparse

def plot_training_results(run_path):
    api = wandb.Api()
    run = api.run(run_path)
    
    # 获取训练数据
    history = pd.DataFrame(run.scan_history())
    
    # 绘制分数图
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history['episode'], history['score'], label='Score')
    plt.plot(history['episode'], history['avg_score'], label='Avg Score')
    plt.xlabel('Episode')
    plt.ylabel('Score')
    plt.title('Training Scores')
    plt.legend()
    
    # 绘制损失图
    plt.subplot(1, 2, 2)
    plt.plot(history['loss'], label='Loss')
    plt.xlabel('Training Step')
    plt.ylabel('Loss')
    plt.title('Training Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('training_results.png')
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_path", type=str, required=True,
                      help="WandB run path (e.g., 'username/project/runid')")
    args = parser.parse_args()
    plot_training_results(args.run_path)
