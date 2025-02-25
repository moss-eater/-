import pygame
import random
import os
import time
pygame.init()

BLACH = (0, 0, 0)
WIDTH = 800
HEIGHT = 600
show_attacker = False

font1 = pygame.font.SysFont(None, 25)

clock = pygame.time.Clock()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dung Crawl")

# Завантаження зображень
# Припустимо, що у вас є папка 'backgrounds' з фоновими зображеннями
# і файл 'sprite.png' для спрайту
backgrounds = []
for bg_file in os.listdir('backgrounds'):
    if bg_file.endswith('.png'):
        bg_path = os.path.join('backgrounds', bg_file)
        bg = pygame.image.load(bg_path).convert()
        backgrounds.append(bg)

sprite = pygame.image.load('sprite.png').convert_alpha()
sprite_rect = sprite.get_rect()
sprite_rect.center = (0, 0)

current_bg = 0

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, xar, ys, w, h):
        super().__init__()
        self.h = h
        self.w = w
        self.image = pygame.transform.scale(pygame.image.load(image), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = xar
        self.rect.y = ys
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Palehin(GameSprite):
    def __init__(self, image, xar, ys, w, h, palehin_ht, palehin_ar, palehin_ak):
        super().__init__(image, xar, ys, w, h)
        self.palehin_hp = palehin_ht
        self.palehin_arm = palehin_ar
        self.palehin_ak = palehin_ak

    def attak(self, enemy):
        attacker = GameSprite("sprite.png", self.rect.x, self.rect.centery, 50, 50)
        global show_attacker
        show_attacker = True
        if show_attacker == True:
            attacker.reset()
            time.sleep(1)
            show_attacker = False
        enemy.palehin_ar -= self.palehin_ak
        if enemy.palehin_ar < 0:
            enemy.palehin_ht += enemy.palehin_ar
            enemy.palehin_ar = 0

palehin = Palehin("palehin.png", 200, 400, 50, 50, 20, 5, 10)

running = True
finish = False
while running:

    while finish:
        palehin.reset()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if sprite_rect.collidepoint(event.pos):
                new_bg = random.randint(0, len(backgrounds) - 1)
                while new_bg == current_bg and len(backgrounds) > 1:
                    new_bg = random.randint(0, len(backgrounds) - 1)
                current_bg = new_bg    

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                palehin.attak() == True

    

    window.blit(backgrounds[current_bg], (0, 0))
    window.blit(sprite, sprite_rect)
    pygame.display.flip()

pygame.quit()
