import random
import math

class dots:

    def __init__(self):
        self.food = "dots"
        self.points = 10
        self.radius = 3
        self.color = (0, 0, 0)  # 黑色
        self.speed = random.uniform(1, 3)  # 随机速度
        self.direction = random.uniform(0, 2 * 3.14159)  # 随机方向（弧度）
        self.dx = self.speed * math.cos(self.direction)
        self.dy = self.speed * math.sin(self.direction)

    def get_food(self):
        return self.food

    def get_points(self):
        return self.points

    def move(self, width, height):
        """移动点并在碰到边界时反弹"""
        self.x += self.dx
        self.y += self.dy
        
        # 边界检查和反弹
        if self.x <= self.radius or self.x >= width - self.radius:
            self.dx *= -1
        if self.y <= self.radius or self.y >= height - self.radius:
            self.dy *= -1

        return self.x, self.y

class dot_x2(dots):
    
    def __init__(self):
        super().__init__()  # 添加父类初始化调用
        self.food = "dot_x2"
        self.points = 20
        self.radius = 5
        self.color = (0, 255, 0)  # 绿色
        # 较大的点移动速度应该更慢
        self.speed = random.uniform(0.8, 2.0)
        self.direction = random.uniform(0, 2 * 3.14159)
        self.dx = self.speed * math.cos(self.direction)
        self.dy = self.speed * math.sin(self.direction)

class dot_x3(dots):
    def __init__(self):
        super().__init__()
        self.food = "dot_x3"
        self.points = 30
        self.radius = 7
        self.color = (0, 0, 255)
        self.speed = random.uniform(0.6, 1.8)
        self.direction = random.uniform(0, 2 * 3.14159)
        self.dx = self.speed * math.cos(self.direction)
        self.dy = self.speed * math.sin(self.direction)

class dot_x4(dots):
    def __init__(self):
        super().__init__()
        self.food = "dot_x4"
        self.points = 40
        self.radius = 9
        self.color = (255, 0, 255)
        self.speed = random.uniform(0.5, 1.5)
        self.direction = random.uniform(0, 2 * 3.14159)
        self.dx = self.speed * math.cos(self.direction)
        self.dy = self.speed * math.sin(self.direction)

class dot_x8(dots):
    def __init__(self):
        super().__init__()
        self.food = "dot_x8"
        self.points = 80
        self.radius = 12
        self.color = (255, 165, 0)
        self.speed = random.uniform(0.3, 1.2)
        self.direction = random.uniform(0, 2 * 3.14159)
        self.dx = self.speed * math.cos(self.direction)
        self.dy = self.speed * math.sin(self.direction)

class dot_x16(dots):
    def __init__(self):
        super().__init__()
        self.food = "dot_x16"
        self.points = 160
        self.radius = 15
        self.color = (255, 0, 0)
        self.speed = random.uniform(0.2, 1.0)
        self.direction = random.uniform(0, 2 * 3.14159)
        self.dx = self.speed * math.cos(self.direction)
        self.dy = self.speed * math.sin(self.direction)

