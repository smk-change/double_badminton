"""   
    @Author: smk
    @Create Time: 2025/11/22 16:40
    @Description: 
"""

# settings.py
import pygame

# --- 屏幕设置 ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Python双人火柴人羽毛球"

# --- 颜色定义 (R, G, B) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)  # 玩家1 (左)
BLUE = (50, 50, 220)  # 玩家2 (右)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (118, 85, 43)
NET_COLOR = (50, 50, 50)
RACKET_COLOR = (150, 150, 150)  # 球拍颜色

# --- 游戏物理与参数 ---
GRAVITY = 0.6
PLAYER_SPEED = 7
JUMP_FORCE = -14
BALL_AIR_RESISTANCE = 0.985  # 空气阻力系数 (每帧速度乘以这个数)

# 击球力度
HIT_SPEED_X = 14
HIT_SPEED_Y = -16
SERVE_SPEED_X = 11
SERVE_SPEED_Y = -10

# 游戏规则
WIN_SCORE = 11  # 几分获胜

# 尺寸定义
PLAYER_HEIGHT = 90
PLAYER_WIDTH = 30  # 用于碰撞检测的身体宽度
NET_HEIGHT = 130
FLOOR_Y = SCREEN_HEIGHT - 60

# 挥拍动画时长 (帧数)
SWING_DURATION = 15

# 发球线距离中网的距离 (像素)
SERVICE_LINE_DIST = 160
