import colorsys
import pygame
import math
import os

class PlayerBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = 5
        self.score = 0
        self.hue = 0.0
        self.color = (255, 0, 0)  # 添加初始颜色
        
        # 加载并缩放图片，修改缩放系数使角更明显
        image_path = os.path.join("assets", "demon.jpg")
        self.original_image = pygame.image.load(image_path)
        # 使用更大的缩放参数来保持角的可见性
        self.image = pygame.transform.scale(
            self.original_image, 
            (int(self.radius * 2.8), int(self.radius * 2.8))  # 将2改为2.8
        )
        # 使图片保持圆形
        self.image.set_colorkey((0, 0, 0))  # 设置透明色
        self.rect = self.image.get_rect()
        
        # 创建圆形蒙版
        self.mask = self.create_circular_mask()
        
        self.effect_timer = 0
        self.effect_duration = 10  # 效果持续帧数

    def create_circular_mask(self):
        """创建圆形蒙版"""
        mask_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(
            mask_surface,
            (255, 255, 255, 255),
            (int(self.radius), int(self.radius)),
            int(self.radius)
        )
        return mask_surface

    def update(self):
        # 获取键盘输入
        keys = pygame.key.get_pressed()
        new_x = self.x
        new_y = self.y
        
        if keys[pygame.K_LEFT]:
            new_x -= self.speed
        if keys[pygame.K_RIGHT]:
            new_x += self.speed
        if keys[pygame.K_UP]:
            new_y -= self.speed
        if keys[pygame.K_DOWN]:
            new_y += self.speed
            
        # 边界检查
        if new_x - self.radius >= 0 and new_x + self.radius <= 1280:
            self.x = new_x
        if new_y - self.radius >= 0 and new_y + self.radius <= 720:
            self.y = new_y

        # 更新颜色（彩虹效果）
        self.hue = (self.hue + 0.01) % 1.0
        rgb = colorsys.hsv_to_rgb(self.hue, 0.8, 1.0)
        self.color = tuple(int(x * 255) for x in rgb)

    def on_eat_effect(self):
        """被调用时触发吃到食物的视觉效果"""
        self.effect_timer = self.effect_duration

    def draw(self, screen):
        # 图片缩放系数
        image_scale = 2  # 保持原始大小
        mask_scale = 2.8   # 让蒙版和图片一样大
        
        # 计算尺寸
        scaled_size = int(self.radius * image_scale)
        
        # 缩放图片
        self.image = pygame.transform.scale(
            self.original_image,
            (scaled_size, scaled_size)
        )
        
        # 创建新的蒙版，大小和图片一致
        mask_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        pygame.draw.circle(
            mask_surface,
            (255, 255, 255, 255),
            (scaled_size//2, scaled_size//2),
            int(self.radius * mask_scale//2)  # 蒙版圆形大小也相应调整
        )
        
        # 创建临时surface进行混合
        temp_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        temp_surface.blit(self.image, (0, 0))
        temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 居中绘制
        draw_pos = (
            int(self.x - scaled_size//2),
            int(self.y - scaled_size//2)
        )
        screen.blit(temp_surface, draw_pos)
        
        # 添加发光效果（可选）
        glow_color = self.color if hasattr(self, 'color') else (255, 0, 0)  # 添加默认颜色
        glow_radius = int(self.radius * 1.2)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*glow_color[:3], 30),  # 使用当前颜色或默认颜色
            (glow_radius, glow_radius),
            glow_radius
        )
        glow_rect = glow_surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # 如果在效果持续时间内，添加额外的发光效果
        if self.effect_timer > 0:
            effect_radius = int(self.radius * (1.5 + 0.2 * (self.effect_timer / self.effect_duration)))
            effect_surface = pygame.Surface((effect_radius * 2, effect_radius * 2), pygame.SRCALPHA)
            effect_alpha = int(200 * (self.effect_timer / self.effect_duration))
            pygame.draw.circle(
                effect_surface,
                (*self.color[:3], effect_alpha),
                (effect_radius, effect_radius),
                effect_radius
            )
            effect_rect = effect_surface.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(effect_surface, effect_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
            self.effect_timer -= 1

    def eat(self, points):
        # 吃到食物后增加大小
        self.radius += points / 10
        # 随着体积增大，速度略微减少
        self.speed = max(2, 5 - (self.radius - 10) / 20)
        self.score += points
        # 图片和蒙版会在下一次draw时自动调整大小
        self.mask = self.create_circular_mask()

    def check_collision(self, food_x, food_y, food_radius):  # 添加 food_radius 参数
        # 检测与食物的碰撞，并确保只能吃比自己小的点
        distance = math.sqrt((self.x - food_x)**2 + (self.y - food_y)**2)
        return distance < self.radius and self.radius > food_radius  # 添加大小比较

    def get_score(self):
        return self.score

