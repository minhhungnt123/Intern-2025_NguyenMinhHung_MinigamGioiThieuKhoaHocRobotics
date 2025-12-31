import pygame
import os
from config import PROJECT_ROOT

class DragItem:
    def __init__(self, name, pos, robot_id):
        self.name = name
        self.start_pos = pos
        self.dragging = False
        self.offset = (0, 0)

        img_path = os.path.join(PROJECT_ROOT, "Images", robot_id, f"{name}.png")
        
        if os.path.exists(img_path):
            # 1. Load ảnh gốc
            raw_image = pygame.image.load(img_path).convert_alpha()
            
            # 2. --- THÊM DÒNG NÀY ĐỂ SCALE ẢNH ---
            # Chỉnh kích thước về 100x100 (hoặc kích thước bạn muốn)
            self.image = pygame.transform.smoothscale(raw_image, (200, 200)) 
        else:
            print("❌ Missing part image:", img_path)
            self.image = pygame.Surface((200, 200))
            self.image.fill((255, 0, 0))

        # 3. Tạo rect từ ảnh đã scale
        self.rect = self.image.get_rect(topleft=pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mx, my = event.pos
                self.offset = (self.rect.x - mx, self.rect.y - my)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            self.rect.x = mx + self.offset[0]
            self.rect.y = my + self.offset[1]

    def reset(self):
        self.rect.topleft = self.start_pos

    def draw(self, screen):
        screen.blit(self.image, self.rect)