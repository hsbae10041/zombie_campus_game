# main.py
import pygame
import sys

from world import World
from dialogue import DialogueManager
from building import run_building_scene
from fonts import get_font
from intro_typing import IntroTypingManager

pygame.init()


def main():
    SCREEN_W, SCREEN_H = 1200, 800
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Zombie Escape Campus")
    clock = pygame.time.Clock()

    # 🔹 인트로 문장들 (줄바꿈 포함)
    intro_lines = [
        "좀비에 감염된 연세대학교에 입장하시겠습니까?",
        "주의: 신중히 생각하세요.\n한 번 입장하시면 탈출키를 찾아 탈출구로 나가기 전까지 게임을 종료하실 수 없습니다.\n좀비들을 피해 아이템을 획득하고 탈출키를 찾아 살아 나오시길 바라겠습니다.",
        "행운을 빕니다. GOOD LUCK",
    ]
    intro = IntroTypingManager(screen, intro_lines)

    show_intro = True

    # 🔹 인트로 딜레이 (배경만 먼저 보여주는 시간)
    intro_delay_done = False
    intro_delay_timer = 0
    intro_delay_duration = 1.2   # 1.2초 동안 intro.png만 표시

    # 🔹 인트로 배경 이미지
    intro_img = pygame.image.load("intro.png").convert()
    intro_bg = pygame.transform.scale(intro_img, (SCREEN_W, SCREEN_H))

    # ---- 월드/대화 ----
    world = World(screen, "map.png")
    dialogue = DialogueManager(screen)

    last_cancelled_building = None
    player_hp = 100

    hp_font = get_font(26)

    # 🔧 좌표 측정 모드 (M키로 ON/OFF)
    measure_mode = False
    measure_points = []

    # =============================
    # 메인 루프
    # =============================
    while True:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ================================
            # 인트로 입력 처리 (ENTER로 월드 진입)
            # ================================
            if show_intro:
                if intro_delay_done:
                    if event.type == pygame.KEYDOWN and intro.finished:
                        if event.key == pygame.K_RETURN:
                            show_intro = False
                continue

            # ================================
            # 월드 대화창 입력 처리
            # ================================
            if dialogue.active and event.type == pygame.KEYDOWN:
                result = dialogue.handle_key(event)
                if result == "enter":
                    pygame.time.delay(200)
                    building_name = dialogue.building_name
                    dialogue.close()
                    player_hp = run_building_scene(screen, clock, building_name, player_hp)
                    last_cancelled_building = None
                elif result == "cancel":
                    pygame.time.delay(200)
                    last_cancelled_building = dialogue.building_name
                    dialogue.close()

            # =========================================================
            # 🔧 좌표 측정 모드 토글 (M키)
            # =========================================================
            if event.type == pygame.KEYDOWN and not show_intro:
                if event.key == pygame.K_m:
                    measure_mode = not measure_mode
                    measure_points = []
                    print("\n=== 좌표 측정 모드: {} ===".format("ON" if measure_mode else "OFF"))
                    if measure_mode:
                        print("파란 건물의 '왼쪽 위'를 마우스로 클릭하세요.")
                    continue

            # =========================================================
            # 🔧 좌표 측정 모드일 때 마우스 클릭 → 건물 Rect 자동 계산
            # =========================================================
            if measure_mode and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # 화면 좌표 → 월드 좌표로 변환
                world_x = mx + world.camera.x
                world_y = my + world.camera.y
                measure_points.append((world_x, world_y))
                print("찍은 점:", (world_x, world_y))

                if len(measure_points) == 1:
                    print("이제 같은 건물의 '오른쪽 아래'를 클릭하세요.")
                elif len(measure_points) == 2:
                    (x1, y1), (x2, y2) = measure_points
                    left = min(x1, x2)
                    top = min(y1, y2)
                    width = abs(x2 - x1)
                    height = abs(y2 - y1)

                    print("\n🎉 완성된 Rect:")
                    print(f"pygame.Rect({left}, {top}, {width}, {height})")

                    measure_mode = False
                    measure_points = []
                    print("좌표 측정 모드 OFF\n")

        # ======================================
        # 1) 인트로 화면 처리
        # ======================================
        if show_intro:

            # 1단계: intro.png만 출력되는 구간
            if not intro_delay_done:
                intro_delay_timer += dt

                # 배경 이미지
                screen.blit(intro_bg, (0, 0))

                # 어두운 오버레이
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 90))
                screen.blit(overlay, (0, 0))

                # 시간이 지나면 타이핑 시작 단계로 이동
                if intro_delay_timer >= intro_delay_duration:
                    intro_delay_done = True

                pygame.display.flip()
                continue

            # 2단계: 타이핑 시작
            screen.blit(intro_bg, (0, 0))

            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            screen.blit(overlay, (0, 0))

            intro.update(dt)
            intro.draw()

            pygame.display.flip()
            continue

        # ==================================================================
        # 2) 실제 게임(월드 화면)
        # ==================================================================
        dialogue.update(dt)
        world.update(dt, allow_move=not dialogue.active)

        if not dialogue.active:
            hit = world.get_colliding_building()
            if hit is None:
                last_cancelled_building = None
            else:
                if hit != last_cancelled_building:
                    dialogue.open_for_building(hit)

        world.draw()

        # HP UI
        hp_bar_width = 200
        hp_ratio = max(0, player_hp / 100)
        hp_fill = int(hp_bar_width * hp_ratio)

        pygame.draw.rect(screen, (100, 0, 0), (20, 20, hp_bar_width, 20))
        pygame.draw.rect(screen, (255, 80, 80), (20, 20, hp_fill, 20))

        hp_label = hp_font.render(f"HP: {player_hp}", True, (255, 255, 255))
        screen.blit(hp_label, (20, 45))

        if dialogue.active:
            dialogue.draw()

        pygame.display.flip()


if __name__ == "__main__":
    main()
