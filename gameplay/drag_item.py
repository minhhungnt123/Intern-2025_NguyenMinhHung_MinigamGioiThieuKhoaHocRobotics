import pygame
import os
from config import PROJECT_ROOT


# ==============================
# DRAG MANAGER (GLOBAL)
# ==============================
class DragManager:
    """
    Quản lý object đang được drag (singleton logic)
    """
    active_item = None

    @classmethod
    def lock(cls, item):
        cls.active_item = item

    @classmethod
    def release(cls, item):
        if cls.active_item == item:
            cls.active_item = None

    @classmethod
    def is_locked(cls):
        return cls.active_item is not None


# ==============================
# DRAG ITEM
# ==============================
class DragItem:
    def __init__(self, name, pos, robot_id, scale=(200, 200)):
        self.name = name
        self.start_pos = pos
        self.dragging = False
        self.offset = (0, 0)

        # ---- Load Image ----
        img_path = os.path.join(PROJECT_ROOT, "Images", robot_id, f"{name}.png")
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"❌ Missing part image: {img_path}")

        raw_image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.smoothscale(raw_image, scale)

        # ---- Rect & Mask (Pixel Perfect) ----
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos
        self.mask = pygame.mask.from_surface(self.image)

    # ==========================
    # EVENT HANDLING
    # ==========================
    def handle_event(self, event):
        # ----------------------
        # MOUSE DOWN
        # ----------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if DragManager.is_locked():
                return

            if self._pixel_hit(event.pos):
                self.dragging = True
                DragManager.lock(self)

                mx, my = event.pos
                self.offset = (self.rect.x - mx, self.rect.y - my)

        # ----------------------
        # MOUSE UP
        # ----------------------
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                DragManager.release(self)

        # ----------------------
        # MOUSE MOVE
        # ----------------------
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            self.rect.x = mx + self.offset[0]
            self.rect.y = my + self.offset[1]

    # ==========================
    # PIXEL PERFECT CHECK
    # ==========================
    def _pixel_hit(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos):
            return False

        local_x = mouse_pos[0] - self.rect.x
        local_y = mouse_pos[1] - self.rect.y

        if 0 <= local_x < self.mask.get_size()[0] and 0 <= local_y < self.mask.get_size()[1]:
            return self.mask.get_at((local_x, local_y))

        return False

    # ==========================
    # HELPERS
    # ==========================
    def reset(self):
        self.rect.topleft = self.start_pos

    def draw(self, screen):
        screen.blit(self.image, self.rect)
