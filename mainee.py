import pygame
pygame.init()
import os
import random

BLACH = (0, 0, 0)
WIDTH = 800
HEIGHT = 600

font1 = pygame.font.SysFont(None, 25)

clock = pygame.time.Clock()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dung Crawl")

backgrounds = []
for bg_file in os.listdir('backgrounds'):
    if bg_file.endswith('.png'):
        bg_path = os.path.join('backgrounds', bg_file)
        bg = pygame.image.load(bg_path).convert()
        backgrounds.append(bg)
sprite = pygame.image.load('sprite.png').convert_alpha()
sprite_rect = sprite.get_rect()
current_bg = 0



game = True
finish = False
while game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if sprite_rect.collidepoint(event.pos):
                new_bg = random.randint(0, len(backgrounds) - 1)
                while new_bg == current_bg and len(backgrounds) > 1:
                    new_bg = random.randint(0, len(backgrounds) - 1)
                current_bg = new_bg

    if finish != True:
        window.fill(BLACH)