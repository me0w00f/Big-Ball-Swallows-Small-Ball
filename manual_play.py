import pygame
from lib.balls import PlayerBall
from lib.foods import dots, dot_x2, dot_x3, dot_x4, dot_x8, dot_x16
import random
from lib.scoreboard import Scoreboard

# 初始化 Pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
VICTORY_SCORE = 5000

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Big Ball Swallows Small Ball")

# 颜色定义
BACKGROUND_COLOR = (240, 248, 255)  # 淡蓝色背景
GRID_COLOR = (230, 240, 250)  # 网格线颜色
GRID_SIZE = 40  # 网格大小

def draw_grid():
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

def draw_text(screen, text, size, x, y, color=(0, 0, 0)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def show_victory(screen, score, high_scores):
    screen.fill(BACKGROUND_COLOR)
    draw_text(screen, "👑 Congratulations! You Won! 👑", 48, WINDOW_WIDTH//4, WINDOW_HEIGHT//3)
    draw_text(screen, f"Final Score: {score}", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT//2)
    draw_text(screen, "Press SPACE to play again", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT*3//4)
    pygame.display.flip()

def show_game_over(screen, score, high_scores):
    screen.fill(BACKGROUND_COLOR)
    draw_text(screen, "💀 Game Over! 💀", 48, WINDOW_WIDTH//4, WINDOW_HEIGHT//3)
    draw_text(screen, f"Score: {score}", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT//2-30)
    draw_text(screen, "High Scores:", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT//2+30)
    
    for i, high_score in enumerate(high_scores[:5]):
        draw_text(screen, f"{i+1}. {high_score}", 24, WINDOW_WIDTH//4, WINDOW_HEIGHT//2 + 70 + i*30)
    
    draw_text(screen, "Press SPACE to play again", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT*3//4)
    pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    player = PlayerBall(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
    foods = []
    scoreboard = Scoreboard()
    game_active = True
    
    # 更新食物类型和数量
    food_types = [
        (dots, 40),      # 普通点 40个
        (dot_x2, 20),    # 2倍点 20个
        (dot_x3, 10),    # 3倍点 10个
        (dot_x4, 5),     # 4倍点 5个
        (dot_x8, 3),     # 8倍点 3个
        (dot_x16, 1)     # 16倍点 1个
    ]
    
    # 修改食物存储方式，增加位置信息
    foods = []
    for food_class, count in food_types:
        for _ in range(count):
            food = food_class()
            food.x = random.randint(0, WINDOW_WIDTH)  # 存储位置到食物对象中
            food.y = random.randint(0, WINDOW_HEIGHT)
            foods.append(food)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and not game_active:
                if event.key == pygame.K_SPACE:
                    # 重置游戏
                    player = PlayerBall(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
                    foods = []
                    game_active = True
                    # 重新生成食物
                    for food_class, count in food_types:
                        for _ in range(count):
                            food = food_class()
                            food.x = random.randint(0, WINDOW_WIDTH)
                            food.y = random.randint(0, WINDOW_HEIGHT)
                            foods.append(food)

        if game_active:
            # 更新玩家位置
            player.update()
            
            # 更新所有食物的位置
            for food in foods:
                food.move(WINDOW_WIDTH, WINDOW_HEIGHT)
            
            # 检测碰撞和进食
            for food in foods[:]:
                collision = player.check_collision(food.x, food.y, food.radius)
                if collision == -1:  # 碰到更大的点，游戏结束
                    game_active = False
                    scoreboard.save_score(player.get_score())
                    break
                elif collision == 1:  # 可以吃掉这个点
                    player.eat(food.get_points())
                    foods.remove(food)
                    # 添加新食物
                    food_class = random.choices(
                        [dots, dot_x2, dot_x3, dot_x4, dot_x8, dot_x16],
                        weights=[60, 25, 10, 5, 2, 1]
                    )[0]
                    new_food = food_class()
                    new_food.x = random.randint(0, WINDOW_WIDTH)
                    new_food.y = random.randint(0, WINDOW_HEIGHT)
                    foods.append(new_food)

            # 绘制
            screen.fill(BACKGROUND_COLOR)
            draw_grid()
            
            # 绘制食物和它们的阴影
            for food in foods:
                # 绘制阴影
                shadow_surface = pygame.Surface((food.radius * 2, food.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(shadow_surface, (*food.color[:3], 100), 
                                (food.radius, food.radius), food.radius)
                screen.blit(shadow_surface, 
                           (int(food.x - food.radius), int(food.y - food.radius + 2)))
                
                # 绘制食物
                pygame.draw.circle(screen, food.color, 
                                (int(food.x), int(food.y)), food.radius)
            
            # 绘制玩家
            player.draw(screen)
            
            # 显示信息
            draw_text(screen, f"Score: {player.get_score()}", 36, 10, 10)
            draw_text(screen, f"Size: {int(player.radius)}", 36, 10, 50)
            
            # 如果分数接近胜利条件，显示进度
            if player.get_score() > 3000:
                progress = (player.get_score() / 5000) * 100
                draw_text(screen, f"Victory Progress: {progress:.1f}%", 36, 10, 90, (0, 100, 0))
            
            # 胜利检查
            if player.get_score() >= VICTORY_SCORE:
                game_active = False
                scoreboard.save_score(player.get_score())
                show_victory(screen, player.get_score(), scoreboard.get_high_scores())
        else:
            if player.get_score() >= VICTORY_SCORE:
                show_victory(screen, player.get_score(), scoreboard.get_high_scores())
            else:
                show_game_over(screen, player.get_score(), scoreboard.get_high_scores())
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()