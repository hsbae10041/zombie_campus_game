# intro_typing.py
import pygame
from fonts import get_font


class IntroTypingManager:
    def __init__(self, screen, lines):
        self.screen = screen
        self.SCREEN_W, self.SCREEN_H = screen.get_size()

        # 폰트
        self.font_main = get_font(32)      # 첫 줄 & 마지막 줄
        self.font_warning = get_font(26)   # '주의' 문장 전용
        self.small_font = get_font(24)     # ENTER 안내

        # 문장 리스트
        self.lines = lines
        self.current_line = 0
        self.display_text = ""
        self.full_text = lines[0]

        # 타이핑 속도 (느리게)
        self.char_index = 0
        self.chars_per_sec = 12  # 기본 35 → 18
        self.time_accum = 0.0

        self.finished = False

    # -------------------------------------------------------
    # 줄바꿈(\n) 처리 + 자동 줄바꿈 처리
    # -------------------------------------------------------
    def _wrap_text_chars(self, text: str, font: pygame.font.Font, max_width: int):
        # 강제 줄바꿈 (\n)
        if "\n" in text:
            lines = []
            for raw in text.split("\n"):
                wrapped = self._wrap_text_chars(raw, font, max_width)
                lines.extend(wrapped)
            return lines

        if text == "":
            return []

        current = ""
        lines = []

        for ch in text:
            test = current + ch
            w, _ = font.size(test)
            if w <= max_width:
                current = test
            else:
                lines.append(current)
                current = ch

        if current:
            lines.append(current)

        return lines

    # -------------------------------------------------------
    # 타이핑 업데이트
    # -------------------------------------------------------
    def update(self, dt):
        if self.finished:
            return

        self.time_accum += dt
        step = 1.0 / self.chars_per_sec

        while self.time_accum >= step and self.char_index < len(self.full_text):
            self.time_accum -= step
            self.char_index += 1
            self.display_text = self.full_text[:self.char_index]

        if self.char_index >= len(self.full_text):
            if self.current_line == len(self.lines) - 1:
                self.finished = True
                return

            self.current_line += 1
            self.full_text = self.lines[self.current_line]
            self.display_text = ""
            self.char_index = 0

    # -------------------------------------------------------
    # 화면 렌더링
    # -------------------------------------------------------
    def draw(self):
        screen = self.screen

        max_width = int(self.SCREEN_W * 0.75)
        render_lines = []

        # 이미 끝난 문장들
        for idx in range(self.current_line):
            base = self.lines[idx]
            if idx == 1:
                font = self.font_warning
                color = (255, 230, 190)
            else:
                font = self.font_main
                color = (255, 255, 255)

            wrapped = self._wrap_text_chars(base, font, max_width)
            for s in wrapped:
                render_lines.append((s, font, color))

        # 현재 타이핑 중인 문장
        cur = self.current_line
        if cur < len(self.lines):
            if cur == 1:
                font = self.font_warning
                color = (255, 230, 190)
            else:
                font = self.font_main
                color = (255, 255, 255)

            wrapped = self._wrap_text_chars(self.display_text, font, max_width)
            for s in wrapped:
                render_lines.append((s, font, color))

        if not render_lines:
            return

        # 전체 높이 계산
        total_h = sum(font.get_height() + 10 for (_, font, _) in render_lines)

        # 🔹 위치: 화면 중앙보다 위쪽
        box_center_y = int(self.SCREEN_H * 0.30)  # 0.35 → 0.30 더 위
        start_y = box_center_y - total_h // 2

        box_w = max_width + 40
        box_h = total_h + 40
        box_x = (self.SCREEN_W - box_w) // 2
        box_y = start_y - 20

        # 반투명 박스
        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        screen.blit(bg, (box_x, box_y))

        # 텍스트 렌더링
        x = box_x + 20
        y = start_y

        for text, font, color in render_lines:
            surf = font.render(text, True, color)
            screen.blit(surf, (x, y))
            y += font.get_height() + 10

        # ENTER 안내
        if self.finished:
            hint = self.small_font.render("ENTER를 눌러 게임을 시작합니다.", True, (255, 255, 180))
            hint_rect = hint.get_rect(center=(self.SCREEN_W // 2, self.SCREEN_H - 80))

            bg_w = hint_rect.width + 40
            bg_h = hint_rect.height + 20
            hint_bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
            hint_bg.fill((0, 0, 0, 160))

            screen.blit(hint_bg, (hint_rect.centerx - bg_w // 2,
                                  hint_rect.centery - bg_h // 2))
            screen.blit(hint, hint_rect)
