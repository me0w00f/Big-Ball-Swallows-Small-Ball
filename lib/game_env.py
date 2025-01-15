import random  # 改用这种方式导入
import pygame
import numpy as np
from lib.balls import PlayerBall
from lib.foods import dots, dot_x2, dot_x3, dot_x4, dot_x8, dot_x16

class BallGameEnv:
    def __init__(self, width=1920, height=1080, render_mode="human"):
        self.width = width
        self.height = height
        self.render_mode = render_mode
        
        # 动作空间: 0:不动, 1:上, 2:下, 3:左, 4:右
        self.action_space = 5
        
        # 状态空间: 玩家位置(x,y), 大小, 附近食物信息
        self.observation_space = 69  # 4 + 13*5 (玩家状态 + 13个食物的扩展信息)
        
        if render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((width, height))
        
        self.steps_without_eating = 0  # 添加计数器
        self.background_color = (240, 248, 255)  # 添加淡蓝色背景
        self.grid_color = (230, 240, 250)  # 网格线颜色
        self.grid_size = 40  # 网格大小
        
        self.reset()
    
    def reset(self):
        self.player = PlayerBall(self.width//2, self.height//2)
        self.foods = self._spawn_initial_foods()
        return self._get_state()
    
    def step(self, action):
        # 执行动作前的位置和距离
        old_x = self.player.x
        old_y = self.player.y
        old_distances = [((food.x - old_x)**2 + (food.y - old_y)**2)**0.5 for food in self.foods]
        
        # 执行动作
        if action == 1: self.player.y -= self.player.speed
        elif action == 2: self.player.y += self.player.speed
        elif action == 3: self.player.x -= self.player.speed
        elif action == 4: self.player.x += self.player.speed
        
        # 计算动作后的距离
        new_distances = [((food.x - self.player.x)**2 + (food.y - self.player.y)**2)**0.5 for food in self.foods]
        
        # 基础奖励设置
        reward = 0  # 移除基础惩罚
        
        # 朝向可食用点移动时给予更多奖励
        for i, (old_d, new_d) in enumerate(zip(old_distances, new_distances)):
            if self.player.radius > self.foods[i].radius:  # 只考虑可以吃的点
                if new_d < old_d:  # 距离减少
                    reward += 0.2 * (old_d - new_d) / self.player.speed  # 增加接近奖励
                    if new_d < self.player.radius * 2:  # 非常接近目标
                        reward += 0.5  # 额外接近奖励
        
        # 留在安全区域给予奖励
        safe_zone = self.width * 0.2  # 边缘20%区域被视为危险区
        if (safe_zone < self.player.x < self.width - safe_zone and 
            safe_zone < self.player.y < self.height - safe_zone):
            reward += 0.1  # 安全区域奖励
        
        # 边界惩罚
        edge_margin = 100
        if (self.player.x < edge_margin or 
            self.player.x > self.width - edge_margin or 
            self.player.y < edge_margin or 
            self.player.y > self.height - edge_margin):
            reward -= 2.0  # 增加边界惩罚
        
        # 更新食物位置
        for food in self.foods:
            food.move(self.width, self.height)
        
        # 检查碰撞
        done = False
        self.steps_without_eating += 1
        
        for food in self.foods[:]:
            collision = self.player.check_collision(food.x, food.y, food.radius)
            if collision == -1:  # 游戏结束
                reward = -200  # 增加失败惩罚
                done = True
                break
            elif collision == 1:  # 吃到食物
                base_reward = food.points * 3  # 增加基础得分奖励
                # 额外的进食奖励
                size_ratio = self.player.radius / food.radius
                if size_ratio > 2:  # 吃掉明显更小的点
                    bonus = 1.5
                else:  # 吃掉接近自己大小的点
                    bonus = 2.0
                reward += base_reward * bonus
                self.player.eat(food.points)
                self.foods.remove(food)
                self._spawn_new_food()
                self.steps_without_eating = 0
                # 为玩家添加简单的视觉效果
                if hasattr(self.player, 'on_eat_effect'):  # 检查方法是否存在
                    try:
                        self.player.on_eat_effect()
                    except:
                        pass  # 如果方法调用失败，静默处理
        
        # 惩罚长时间不吃食物
        if self.steps_without_eating > 200:  # 增加容忍步数
            reward -= 0.5
        
        # 生存奖励
        if not done:
            reward += 0.05  # 每步生存奖励
        
        # 检查胜利条件
        if self.player.get_score() >= 2000:
            reward = 2000  # 增加胜利奖励
            done = True
        
        # 渲染
        if self.render_mode == "human":
            self._render()
        
        return self._get_state(), reward, done, {}
    
    def _get_state(self):
        # 增强状态表示
        state = [
            self.player.x / self.width,
            self.player.y / self.height,
            self.player.radius / 100,
            self.steps_without_eating / 1000,  # 添加饥饿度信息
        ]
        
        # 排序食物按距离
        sorted_foods = sorted(
            [(food, ((food.x-self.player.x)**2 + (food.y-self.player.y)**2)**0.5)
             for food in self.foods],
            key=lambda x: x[1]
        )
        
        # 为每个临近食物添加更多信息
        for food, dist in sorted_foods[:13]:
            state.extend([
                food.x / self.width,
                food.y / self.height,
                food.radius / 100,
                dist / ((self.width**2 + self.height**2)**0.5),  # 归一化距离
                1.0 if food.radius < self.player.radius else 0.0  # 是否可食用
            ])
        
        # 填充剩余状态空间
        while len(state) < self.observation_space:
            state.extend([0, 0, 0, 1.0, 0.0])
            
        return np.array(state)
    
    def _spawn_initial_foods(self):
        foods = []
        food_types = [
            (dots, 40),      # 普通点 40个
            (dot_x2, 20),    # 2倍点 20个
            (dot_x3, 10),    # 3倍点 10个
            (dot_x4, 5),     # 4倍点 5个
            (dot_x8, 3),     # 8倍点 3个
            (dot_x16, 1)     # 16倍点 1个
        ]
        
        for food_class, count in food_types:
            for _ in range(count):
                food = food_class()
                food.x = random.randint(0, self.width)
                food.y = random.randint(0, self.height)
                foods.append(food)
        return foods
    
    def _spawn_new_food(self):
        food_class = random.choices(
            [dots, dot_x2, dot_x3, dot_x4, dot_x8, dot_x16],
            weights=[60, 25, 10, 5, 2, 1]
        )[0]
        food = food_class()
        food.x = random.randint(0, self.width)
        food.y = random.randint(0, self.height)
        self.foods.append(food)
        
    def _render(self):
        # 绘制背景
        self.screen.fill(self.background_color)
        
        # 绘制网格
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
        
        # 绘制食物和它们的阴影
        for food in self.foods:
            # 绘制食物阴影
            shadow_offset = 2
            shadow_alpha = 100
            shadow_surface = pygame.Surface((food.radius * 2, food.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                shadow_surface, 
                (*food.color[:3], shadow_alpha),
                (food.radius, food.radius),
                food.radius
            )
            self.screen.blit(
                shadow_surface,
                (int(food.x - food.radius), int(food.y - food.radius + shadow_offset))
            )
            
            # 绘制食物
            pygame.draw.circle(
                self.screen,
                food.color,
                (int(food.x), int(food.y)),
                food.radius
            )
        
        # 绘制玩家（现在使用图片）
        self.player.draw(self.screen)
        
        # 显示游戏信息
        font = pygame.font.Font(None, 36)
        # 分数和大小显示在左上角
        score_text = font.render(f"Score: {self.player.get_score()}", True, (0, 0, 0))
        size_text = font.render(f"Size: {int(self.player.radius)}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(size_text, (10, 50))
        
        # 如果接近胜利，显示进度条
        if self.player.get_score() > 8000:
            progress = (self.player.get_score() / 10000) * 100
            progress_text = font.render(
                f"Victory Progress: {progress:.1f}%", 
                True, 
                (0, 100, 0)
            )
            self.screen.blit(progress_text, (10, 90))
        
        pygame.display.flip()
