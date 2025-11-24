"""   
    @Author: smk
    @Create Time: 2025/11/22 16:41
    @Description: 
"""
# sprites.py
import pygame
import math
from settings import *


class StickmanPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y, color, is_left_side):
        super().__init__()
        self.color = color
        self.is_left_side = is_left_side

        # 身体是一个用于物理碰撞的隐形矩形
        self.rect = pygame.Rect(x, y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

        self.vel_y = 0
        self.speed = PLAYER_SPEED
        self.score = 0
        self.is_jumping = False

        # 挥拍相关
        self.is_swinging = False
        self.swing_timer = 0
        # 击球判定框 (挥拍时才有效)
        self.hitbox = pygame.Rect(0, 0, 60, 60)

    def update(self, keys):
        # 1. 移动逻辑
        if self.is_left_side:
            if keys[pygame.K_a] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH // 2 - 5:  # 不过网
                self.rect.x += self.speed
        else:
            if keys[pygame.K_LEFT] and self.rect.left > SCREEN_WIDTH // 2 + 5:  # 不过网
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
                self.rect.x += self.speed

        # 2. 跳跃逻辑
        if self.is_left_side:
            if keys[pygame.K_w] and not self.is_jumping:
                self.vel_y = JUMP_FORCE
                self.is_jumping = True
        else:
            if keys[pygame.K_UP] and not self.is_jumping:
                self.vel_y = JUMP_FORCE
                self.is_jumping = True

        # 3. 物理应用
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # 地面碰撞
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.is_jumping = False
            self.vel_y = 0

        # 4. 更新挥拍状态
        if self.is_swinging:
            self.swing_timer -= 1
            if self.swing_timer <= 0:
                self.is_swinging = False

        # 更新击球框位置 (在玩家前方)
        hitbox_offset_x = 20 if self.is_left_side else -60
        self.hitbox.topleft = (self.rect.centerx + hitbox_offset_x, self.rect.centery - 40)

    def swing(self):
        if not self.is_swinging:
            self.is_swinging = True
            self.swing_timer = SWING_DURATION

    def draw(self, surface):
        # 绘制火柴人 (相对于 self.rect 的位置)
        cx, cy = self.rect.centerx, self.rect.centery
        foot_y = self.rect.bottom

        # 头部
        head_pos = (cx, foot_y - PLAYER_HEIGHT + 15)
        pygame.draw.circle(surface, self.color, head_pos, 15)
        # 躯干
        neck_pos = (cx, foot_y - PLAYER_HEIGHT + 30)
        hip_pos = (cx, foot_y - 35)
        pygame.draw.line(surface, self.color, neck_pos, hip_pos, 4)
        # 腿
        pygame.draw.line(surface, self.color, hip_pos, (cx - 15, foot_y), 4)  # 左腿
        pygame.draw.line(surface, self.color, hip_pos, (cx + 15, foot_y), 4)  # 右腿

        # 手臂和球拍 (重点：根据挥拍状态改变)
        shoulder_pos = (cx, foot_y - PLAYER_HEIGHT + 45)

        if self.is_left_side:
            hand_pos = (cx + 25, shoulder_pos[1] + 20)
            racket_end = (hand_pos[0] + 30, hand_pos[1] - 30)
            # 挥拍时的动作：手举高向前
            if self.is_swinging:
                hand_pos = (cx + 35, shoulder_pos[1] - 10)
                racket_end = (hand_pos[0] + 40, hand_pos[1] + 10)
        else:  # 右侧玩家
            hand_pos = (cx - 25, shoulder_pos[1] + 20)
            racket_end = (hand_pos[0] - 30, hand_pos[1] - 30)
            # 挥拍时的动作
            if self.is_swinging:
                hand_pos = (cx - 35, shoulder_pos[1] - 10)
                racket_end = (hand_pos[0] - 40, hand_pos[1] + 10)

        # 画后手臂(装饰)
        pygame.draw.line(surface, self.color, shoulder_pos,
                         (cx - 10 if self.is_left_side else cx + 10, shoulder_pos[1] + 30), 4)
        # 画持拍手臂
        pygame.draw.line(surface, self.color, shoulder_pos, hand_pos, 4)

        # 画球拍
        pygame.draw.line(surface, RACKET_COLOR, hand_pos, racket_end, 3)  # 拍杆
        pygame.draw.circle(surface, RACKET_COLOR, racket_end, 15, 2)  # 拍面网

        # (调试用) 画出击球判定框
        # if self.is_swinging:
        #      pygame.draw.rect(surface, (0, 255, 0), self.hitbox, 2)


class Shuttlecock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 用一个较小的矩形作为核心物理碰撞箱
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.vel_x = 0
        self.vel_y = 0
        self.angle = 0  # 用于旋转绘图

    def reset_for_serve(self, server_player):
        # 发球时球跟随玩家手里
        if server_player.is_left_side:
            self.rect.center = (server_player.rect.right + 10, server_player.rect.centery)
        else:
            self.rect.center = (server_player.rect.left - 10, server_player.rect.centery)
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        self.vel_y += GRAVITY

        # 空气阻力 (羽毛球核心特性)
        self.vel_x *= BALL_AIR_RESISTANCE
        self.vel_y *= BALL_AIR_RESISTANCE  # Y轴也加一点阻力，让下落更真实

        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        if self.rect.left <= 0:
            self.rect.left = 0  # 修正位置，防止卡在墙里
            self.vel_x *= -0.8  # 反弹！乘以负数表示方向变反，0.8表示撞墙损耗一点能量
        elif self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel_x *= -0.8


        # 球网碰撞 (简单反弹)
        net_rect = pygame.Rect(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT - NET_HEIGHT, 10, NET_HEIGHT)
        if self.rect.colliderect(net_rect):
            self.vel_x *= -0.8  # 撞网损失能量
            # 防止粘在网上
            if self.rect.centerx < SCREEN_WIDTH // 2:
                self.rect.right = net_rect.left
            else:
                self.rect.left = net_rect.right

        # 计算飞行角度用于绘图
        if abs(self.vel_x) > 1 or abs(self.vel_y) > 1:
            self.angle = math.degrees(math.atan2(-self.vel_y, self.vel_x))

    def draw(self, surface):
        # 手动绘制一个更真实的羽毛球 (圆头 + 羽毛裙)
        # 我们需要根据 self.angle 旋转绘图。这有点复杂，我们用一个简化的方法：
        # 将画布旋转，画好，再转回来。

        # 创建一个临时表面用于旋转
        cock_surf = pygame.Surface((40, 30), pygame.SRCALPHA)

        # 在临时表面上画水平向右的羽毛球
        # 球头
        pygame.draw.circle(cock_surf, WHITE, (30, 15), 8)
        pygame.draw.circle(cock_surf, RACKET_COLOR, (32, 15), 8, 2)  # 球头底座线
        # 羽毛 (用多边形模拟)
        pygame.draw.polygon(cock_surf, WHITE, [(25, 10), (0, 5), (0, 25), (25, 20)])
        pygame.draw.line(cock_surf, RACKET_COLOR, (25, 10), (0, 5), 1)
        pygame.draw.line(cock_surf, RACKET_COLOR, (25, 20), (0, 25), 1)

        # 旋转这个表面
        rotated_surf = pygame.transform.rotate(cock_surf, self.angle)
        rotated_rect = rotated_surf.get_rect(center=self.rect.center)

        surface.blit(rotated_surf, rotated_rect)

        # (调试用) 画物理框
        # pygame.draw.rect(surface, RED, self.rect, 1)