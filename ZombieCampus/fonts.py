# fonts.py
import pygame
import os

# 이 파일(fonts.py)와 같은 폴더에 있는 gamefont.ttf 사용
FONT_PATH = os.path.join(os.path.dirname(__file__), "gamefont.ttf")

def get_font(size: int) -> pygame.font.Font:
    """지정한 size의 공통 폰트 객체를 반환"""
    return pygame.font.Font(FONT_PATH, size)
