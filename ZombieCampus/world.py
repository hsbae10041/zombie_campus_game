# world.py
import pygame

# 건물 좌표 (네가 측정해 준 값 반영)
BUILDINGS = {
    "정의관":     pygame.Rect(295, 398, 46, 61),
    "청송관":     pygame.Rect(395, 301, 66, 40),
    "컨버전스홀": pygame.Rect(505, 409, 90, 51),
    "학생회관":   pygame.Rect(438, 503, 50, 64),
    "도서관":     pygame.Rect(636, 490, 37, 76),
    # 미래관은 두 덩어리 → 하나의 큰 Rect로 합침
    "미래관": pygame.Rect(748, 450, 55, 110),
    "창조관":     pygame.Rect(623, 289, 90, 53),
    "백운관":     pygame.Rect(741, 131, 92, 51),
}


class World:
    def __init__(self, screen, map_path="map.png"):
        self.screen = screen
        self.SCREEN_W, self.SCREEN_H = screen.get_size()

        # 맵 이미지 로드
        self.map_image = pygame.image.load(map_path).convert()
        self.MAP_W, self.MAP_H = self.map_image.get_width(), self.map_image.get_height()

        # 플레이어 (월드 좌표 기준 위치/크기)
        self.player_rect = pygame.Rect(400, 400, 48, 48)
        self.player_speed = 300  # px/s

        # ─────────────────────────────
        #  🔥 플레이어 스프라이트 (서있음/왼/오)
        # ─────────────────────────────
        base_size = (self.player_rect.width, self.player_rect.height)

        self.player_img_stand = pygame.transform.scale(
            pygame.image.load("player_stand.png").convert_alpha(), base_size
        )
        self.player_img_right = pygame.transform.scale(
            pygame.image.load("player_run_right.png").convert_alpha(), base_size
        )
        self.player_img_left = pygame.transform.scale(
            pygame.image.load("player_run_left.png").convert_alpha(), base_size
        )

        self.player_img = self.player_img_stand
        self.last_direction = "right"

        # ─────────────────────────────
        #  🔍 줌 있는 카메라
        # ─────────────────────────────
        self.zoom = 2.5  # 1.0이면 줌 없음, 1.5면 1.5배 확대
        cam_w = int(self.SCREEN_W / self.zoom)
        cam_h = int(self.SCREEN_H / self.zoom)
        self.camera = pygame.Rect(0, 0, cam_w, cam_h)
        self.camera.center = self.player_rect.center

        # ─────────────────────────────
        #  🗺 미니맵 설정
        # ─────────────────────────────
        self.MINIMAP_SCALE = 0.18
        self.minimap_w = int(self.MAP_W * self.MINIMAP_SCALE)
        self.minimap_h = int(self.MAP_H * self.MINIMAP_SCALE)
        self.minimap_x = self.SCREEN_W - self.minimap_w - 20
        self.minimap_y = 20

        self.minimap_surface = pygame.transform.smoothscale(
            self.map_image, (self.minimap_w, self.minimap_h)
        )

    def update(self, dt, allow_move=True):
        """월드 상태 업데이트 (플레이어 이동 + 카메라)"""
        if allow_move:
            self._update_player(dt)
            self._update_camera()

    def _update_player(self, dt):
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # 대각선 보정
        if dx != 0 or dy != 0:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length

        # 스프라이트 방향 결정
        if dx == 0 and dy == 0:
            self.player_img = self.player_img_stand
        else:
            if dx > 0:
                self.player_img = self.player_img_right
                self.last_direction = "right"
            elif dx < 0:
                self.player_img = self.player_img_left
                self.last_direction = "left"
            else:
                # 위/아래만 움직일 때는 마지막 방향 유지
                if self.last_direction == "right":
                    self.player_img = self.player_img_right
                else:
                    self.player_img = self.player_img_left

        # 실제 이동
        self.player_rect.x += dx * self.player_speed * dt
        self.player_rect.y += dy * self.player_speed * dt

        # 맵 경계 제한
        self.player_rect.x = max(0, min(self.player_rect.x, self.MAP_W - self.player_rect.width))
        self.player_rect.y = max(0, min(self.player_rect.y, self.MAP_H - self.player_rect.height))

    def _update_camera(self):
        """카메라를 플레이어 중심으로 이동, 맵 밖으로 안 나가게 조정"""
        self.camera.center = self.player_rect.center

        self.camera.x = max(0, min(self.camera.x, self.MAP_W - self.camera.width))
        self.camera.y = max(0, min(self.camera.y, self.MAP_H - self.camera.height))

    def get_colliding_building(self):
        """플레이어가 어떤 건물 위에 있는지 확인, 없으면 None"""
        for name, rect in BUILDINGS.items():
            if self.player_rect.colliderect(rect):
                return name
        return None

    def draw(self):
        screen = self.screen

        # ─────────────────────────────
        #  메인 화면: 줌된 맵 그리기
        # ─────────────────────────────
        # 카메라가 가리키는 부분을 잘라서
        view = self.map_image.subsurface(self.camera)
        # 화면 크기에 맞게 확대/축소
        view_scaled = pygame.transform.smoothscale(
            view, (self.SCREEN_W, self.SCREEN_H)
        )
        screen.blit(view_scaled, (0, 0))

        # 플레이어 그리기 (카메라 기준 → 줌 반영)
        scale = self.zoom
        px = (self.player_rect.x - self.camera.x) * scale
        py = (self.player_rect.y - self.camera.y) * scale
        pw = int(self.player_rect.width * scale)
        ph = int(self.player_rect.height * scale)

        player_scaled = pygame.transform.smoothscale(self.player_img, (pw, ph))
        screen.blit(player_scaled, (px, py))

        # ─────────────────────────────
        #  미니맵
        # ─────────────────────────────
        # 미니맵 배경
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (self.minimap_x - 5, self.minimap_y - 5, self.minimap_w + 10, self.minimap_h + 10),
        )
        screen.blit(self.minimap_surface, (self.minimap_x, self.minimap_y))

        # 미니맵 위 플레이어 점
        mini_player_x = self.minimap_x + (self.player_rect.x / self.MAP_W) * self.minimap_w
        mini_player_y = self.minimap_y + (self.player_rect.y / self.MAP_H) * self.minimap_h
        pygame.draw.circle(
            screen, (255, 80, 80),
            (int(mini_player_x), int(mini_player_y)), 4
        )

        # 미니맵 위 카메라 시야 박스 (현재 화면이 보고 있는 영역)
        mini_cam_x = self.minimap_x + (self.camera.x / self.MAP_W) * self.minimap_w
        mini_cam_y = self.minimap_y + (self.camera.y / self.MAP_H) * self.minimap_h
        mini_cam_w = (self.camera.width / self.MAP_W) * self.minimap_w
        mini_cam_h = (self.camera.height / self.MAP_H) * self.minimap_h

        pygame.draw.rect(
            screen,
            (0, 230, 255),   # 시안색 박스
            (mini_cam_x, mini_cam_y, mini_cam_w, mini_cam_h),
            2
        )
