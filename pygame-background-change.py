import pygame
import random
import os

# Ініціалізація Pygame
pygame.init()

# Налаштування вікна
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Зміна фону при кліку")

# Завантаження зображень
# Припустимо, що у вас є папка 'backgrounds' з фоновими зображеннями
# і файл 'sprite.png' для спрайту
backgrounds = []
for bg_file in os.listdir('backgrounds'):
    if bg_file.endswith('.png'):
        bg_path = os.path.join('backgrounds', bg_file)
        bg = pygame.image.load(bg_path).convert()
        backgrounds.append(bg)

# Завантаження спрайту
sprite = pygame.image.load('sprite.png').convert_alpha()
sprite_rect = sprite.get_rect()
sprite_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

# Початковий фон
current_bg = 0

# Головний цикл гри
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Перевірка кліку миші
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Якщо клік потрапив на спрайт
            if sprite_rect.collidepoint(event.pos):
                # Випадково вибираємо новий фон
                new_bg = random.randint(0, len(backgrounds) - 1)
                # Переконуємось, що новий фон відрізняється від поточного
                while new_bg == current_bg and len(backgrounds) > 1:
                    new_bg = random.randint(0, len(backgrounds) - 1)
                current_bg = new_bg
    
    # Відображення
    screen.blit(backgrounds[current_bg], (0, 0))  # Малюємо фон
    screen.blit(sprite, sprite_rect)  # Малюємо спрайт
    pygame.display.flip()

pygame.quit()
