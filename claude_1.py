import sys
import pygame
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Головний клас гри (PyGame)
class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Пригодницька гра")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('Arial', 20)
        
        # Локації
        self.locations = {
            'forest': {
                'background': (34, 139, 34),
                'name': 'Ліс',
                'exits': {'east': 'village', 'south': 'river'},
                'items': ['stick', 'berry'],
                'sprites': [
                    {'name': 'tree1', 'rect': pygame.Rect(100, 100, 80, 150), 'color': (50, 120, 50)},
                    {'name': 'tree2', 'rect': pygame.Rect(300, 200, 80, 150), 'color': (50, 120, 50)},
                    {'name': 'berry_bush', 'rect': pygame.Rect(500, 300, 60, 60), 'color': (150, 0, 0)},
                ]
            },
            'village': {
                'background': (210, 180, 140),
                'name': 'Село',
                'exits': {'west': 'forest', 'south': 'cave'},
                'items': ['key'],
                'sprites': [
                    {'name': 'house1', 'rect': pygame.Rect(200, 150, 120, 100), 'color': (139, 69, 19)},
                    {'name': 'house2', 'rect': pygame.Rect(400, 200, 120, 100), 'color': (139, 69, 19)},
                    {'name': 'well', 'rect': pygame.Rect(300, 350, 50, 50), 'color': (105, 105, 105)},
                ]
            },
            'river': {
                'background': (65, 105, 225),
                'name': 'Річка',
                'exits': {'north': 'forest', 'east': 'cave'},
                'items': ['fish'],
                'sprites': [
                    {'name': 'rock1', 'rect': pygame.Rect(150, 200, 70, 50), 'color': (128, 128, 128)},
                    {'name': 'rock2', 'rect': pygame.Rect(400, 250, 70, 50), 'color': (128, 128, 128)},
                    {'name': 'fish_spot', 'rect': pygame.Rect(270, 300, 40, 20), 'color': (0, 191, 255)},
                ]
            },
            'cave': {
                'background': (47, 79, 79),
                'name': 'Печера',
                'exits': {'north': 'village', 'west': 'river'},
                'items': ['treasure'],
                'sprites': [
                    {'name': 'stalagmite1', 'rect': pygame.Rect(150, 150, 40, 80), 'color': (169, 169, 169)},
                    {'name': 'stalagmite2', 'rect': pygame.Rect(350, 200, 40, 80), 'color': (169, 169, 169)},
                    {'name': 'treasure_chest', 'rect': pygame.Rect(550, 350, 70, 50), 'color': (255, 215, 0)},
                ]
            }
        }
        
        # Предмети та їх властивості
        self.items_info = {
            'stick': {'name': 'Палиця', 'desc': 'Звичайна дерев\'яна палиця', 'usable_on': ['berry_bush']},
            'berry': {'name': 'Ягоди', 'desc': 'Смачні лісові ягоди', 'usable_on': []},
            'key': {'name': 'Ключ', 'desc': 'Старий іржавий ключ', 'usable_on': ['treasure_chest']},
            'fish': {'name': 'Риба', 'desc': 'Свіжа риба', 'usable_on': []},
            'treasure': {'name': 'Скарб', 'desc': 'Старовинні монети', 'usable_on': []}
        }
        
        # Стан гри
        self.current_location = 'forest'
        self.inventory = []
        self.selected_item = None
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        return
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Переміщення між локаціями за допомогою клавіш
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.move_location('north')
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.move_location('south')
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.move_location('west')
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.move_location('east')
                # Перемикання між предметами в інвентарі
                elif event.key == pygame.K_1 and len(self.inventory) >= 1:
                    self.selected_item = 0
                elif event.key == pygame.K_2 and len(self.inventory) >= 2:
                    self.selected_item = 1
                elif event.key == pygame.K_3 and len(self.inventory) >= 3:
                    self.selected_item = 2
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Перевірка кліків по спрайтах
                mouse_pos = pygame.mouse.get_pos()
                self.check_sprite_click(mouse_pos)
    
    def move_location(self, direction):
        location = self.locations[self.current_location]
        if direction in location['exits']:
            self.current_location = location['exits'][direction]
    
    def check_sprite_click(self, mouse_pos):
        location = self.locations[self.current_location]
        
        # Перевірка кліків по спрайтах
        for sprite in location['sprites']:
            if sprite['rect'].collidepoint(mouse_pos):
                # Якщо це предмет для збору
                if sprite['name'] == 'berry_bush' and 'berry' in location['items']:
                    if self.selected_item is not None and self.inventory[self.selected_item] == 'stick':
                        self.collect_item('berry')
                        print(f"Ви зібрали ягоди за допомогою палиці!")
                    else:
                        print(f"Потрібна палиця, щоб зібрати ягоди!")
                
                elif sprite['name'] == 'fish_spot' and 'fish' in location['items']:
                    self.collect_item('fish')
                    print(f"Ви зловили рибу!")
                
                elif sprite['name'] == 'treasure_chest' and 'treasure' in location['items']:
                    if self.selected_item is not None and self.inventory[self.selected_item] == 'key':
                        self.collect_item('treasure')
                        print(f"Ви відкрили скриню ключем та знайшли скарб!")
                    else:
                        print(f"Скриня замкнена. Потрібен ключ!")
                
                elif sprite['name'] == 'well' and 'key' in location['items']:
                    self.collect_item('key')
                    print(f"Ви знайшли ключ біля колодязя!")
                
                else:
                    print(f"Ви клікнули на {sprite['name']}")
    
    def collect_item(self, item_name):
        location = self.locations[self.current_location]
        if item_name in location['items']:
            self.inventory.append(item_name)
            location['items'].remove(item_name)
            if self.selected_item is None:
                self.selected_item = len(self.inventory) - 1
    
    def update(self):
        pass
        
    def render(self):
        # Фон локації
        location = self.locations[self.current_location]
        self.screen.fill(location['background'])
        
        # Малювання спрайтів
        for sprite in location['sprites']:
            pygame.draw.rect(self.screen, sprite['color'], sprite['rect'])
        
        # Інформація про поточну локацію
        location_text = self.font.render(f"Локація: {location['name']}", True, (255, 255, 255))
        self.screen.blit(location_text, (10, 10))
        
        # Доступні виходи
        exits_text = self.font.render(f"Виходи: {', '.join(location['exits'].keys())}", True, (255, 255, 255))
        self.screen.blit(exits_text, (10, 40))
        
        # Інвентар
        inventory_text = self.font.render("Інвентар:", True, (255, 255, 255))
        self.screen.blit(inventory_text, (10, 500))
        
        for i, item in enumerate(self.inventory):
            color = (255, 255, 0) if self.selected_item == i else (255, 255, 255)
            item_text = self.font.render(f"{i+1}. {self.items_info[item]['name']}", True, color)
            self.screen.blit(item_text, (10, 530 + i * 25))
        
        # Оновлення екрану
        pygame.display.flip()

# Головне меню (PyQt5)
class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пригодницька гра - Меню")
        self.setGeometry(100, 100, 400, 300)
        
        # Центральний віджет і макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title = QLabel("Пригодницька гра")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 24))
        layout.addWidget(title)
        
        # Кнопки
        start_button = QPushButton("Почати гру")
        start_button.clicked.connect(self.start_game)
        layout.addWidget(start_button)
        
        exit_button = QPushButton("Вихід")
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)
        
    def start_game(self):
        self.hide()
        self.game = Game()
        self.game.run()
        self.show()

# Запуск програми
if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())