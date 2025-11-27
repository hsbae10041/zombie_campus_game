# dialogue.py
import pygame
from fonts import get_font


class DialogueManager:
    def __init__(self, screen):
        self.screen = screen
        self.SCREEN_W, self.SCREEN_H = screen.get_size()

        # 폰트
        self.font = get_font(32)       # 질문 폰트
        self.small_font = get_font(26) # 선택지 폰트

        # 상태
        self.active = False
        self.text = ""         # 화면에 실제로 보여줄 질문 (타이핑 적용)
        self.full_text = ""    # 질문 전체 문자열
        self.building_name = None

        # 타이핑 효과 관련
        self.typing = False
        self.char_index = 0
        self.chars_per_sec = 30   # 초당 글자 수
        self.time_accum = 0.0

        # 색상 / 레이아웃
        self.bg_color = (20, 20, 20)  # 알파는 draw에서 입힘
        self.text_color = (240, 240, 240)
        self.box_h = 210              # 대화창 높이

    # ─────────────────────────────
    # 외부에서 쓰는 인터페이스
    # ─────────────────────────────
    def open_for_building(self, building_name: str):
        """건물 위에 올라갔을 때 대화창 여는 함수"""
        self.active = True
        self.building_name = building_name
        self.full_text = f"{building_name}에 입장하시겠습니까?"
        self.text = ""

        # 타이핑 초기화
        self.typing = True
        self.char_index = 0
        self.time_accum = 0.0

    def handle_key(self, event):
        """
        1 → 'enter', 2 → 'cancel', 그 외 → None
        """
        if event.key == pygame.K_1:
            return "enter"
        elif event.key == pygame.K_2:
            return "cancel"
        return None

    def close(self):
        self.active = False
        self.text = ""
        self.full_text = ""
        self.building_name = None
        self.typing = False
        self.char_index = 0
        self.time_accum = 0.0

    def update(self, dt: float):
        """타이핑 효과 업데이트 (main.py에서 매 프레임마다 호출 필요)"""
        if not self.active or not self.typing:
            return

        self.time_accum += dt
        step = 1.0 / self.chars_per_sec

        # 일정 시간이 지날 때마다 한 글자씩 추가
        while self.time_accum >= step and self.char_index < len(self.full_text):
            self.time_accum -= step
            self.char_index += 1
            self.text = self.full_text[:self.char_index]

        # 다 쳤으면 타이핑 종료
        if self.char_index >= len(self.full_text):
            self.typing = False

    # ─────────────────────────────
    # 텍스트 강제 줄바꿈 함수 (한글 대응, 글자 단위)
    # ─────────────────────────────
    def _wrap_text_chars(self, text: str, font: pygame.font.Font, max_width: int):
        """
        공백 기준이 아니라 '글자 단위'로 줄을 나눔.
        한국어 문장은 띄어쓰기 없어도 자연스럽게 줄바꿈 되도록.
        """
        if text == "":
            return []

        lines = []
        current = ""

        for ch in text:
            test = current + ch
            w, _ = font.size(test)
            if w <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = ch

        if current:
            lines.append(current)

        return lines

    # ─────────────────────────────
    # 그리기
    # ─────────────────────────────
    def draw(self):
        if not self.active:
            return

        screen = self.screen
        box_top = self.SCREEN_H - self.box_h

        # 🔹 반투명 배경 박스
        dialog_surface = pygame.Surface((self.SCREEN_W, self.box_h), pygame.SRCALPHA)
        dialog_surface.fill((*self.bg_color, 190))
        screen.blit(dialog_surface, (0, box_top))

        margin_x = 40
        margin_y = 26
        max_text_width = self.SCREEN_W - margin_x * 2

        # 1) 질문 줄바꿈해서 그리기
        lines = self._wrap_text_chars(self.text, self.font, max_text_width)

        y = box_top + margin_y

        for line in lines:
            surf = self.font.render(line, True, self.text_color)
            screen.blit(surf, (margin_x, y))
            y += self.font.get_height() + 8  # 줄 간격

        # 질문이 전혀 없을 수도 있으니, 마지막 줄 y 기준으로 사용
        last_line_bottom = y

        # 2) 질문 "다음 줄"에 선택지 1번
        choice1_text = "1 : 입장하겠습니다."
        choice1_surf = self.small_font.render(choice1_text, True, (220, 220, 220))
        choice1_y = last_line_bottom + 10
        screen.blit(choice1_surf, (margin_x, choice1_y))

        # 3) 그 아래 줄에 선택지 2번
        choice2_text = "2 : 입장하지 않고 더 살펴보겠습니다."
        choice2_surf = self.small_font.render(choice2_text, True, (220, 220, 220))
        choice2_y = choice1_y + self.small_font.get_height() + 6
        screen.blit(choice2_surf, (margin_x, choice2_y))

