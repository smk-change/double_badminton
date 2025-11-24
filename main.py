"""   
    @Author: smk
    @Create Time: 2025/11/22 16:40
    @Description: 
"""
import sys
from settings import *
from sprites import StickmanPlayer, Shuttlecock

# --- 初始化 Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
font_score = pygame.font.SysFont("arial", 40, bold=True)
font_msg = pygame.font.SysFont("simhei", 50, bold=True)

# --- 游戏状态枚举 ---
STATE_MENU = "menu"
STATE_SERVING = "serving"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

# --- 全局变量初始化 ---
game_state = STATE_SERVING
current_server = "P1"  # P1 先发球
winner = None

# 创建对象
player1 = StickmanPlayer(SCREEN_WIDTH // 4, FLOOR_Y, RED, True)
player2 = StickmanPlayer(SCREEN_WIDTH * 3 // 4, FLOOR_Y, BLUE, False)
ball = Shuttlecock()


# --- 辅助函数 ---

def reset_game():
    """重置整个游戏状态"""
    global game_state, current_server, winner
    player1.score = 0
    player2.score = 0
    player1.rect.topleft = (SCREEN_WIDTH // 4, FLOOR_Y - PLAYER_HEIGHT)
    player2.rect.topleft = (SCREEN_WIDTH * 3 // 4, FLOOR_Y - PLAYER_HEIGHT)
    current_server = "P1"
    game_state = STATE_SERVING
    winner = None


def handle_hit_collision():
    """处理球拍击球检测 (R3: 只有挥拍才有效)"""
    # P1 击球检测
    if player1.is_swinging and player1.hitbox.colliderect(ball.rect):
        # 简单的击球反馈：根据球的位置给一个向对方场地的速度
        # 如果球在人上方，给高远球；如果球在人前方低处，给平抽
        ball.vel_x = HIT_SPEED_X
        offset_y = (ball.rect.centery - player1.rect.centery) / 5
        ball.vel_y = HIT_SPEED_Y + offset_y
        player1.is_swinging = False  # 击中后立即停止挥拍状态，防止连续判定

    # P2 击球检测
    if player2.is_swinging and player2.hitbox.colliderect(ball.rect):
        ball.vel_x = -HIT_SPEED_X
        offset_y = (ball.rect.centery - player2.rect.centery) / 5
        ball.vel_y = HIT_SPEED_Y + offset_y
        player2.is_swinging = False


def draw_text_center(text, font, color, y_offset=0):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, rect)


# --- 主循环 ---
running = True
while running:
    # =================== 事件处理 ===================
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # R1: 暂停功能
            if event.key == pygame.K_p:
                if game_state == STATE_PLAYING:
                    game_state = STATE_PAUSED
                elif game_state == STATE_PAUSED:
                    game_state = STATE_PLAYING

            # R6: 发球操作
            if game_state == STATE_SERVING:
                if current_server == "P1" and event.key == pygame.K_s:
                    ball.vel_x = SERVE_SPEED_X
                    ball.vel_y = SERVE_SPEED_Y
                    player1.swing()  # 发球也要挥拍
                    game_state = STATE_PLAYING
                elif current_server == "P2" and event.key == pygame.K_DOWN:
                    ball.vel_x = -SERVE_SPEED_X
                    ball.vel_y = SERVE_SPEED_Y
                    player2.swing()
                    game_state = STATE_PLAYING

            # 游戏中挥拍操作
            if game_state == STATE_PLAYING:
                if event.key == pygame.K_s: player1.swing()
                if event.key == pygame.K_DOWN: player2.swing()

            # R7: 游戏结束后重启
            if game_state == STATE_GAME_OVER:
                if event.key == pygame.K_y:
                    reset_game()
                elif event.key == pygame.K_n:
                    running = False

    # =================== 状态更新逻辑 ===================
    if game_state == STATE_PLAYING:
        player1.update(keys)
        player2.update(keys)
        ball.update()
        handle_hit_collision()

        # R2 & R7: 得分判定 (球落地)
        # 羽毛球规则：球落在谁的场地，对方得分。界外球算对方得分。
        # 我们简化判断：只要落地，看在哪边。
        if ball.rect.bottom >= FLOOR_Y:
            ball.rect.bottom = FLOOR_Y  # 防止穿地
            if ball.rect.centerx < SCREEN_WIDTH // 2:
                # 球落在左场，P2得分
                player2.score += 1
                current_server = "P2"  # R6: 得分方发球
            else:
                # 球落在右场，P1得分
                player1.score += 1
                current_server = "P1"

            # R7: 胜利判定
            if player1.score >= WIN_SCORE:
                winner = "P1 (红方)"
                game_state = STATE_GAME_OVER
            elif player2.score >= WIN_SCORE:
                winner = "P2 (蓝方)"
                game_state = STATE_GAME_OVER
            else:
                # 还没赢，进入下一次发球状态
                game_state = STATE_SERVING

    elif game_state == STATE_SERVING:
        # 发球状态下，玩家可以移动调整位置
        player1.update(keys)
        player2.update(keys)
        # 规则：发球方不能超过发球线靠近球网

        # 定义限制区域
        service_line_left_x = SCREEN_WIDTH // 2 - SERVICE_LINE_DIST
        service_line_right_x = SCREEN_WIDTH // 2 + SERVICE_LINE_DIST

        if current_server == "P1":
            # 如果是 P1 发球，他的最右边 (rect.right) 不能超过左侧发球线
            if player1.rect.right > service_line_left_x:
                player1.rect.right = service_line_left_x
        else:
            # 如果是 P2 发球，他的最左边 (rect.left) 不能小于右侧发球线
            if player2.rect.left < service_line_right_x:
                player2.rect.left = service_line_right_x
        # 球跟随发球者
        if current_server == "P1":
            ball.reset_for_serve(player1)
        else:
            ball.reset_for_serve(player2)

    # =================== 绘图渲染 ===================
    screen.fill(SKY_BLUE)  # 天空

    # 画地面
    pygame.draw.rect(screen, GROUND_COLOR, (0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y))
    # 画球网
    pygame.draw.rect(screen, NET_COLOR, (SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT - NET_HEIGHT, 10, NET_HEIGHT))
    # 左侧发球线 (细白线)
    pygame.draw.line(screen, WHITE,
                     (SCREEN_WIDTH // 2 - SERVICE_LINE_DIST, FLOOR_Y),
                     (SCREEN_WIDTH // 2 - SERVICE_LINE_DIST, FLOOR_Y - 20), 3)
    # 右侧发球线
    pygame.draw.line(screen, WHITE,
                     (SCREEN_WIDTH // 2 + SERVICE_LINE_DIST, FLOOR_Y),
                     (SCREEN_WIDTH // 2 + SERVICE_LINE_DIST, FLOOR_Y - 20), 3)
    # 画中线(装饰)
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, FLOOR_Y), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 5)

    # 画所有的精灵
    player1.draw(screen)
    player2.draw(screen)
    ball.draw(screen)

    # 画UI界面 (分数和提示)
    screen.blit(font_score.render(f"P1: {player1.score}", True, RED), (50, 20))
    screen.blit(font_score.render(f"P2: {player2.score}", True, BLUE), (SCREEN_WIDTH - 180, 20))

    # 根据状态画不同的覆盖层信息
    if game_state == STATE_SERVING:
        server_color = RED if current_server == "P1" else BLUE
        key_hint = "S键" if current_server == "P1" else "下键"
        draw_text_center(f"{current_server} 发球 - 按 {key_hint} 发球", font_msg, server_color, -100)

    elif game_state == STATE_PAUSED:
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))  # 半透明黑色遮罩
        screen.blit(s, (0, 0))
        draw_text_center("已暂停 - 按 P 继续", font_msg, WHITE)

    elif game_state == STATE_GAME_OVER:
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        draw_text_center(f"恭喜 {winner} 获胜!", font_msg, WHITE, -50)
        draw_text_center("按 Y 重新开始, 按 N 退出", font_msg, WHITE, 50)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
