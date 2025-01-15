import pygame
import math
import colorsys

class PlayerBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 5
        self.hue = 0  # 添加色调值用于制作彩虹效果
        self.color = (147, 112, 219)  # 改为紫罗兰色作为初始颜色
        self.score = 0  # 添加分数属性

    def update(self):
        # 获取键盘输入
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
        # 更新颜色（彩虹效果）
        self.hue = (self.hue + 0.01) % 1.0
        rgb = colorsys.hsv_to_rgb(self.hue, 0.8, 1.0)
        self.color = tuple(int(x * 255) for x in rgb)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def eat(self, points):
        # 吃到食物后增加大小
        self.radius += points / 10
        # 随着体积增大，速度略微减少
        self.speed = max(2, 5 - (self.radius - 10) / 20)
        self.score += points  # 更新分数

    def check_collision(self, food_x, food_y, food_radius):
        # 检测与食物的碰撞
        distance = math.sqrt((self.x - food_x)**2 + (self.y - food_y)**2)
        if distance < max(self.radius, food_radius):
            # 如果食物更大，返回 -1 表示游戏结束
            if food_radius >= self.radius:
                return -1
            # 如果食物更小，返回 1 表示可以吃掉
            return 1
        # 没有碰撞返回 0
        return 0

    def get_score(self):
        return self.score

