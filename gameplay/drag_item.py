import pygame
import os
from config import PROJECT_ROOT

class DragItem(pygame.sprite.Sprite):
    def __init__(self, name, pos, robot_id, scale_factor=1.0):
        super().__init__()
        self.name = name
        self.robot_id = robot_id
        
        # Kích thước chuẩn
        self.BASE_SIZE = 130 

        image_path = os.path.join(PROJECT_ROOT, "Images", robot_id, f"{name}.png")
        
        if os.path.exists(image_path):
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                
                # --- LOGIC SCALE (GIỮ NGUYÊN) ---
                orig_w = self.image.get_width()
                orig_h = self.image.get_height()
                fit_scale = self.BASE_SIZE / max(orig_w, orig_h)
                final_scale = fit_scale * scale_factor
                new_w = int(orig_w * final_scale)
                new_h = int(orig_h * final_scale)
                
                self.image = pygame.transform.smoothscale(self.image, (new_w, new_h))
                    
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                self._create_fallback_surface(scale_factor)
        else:
            print(f"Image not found: {image_path}")
            self._create_fallback_surface(scale_factor)

        self.mask = pygame.mask.from_surface(self.image)

        # --- THIẾT LẬP VỊ TRÍ ---
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.start_pos = pos 
        
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def _create_fallback_surface(self, scale_factor):
        size = int(self.BASE_SIZE * scale_factor)
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    # Tính tọa độ chuột so với góc trái trên của ảnh
                    rel_x = event.pos[0] - self.rect.x
                    rel_y = event.pos[1] - self.rect.y
                    
                    # Kiểm tra xem tại vị trí đó trên Mask có phải là "phần thịt" không?
                    if self.mask.get_at((rel_x, rel_y)):
                        self.dragging = True
                        mouse_x, mouse_y = event.pos
                        self.offset_x = self.rect.x - mouse_x
                        self.offset_y = self.rect.y - mouse_y
                        return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset_x
                self.rect.y = mouse_y + self.offset_y
                return True
        return False

    def reset(self):
        self.rect.topleft = self.start_pos
        self.dragging = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)