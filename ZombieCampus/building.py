# building.py
import pygame
import random
import sys

from fonts import get_font


def run_building_scene(screen, clock, building_name: str, current_hp: int):
    """
    건물 내부 씬.
    좀비에게 닿으면 HP -20
    HP가 0 이하이면 사망 → 월드로 복귀
    ESC를 누르면 그냥 나가기
    HP를 리턴해서 main.py로 돌려보냄
    """

    WIDTH, HEIGHT = screen.get_size()

    # ─────────────────────────────
    # 플레이어 / 좀비 이미지 로드
    # ─────────────────────────────
    player_size = 100
    zombie_size = 120

    # 방향별 플레이어 이미지 (월드와 맞추기)
    player_img_stand = pygame.transform.scale(
        pygame.image.load("player_stand.png").convert_alpha(),
        (player_size, player_size)
    )
    player_img_right = pygame.transform.scale(
        pygame.image.load("player_run_right.png").convert_alpha(),
        (player_size, player_size)
    )
    player_img_left = pygame.transform.scale(
        pygame.image.load("player_run_left.png").convert_alpha(),
        (player_size, player_size)
    )

    # 기본은 서 있는 상태
    player_img = player_img_stand
    last_dir = "right"  # 위/아래 이동 시 방향 유지용

    zombie_img = pygame.transform.scale(
        pygame.image.load("zombie.png").convert_alpha(),
        (zombie_size, zombie_size)
    )

    # 초기 위치
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player_speed = 5

    zombie_x = random.randint(0, WIDTH - zombie_size)
    zombie_y = random.randint(0, HEIGHT - zombie_size)
    zombie_speed = 2

    start_ticks = pygame.time.get_ticks()

    font = get_font(32)
    big_font = get_font(60)

    # 내부 HP 값
    hp = current_hp

    while True:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # ESC로 나가기
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return hp  # HP 유지한 채 그냥 나가기

        # ─────────────────────────────
        # 이동 & 방향에 따른 이미지 변경
        # ─────────────────────────────
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1

        # 이미지 선택
        if dx == 0 and dy == 0:
            # 멈추면 서 있는 이미지
            player_img = player_img_stand
        else:
            if dx > 0:
                player_img = player_img_right
                last_dir = "right"
            elif dx < 0:
                player_img = player_img_left
                last_dir = "left"
            else:
                # 위/아래만 눌렀을 때는 이전 방향 유지
                if last_dir == "right":
                    player_img = player_img_right
                else:
                    player_img = player_img_left

        # 실제 이동
        player_x += dx * player_speed
        player_y += dy * player_speed

        # 화면 경계
        player_x = max(0, min(player_x, WIDTH - player_size))
        player_y = max(0, min(player_y, HEIGHT - player_size))

        # ─────────────────────────────
        # 좀비 추적
        # ─────────────────────────────
        if zombie_x < player_x:
            zombie_x += zombie_speed
        else:
            zombie_x -= zombie_speed

        if zombie_y < player_y:
            zombie_y += zombie_speed
        else:
            zombie_y -= zombie_speed

        # 🔥 충돌 체크 (HP 20 감소)
        if abs(player_x - zombie_x) < player_size and abs(player_y - zombie_y) < player_size:
            hp -= 20

            # HP가 떨어졌으면 텍스트 표시
            if hp > 0:
                screen.fill((255, 255, 255))
                hit_text = big_font.render("-20", True, (255, 50, 50))
                screen.blit(hit_text, (player_x, player_y - 40))
                pygame.display.update()
                pygame.time.delay(300)

                # 좀비를 랜덤한 위치로 리스폰
                zombie_x = random.randint(0, WIDTH - zombie_size)
                zombie_y = random.randint(0, HEIGHT - zombie_size)
            else:
                # 🔥 체력 0 → 사망
                screen.fill((255, 255, 255))
                dead_text = big_font.render("당신은 좀비에게 잡혀 사망했습니다!", True, (200, 0, 0))
                screen.blit(dead_text, (WIDTH // 2 - 300, HEIGHT // 2 - 30))
                pygame.display.update()
                pygame.time.delay(1500)
                return 0

        # ─────────────────────────────
        # 그리기
        # ─────────────────────────────
        screen.fill((255, 255, 255))

        # 생존 시간 표시
        elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000
        title_text = font.render(
            f"{building_name} - 생존 {elapsed_time}s", True, (0, 0, 0)
        )
        screen.blit(title_text, (10, 10))

        # 🔥 HP UI 표시
        hp_bar_width = 200
        hp_ratio = hp / 100
        hp_fill = int(hp_bar_width * hp_ratio)

        pygame.draw.rect(screen, (180, 0, 0), (10, 50, hp_bar_width, 20))  # 바탕
        pygame.draw.rect(screen, (255, 80, 80), (10, 50, hp_fill, 20))    # 남은 HP

        hp_text = font.render(f"HP: {hp}", True, (0, 0, 0))
        screen.blit(hp_text, (220, 45))

        # 플레이어/좀비 이미지
        screen.blit(player_img, (player_x, player_y))
        screen.blit(zombie_img, (zombie_x, zombie_y))

        # ESC 안내 텍스트
        esc_text = font.render("ESC: 건물에서 나가기", True, (50, 50, 50))
        screen.blit(esc_text, (10, HEIGHT - 40))

        pygame.display.update()
