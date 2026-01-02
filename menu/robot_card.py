import pygame

class RobotCard:
    def __init__(self, robot_id, image, center_pos):
        self.robot_id = robot_id

        self.base_width = 220
        self.base_height = 260
        self.base_center = center_pos

        self.scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.15

        self.image = image
        self.image_base_size = self.image.get_size()

        self.hovered = False
        self.selected = False

    def handle_event(self, event):
        if self.selected:
            return None

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.get_rect().collidepoint(event.pos)
            self.target_scale = 1.08 if self.hovered else 1.0

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect().collidepoint(event.pos):
                self.selected = True
                self.target_scale = 1.25
                return self.robot_id

        return None

    def update(self):
        self.scale += (self.target_scale - self.scale) * self.scale_speed

    def get_rect(self):
        w = int(self.base_width * self.scale)
        h = int(self.base_height * self.scale)
        r = pygame.Rect(0, 0, w, h)
        r.center = self.base_center
        return r

    def draw(self, screen, dim=False):
        rect = self.get_rect()

        bg = (230, 245, 255) if self.hovered or self.selected else (190, 210, 230)
        if dim:
            bg = (160, 160, 160)

        pygame.draw.rect(screen, bg, rect, border_radius=18)
        pygame.draw.rect(screen, (120, 150, 190), rect, 3, border_radius=18)

        img_w = int(self.image_base_size[0] * self.scale)
        img_h = int(self.image_base_size[1] * self.scale)
        img = pygame.transform.smoothscale(self.image, (img_w, img_h))
        img_rect = img.get_rect(center=(rect.centerx, rect.centery - 10))

        screen.blit(img, img_rect)