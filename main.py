import pygame
from lib.balls import PlayerBall
from lib.foods import dots, dot_x2, dot_x3, dot_x4, dot_x8, dot_x16  # 更新导入
import random
from lib.scoreboard import Scoreboard

# 初始化 Pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
VICTORY_SCORE = 10000  # 添加胜利分数阈值

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Big Ball Swallows Small Ball")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_text(screen, text, size, x, y, color=(0, 0, 0)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def show_victory(screen, score, high_scores):
    screen.fill(WHITE)
    draw_text(screen, f"Congratulations! You Won!", 48, WINDOW_WIDTH//4, WINDOW_HEIGHT//3)
    draw_text(screen, f"Final Score: {score}", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT//2)
    draw_text(screen, "Press SPACE to play again", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT*3//4)
    pygame.display.flip()

def show_game_over(screen, score, high_scores):
    screen.fill(WHITE)
    draw_text(screen, f"Game Over! Score: {score}", 48, WINDOW_WIDTH//4, WINDOW_HEIGHT//3)
    draw_text(screen, "High Scores:", 36, WINDOW_WIDTH//4, WINDOW_HEIGHT//2)
    
    for i, high_score in enumerate(high_scores[:5]):
        draw_text(screen, f"{i+1}. {high_score}", 24, WINDOW_WIDTH//4, WINDOW_HEIGHT//2 + 40 + i*30)
    
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
                if player.check_collision(food.x, food.y, food.radius):
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
            screen.fill(WHITE)
            player.draw(screen)
            for food in foods:
                pygame.draw.circle(
                    screen,
                    food.color,
                    (int(food.x), int(food.y)),
                    food.radius
                )
            
            # 显示当前分数
            draw_text(screen, f"Score: {player.get_score()}", 36, 10, 10)
            
            # 在绘制分数后添加胜利检查
            if player.get_score() >= VICTORY_SCORE:
                game_active = False
                scoreboard.save_score(player.get_score())
                show_victory(screen, player.get_score(), scoreboard.get_high_scores())
            
        else:
            # 修改游戏结束显示逻辑
            if player.get_score() >= VICTORY_SCORE:
                show_victory(screen, player.get_score(), scoreboard.get_high_scores())
            else:
                show_game_over(screen, player.get_score(), scoreboard.get_high_scores())
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()