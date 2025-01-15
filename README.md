![](./img/screenshot.png)
# Big Ball Swallows Small Ball

A simple and fun game based on Pygame where you control a color-changing ball and grow by swallowing smaller balls.

## Game Features

- Rainbow-colored player ball that changes color over time
- 6 different types of food dots with varying sizes and scores
- Dynamically moving food dots
- High score system
- Victory condition: Reach 10000 points
- Failure condition: Touch a larger ball

## Controls

- ↑ Move up
- ↓ Move down
- ← Move left
- → Move right
- SPACE Restart after game over

## Food Types

- Black dot (3px) - 10 points
- Green dot (5px) - 20 points
- Blue dot (7px) - 30 points
- Purple dot (9px) - 40 points
- Orange dot (12px) - 80 points
- Red dot (15px) - 160 points

## Game Strategy

1. Start by eating the smallest black dots
2. As you grow, you can eat larger dots
3. Avoid dots larger than yourself
4. Movement speed decreases as you grow bigger, be cautious
5. Try to beat your high score

## Dependencies

```bash
pip install pygame
```

## How to run

```bash
python main.py
```

## AI Training

This game includes a reinforcement learning framework for training AI agents to play the game.

### Requirements for AI Training

