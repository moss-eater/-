import sys
import os
import random
import pygame
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QProgressBar, QListWidget, 
                             QListWidgetItem, QPushButton, QFrame)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QColor, QFont, QPixmap, QIcon
pygame.init()

class GameState():
    """Клас для зберігання стану гри, доступного і для PyGame, і для PyQt5"""
    def __init__(self):
        self.health = 10
        self.max_health = 10
        self.armour = 5
        self.max_armour = 50
        self.score = 0
        self.inventory = ["Sword", "Зілля здоров'я", "Ключ"]
        self.player_x = 250
        self.player_y = 100
        self.items_on_ground = [
            {"name": "Золота монета", "x": 200, "y": 150},
            {"name": "Bow", "x": 150, "y": 300}
        ]
        self.attack = 5
        self.enemies = []  # Список ворогів
        self.current_time = 0  # Поточний час для відстеження кулдаунів
class Foe:
    def __init__(self, x, y, health=None, armor=None, attack=None, name="Ворог"):
        self.x = x
        self.y = y
        # Генеруємо випадкові характеристики, якщо вони не задані
        self.health = health if health is not None else random.randint(15, 30)
        self.max_health = self.health
        self.armor = armor if armor is not None else random.randint(0, 10)
        self.atk = attack if attack is not None else random.randint(2, 7)
        self.name = name
        self.is_alive = True
        self.speed = 1  # Швидкість руху ворога
        self.last_attack_time = 0  # Час останньої атаки
        self.attack_cooldown = 2.0  # Кулдаун атаки в секундах
        self.is_attacking = False  # Флаг, що показує чи ворог атакує
        self.attack_animation_time = 0  # Час початку анімації атаки
    



class PyGameWidget(QWidget):
    item_collected = pyqtSignal(str)
    health_changed = pyqtSignal(int)
    armour_changed = pyqtSignal(int)
    foe_defeated = pyqtSignal()
    
    def __init__(self, game_state, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 600)
        self.game_state = game_state
        
        # Ініціалізуємо pygame
        self.surface = pygame.Surface((500, 600))
        
        # Таймер для оновлення гри
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # ~60 FPS
        
        # Ігрові змінні
        self.keys_pressed = set()
        
        # Завантажуємо зображення персонажа та предметів
        self.player_img = pygame.Surface((30, 30))
        self.player_img.fill((255, 255, 255))
        
        self.item_img = pygame.Surface((20, 20))
        self.item_img.fill((255, 215, 0))  # Gold
        
        # Встановлюємо фокус, щоб отримувати події клавіатури
        self.setFocusPolicy(Qt.StrongFocus)

        try:
            # Завантаження зображень зброї
            self.sword_img = pygame.image.load("sord.png")
            self.sword_img = pygame.transform.scale(self.sword_img, (30, 30))
            
            self.bow_img = pygame.image.load("luck.png")
            self.bow_img = pygame.transform.scale(self.bow_img, (30, 30))
        except Exception as e:
            print(f"Помилка завантаження зображень зброї: {e}")
            self.sword_img = None
            self.bow_img = None
        
        # Змінна для поточної екіпіройваної зброї
        self.current_weapon = None
    
    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
    
    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())

    def check_collision_with_walls(self, new_x, new_y):
        # Якщо фонове зображення не завантажено, дозволяємо рух
        if not hasattr(self, 'background_image') or self.background_image is None:
            return True
        
        # Розмір спрайта гравця
        player_radius = 15
        
        # Перевірка точок навколо центру гравця
        check_points = [
            (new_x, new_y),  # Центр
            (new_x - player_radius, new_y),  # Ліво
            (new_x + player_radius, new_y),  # Право
            (new_x, new_y - player_radius),  # Верх
            (new_x, new_y + player_radius)   # Низ
        ]
        
        try:
            for x, y in check_points:
                # Перевіряємо, чи знаходиться точка в межах зображення
                if 0 <= x < self.background_image.get_width() and 0 <= y < self.background_image.get_height():
                    # Отримуємо колір пікселя
                    color = self.background_image.get_at((int(x), int(y)))
                    
                    # Тут визначаємо, які кольори є "стіною"
                    # Наприклад, білий або сірий колір
                    if color[0] > 240 and color[1] > 240 and color[2] > 240:  # Білий
                        return False
                    
                    if color[0] > 200 and color[1] > 200 and color[2] > 200:  # Світло-сірий
                        return False
        
        except Exception as e:
            print(f"Помилка перевірки колізії: {e}")

        return True
    
    def update_game(self):
        self.game_state.current_time = pygame.time.get_ticks() / 1000.0
        # Рух персонажа
        speed = 5
        new_x, new_y = self.game_state.player_x, self.game_state.player_y

        if Qt.Key_A in self.keys_pressed and self.game_state.player_x > 20:
            new_x = self.game_state.player_x - speed
            if self.check_collision_with_walls(new_x, self.game_state.player_y):
                self.game_state.player_x = new_x

        if Qt.Key_D in self.keys_pressed and self.game_state.player_x < 480:
            new_x = self.game_state.player_x + speed
            if self.check_collision_with_walls(new_x, self.game_state.player_y):
                self.game_state.player_x = new_x

        if Qt.Key_W in self.keys_pressed and self.game_state.player_y > 20:
            new_y = self.game_state.player_y - speed
            if self.check_collision_with_walls(self.game_state.player_x, new_y):
                self.game_state.player_y = new_y

        if Qt.Key_S in self.keys_pressed and self.game_state.player_y < 580:
            new_y = self.game_state.player_y + speed
            if self.check_collision_with_walls(self.game_state.player_x, new_y):
                self.game_state.player_y = new_y
        
        # Перевіряємо колізію з предметами
        for item in self.game_state.items_on_ground[:]:
            if (abs(self.game_state.player_x - item["x"]) < 30 and 
                abs(self.game_state.player_y - item["y"]) < 30):
                self.game_state.items_on_ground.remove(item)
                self.game_state.inventory.append(item["name"])
                self.item_collected.emit(item["name"])
                
                # Ефекти від зібраних предметів
                if "Зілля здоров'я" in item["name"]:
                    self.game_state.health = min(self.game_state.max_health, self.game_state.health + 20)
                    self.health_changed.emit(self.game_state.health)
        
            # Логіка атаки ворогів
        for foe in self.game_state.enemies:
            if foe.is_alive:
                # Визначаємо напрямок до гравця
                dx = self.game_state.player_x - foe.x
                dy = self.game_state.player_y - foe.y
                
                # Нормалізуємо вектор напрямку
                length = max(1, (dx**2 + dy**2)**0.5)
                dx /= length
                dy /= length
                
                # Рухаємо ворога в напрямку гравця з певною швидкістю
                foe.x += dx * foe.speed
                foe.y += dy * foe.speed
                
                # Перевірка на колізію з гравцем
                distance_to_player = ((self.game_state.player_x - foe.x)**2 + 
                                    (self.game_state.player_y - foe.y)**2)**0.5
                
                if distance_to_player < 30:  # Радіус колізії
                    # Ворог атакує гравця кожні 2 секунди
                    if self.game_state.current_time - foe.last_attack_time >= foe.attack_cooldown:
                        damage = max(1, foe.atk - self.game_state.armour / 10)
                        self.game_state.health -= damage
                        print(f"{foe.name} атакував вас і наніс {damage} шкоди!")
                        self.health_changed.emit(self.game_state.health)
                        
                        # Оновлюємо час останньої атаки
                        foe.last_attack_time = self.game_state.current_time
                        # Встановлюємо флаг атаки для анімації
                        foe.is_attacking = True
                        foe.attack_animation_time = self.game_state.current_time
        
        # Оновлюємо анімацію атаки
        for foe in self.game_state.enemies:
            if foe.is_attacking and self.game_state.current_time - foe.attack_animation_time > 0.5:
                foe.is_attacking = False
        
        # Обробка атаки гравця
        self.attack_foe()
        
        # Випадкові пошкодження (для демонстрації)
        #if random.random() < 0.005:  # 0.5% шанс пошкодження щотику
            #damage = random.randint(1, 5)
            #self.game_state.health = max(0, self.game_state.health - damage)
            #self.health_changed.emit(self.game_state.health)
        
        # Рендеринг гри
        if hasattr(self, 'background_image') and self.background_image is not None:
            self.surface.blit(self.background_image, (0, 0))
        else:
            self.surface.fill((50, 50, 50))  # Темний фон

        # Малюємо предмети на землі
        for item in self.game_state.items_on_ground:
            pygame.draw.rect(self.surface, (255, 215, 0), 
                            (item["x"] - 10, item["y"] - 10, 20, 20))
            
        # Малюємо ворогів (трикутники)
        for foe in self.game_state.enemies:
            if foe.is_alive:
                # Визначаємо напрямок до гравця для орієнтації трикутника
                angle = math.atan2(self.game_state.player_y - foe.y, self.game_state.player_x - foe.x)
                
                # Розрахунок вершин трикутника
                size = 20
                p1 = (foe.x + size * math.cos(angle), foe.y + size * math.sin(angle))
                p2 = (foe.x + size * math.cos(angle + 2.1), foe.y + size * math.sin(angle + 2.1))
                p3 = (foe.x + size * math.cos(angle - 2.1), foe.y + size * math.sin(angle - 2.1))
                
                # Малюємо трикутник
                pygame.draw.polygon(self.surface, (255, 0, 0), [p1, p2, p3])
                
                # Малюємо полоски здоров'я над ворогом
                health_ratio = foe.health / foe.max_health
                pygame.draw.rect(self.surface, (255, 0, 0), 
                                (foe.x - 15, foe.y - 25, 30, 5))
                pygame.draw.rect(self.surface, (0, 255, 0), 
                                (foe.x - 15, foe.y - 25, 30 * health_ratio, 5))
                
                # Малюємо анімацію вогню при атаці
                if foe.is_attacking:
                    # Створюємо кілька точок полум'я
                    for _ in range(10):
                        flame_x = foe.x + random.randint(-15, 15)
                        flame_y = foe.y + random.randint(-15, 15)
                        flame_size = random.randint(3, 8)
                        flame_color = (255, random.randint(100, 200), 0)  # Відтінки оранжевого
                        pygame.draw.circle(self.surface, flame_color, (int(flame_x), int(flame_y)), flame_size)
        
        # Малюємо границю світу
        #pygame.draw.rect(self.surface, (100, 100, 100), (10, 10, 480, 580), 2)
        
        # Малюємо персонажа
        pygame.draw.circle(self.surface, (255, 255, 255), 
                           (self.game_state.player_x, self.game_state.player_y), 15)
        
        if self.current_weapon == "Sword" and self.sword_img:
            # Позиціонування Swordа трохи праворуч від центру персонажа

            weapon_x = self.game_state.player_x + 20
            weapon_y = self.game_state.player_y - 10
            self.surface.blit(self.sword_img, (weapon_x, weapon_y))
            self.game_state.attack = self.game_state.attack + 5
        
        elif self.current_weapon == "Bow" and self.bow_img:
            # Позиціонування Bowа трохи ліворуч від центру персонажа
            weapon_x = self.game_state.player_x - 40
            weapon_y = self.game_state.player_y - 10
            self.surface.blit(self.bow_img, (weapon_x, weapon_y))
            self.game_state.attack = self.game_state.attack + 5
        
        
        
        # Відображаємо трохи інформації про гру
        font = pygame.font.SysFont(None, 24)
        pos_text = font.render(f"X: {self.game_state.player_x}, Y: {self.game_state.player_y}", 
                              True, (255, 255, 255))
        self.surface.blit(pos_text, (10, 10))
        
        # Оновлюємо віджет
        self.update()

    def attack_foe(self):
    # Перевіряємо чи є екіпірована зброя і чи є вороги
        if not self.game_state.enemies:
            return
        
        # Перевіряємо, чи натиснута клавіша атаки (наприклад, пробіл)
        if Qt.Key_Space in self.keys_pressed:
            # Пошук найближчого ворога
            closest_foe = None
            min_distance = float('inf')
            
            for foe in self.game_state.enemies:
                if foe.is_alive:
                    distance = ((self.game_state.player_x - foe.x) ** 2 + 
                            (self.game_state.player_y - foe.y) ** 2) ** 0.5
                    
                    # Перевіряємо, чи ворог у радіусі атаки (наприклад, 50 пікселів)
                    if distance < 50 and distance < min_distance:
                        min_distance = distance
                        closest_foe = foe
            
            # Якщо знайдено ворога в радіусі атаки
            if closest_foe:
                # Базове пошкодження залежить від атаки гравця
                damage = self.game_state.attack
                
                # Модифікатори для різних типів зброї
                if self.current_weapon == "Меч":
                    # Меч має шанс критичного удару
                    if random.random() < 0.2:  # 20% шанс критичного удару
                        damage *= 2
                        print("Критичний удар!")
                elif self.current_weapon == "Лук":
                    # Лук має більший радіус атаки, але менше пошкодження
                    # Вже враховано в self.game_state.atk
                    pass
                
                # Зменшуємо шкоду на броню ворога (кожні 5 од. броні зменшують шкоду на 1)
                damage_reduction = closest_foe.armor / 5
                damage = max(1, damage - damage_reduction)
                
                # Наносимо шкоду
                closest_foe.health -= damage
                print(f"Нанесено {damage} шкоди {closest_foe.name}!")
                
                # Перевіряємо чи ворог загинув
                if closest_foe.health <= 0:
                    closest_foe.is_alive = False
                    print(f"{closest_foe.name} переможений!")
                    
                    # Видаляємо ворога зі списку
                    self.game_state.enemies.remove(closest_foe)
                    
                    # Оновлюємо панель з характеристиками ворога
                    self.foe_defeated.emit()
                    
                    # Додаємо нагороду
                    self.game_state.score += 50
    
    def paintEvent(self, event):
        buffer = pygame.image.tostring(self.surface, "RGB")
        img = QImage(buffer, 500, 600, QImage.Format_RGB888)
        painter = QPainter(self)
        painter.drawImage(0, 0, img)
        painter.end()

    def set_background(self, image_path):
        """
        Встановлення фонового зображення.
        :param image_path: шлях до файлу зображення
        """
        try:
            # Завантажуємо зображення та масштабуємо до розміру віджета
            bg_img = pygame.image.load(image_path)
            self.background_image = pygame.transform.scale(bg_img, (500, 600))
        except Exception as e:
            print(f"Помилка завантаження зображення: {e}")
            # Якщо не вдалося завантажити, встановлюємо темний фон
            self.background_image = None


class InventoryWidget(QListWidget):
    def __init__(self, game_state, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.setStyleSheet("""
            QListWidget {
                background-color: #2D2D30;
                color: #FFFFFF;
                border: 1px solid #3F3F46;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 1px;
                border-bottom: 1px solid #3F3F46;
            }
            QListWidget::item:selected {
                background-color: #007ACC;
            }
        """)
        self.update_inventory()
    
    def update_inventory(self):
        self.clear()
        for item in self.game_state.inventory:
            item_widget = QListWidgetItem(item)
            self.addItem(item_widget)


class StatBar(QProgressBar):
    def __init__(self, value, max_value, color, parent=None):
        super().__init__(parent)
        self.setRange(0, max_value)
        self.setValue(value)
        self.setTextVisible(True)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #3F3F46;
                border-radius: 1px;
                text-align: center;
                background-color: #2D2D30;
                color: white;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 1px;
            }}
        """)


class GameInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyGame + PyQt5 гра")
        self.setGeometry(100, 100, 1000, 600)

        
        # Ініціалізуємо стан гри
        self.game_state = GameState()
        
        # Створюємо головний віджет і лейаут
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Частина для гри (PyGame)
        self.game_widget = PyGameWidget(self.game_state)
        self.game_widget.item_collected.connect(self.on_item_collected)
        self.game_widget.health_changed.connect(self.update_health)
        self.game_widget.armour_changed.connect(self.update_armour)

        # Додаємо список фонових зображень
        self.background_images = [
            "lg_00.png",  # Додайте реальні шляхи до зображень
            "lg_01.png", 
            "lg_02.png"
        ]
        
        # Частина для інтерфейсу (PyQt5)
        interface_widget = QWidget()
        interface_layout = QVBoxLayout(interface_widget)
        interface_widget.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        # Заголовок для інтерфейсу
        title_label = QLabel("Ігровий інтерфейс")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Рамка для статистики
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_frame.setStyleSheet("background-color: #252526; padding: 1px; border-radius: 1px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        # Здоров'я
        health_layout = QVBoxLayout()
        self.health_num = QLabel(f"Health -- {self.game_state.health}")
        health_layout.addWidget(self.health_num)
        
        # Щит
        armour_layout = QVBoxLayout()
        self.armour_num = QLabel(f"Armour -- {self.game_state.armour}")
        armour_layout.addWidget(self.armour_num)

        # Атака
        attack_layout = QVBoxLayout()
        self.attack_num = QLabel(f"Attack -- {self.game_state.attack}")
        attack_layout.addWidget(self.attack_num)
        
        # Додаємо статистику до рамки
        stats_layout.addLayout(health_layout)
        stats_layout.addLayout(armour_layout)
        stats_layout.addLayout(attack_layout)
        
        # Інвентар
        inventory_group = QFrame()
        inventory_group.setFrameShape(QFrame.StyledPanel)
        inventory_group.setStyleSheet("background-color: #252526; padding: 1px; border-radius: 1px;")
        inventory_layout = QVBoxLayout(inventory_group)
        
        inventory_label = QLabel("Інвентар:")
        inventory_label.setStyleSheet("font-weight: bold;")
        self.inventory_list = InventoryWidget(self.game_state)
        
        inventory_layout.addWidget(inventory_label)
        inventory_layout.addWidget(self.inventory_list)
        
        # Кнопки
        button_layout = QHBoxLayout()
        use_button = QPushButton("Use")
        equip_button = QPushButton("Equip")
        drop_button = QPushButton("Drop")
        unequip_button = QPushButton("Unequip")

        change_bg_button = QPushButton('''
        Перейти на наступний рівень
        Кімната не рахується якщо ви не перемогли ворога
        ''')
        change_bg_button.clicked.connect(self.change_background)
        interface_layout.addWidget(change_bg_button)
        
        button_layout.addWidget(use_button)
        button_layout.addWidget(drop_button)
        button_layout.addWidget(equip_button)
        button_layout.addWidget(unequip_button)
        
        # Обробники подій
        use_button.clicked.connect(self.use_item)
        drop_button.clicked.connect(self.drop_item)
        equip_button.clicked.connect(self.equip_item)
        unequip_button.clicked.connect(self.unequip_weapon)


        
        # Додаємо всі елементи до інтерфейсу
        interface_layout.addWidget(title_label)
        interface_layout.addWidget(stats_frame)
        interface_layout.addWidget(inventory_group)
        interface_layout.addLayout(button_layout)
        interface_layout.addStretch()
        
        # Додаємо всі частини до головного лейауту
        main_layout.addWidget(self.game_widget, 1)
        main_layout.addWidget(interface_widget, 1)

        self.change_background()

        # Підписуємось на сигнал про перемогу над ворогом
        self.game_widget.foe_defeated.connect(self.update_foe_info)
        
        # Створюємо рамку для інформації про ворога
        foe_info_frame = QFrame()
        foe_info_frame.setFrameShape(QFrame.StyledPanel)
        foe_info_frame.setStyleSheet("background-color: #252526; padding: 10px; border-radius: 5px;")
        foe_info_layout = QVBoxLayout(foe_info_frame)
        
        # Заголовок панелі
        foe_title = QLabel("Інформація про ворога")
        foe_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff5555;")
        foe_info_layout.addWidget(foe_title)
        
        # Елементи для відображення характеристик ворога
        self.foe_name_label = QLabel("Ім'я: Немає ворогів")
        self.foe_health_label = QLabel("Здоров'я: 0/0")
        self.foe_armor_label = QLabel("Броня: 0")
        self.foe_attack_label = QLabel("Атака: 0")
        
        # Додаємо елементи на панель
        foe_info_layout.addWidget(self.foe_name_label)
        foe_info_layout.addWidget(self.foe_health_label)
        foe_info_layout.addWidget(self.foe_armor_label)
        foe_info_layout.addWidget(self.foe_attack_label)
        
        # Додаємо рамку до інтерфейсу
        interface_layout.addWidget(foe_info_frame)
        
        # Додаємо таймер для оновлення інформації
        self.foe_info_timer = QTimer()
        self.foe_info_timer.timeout.connect(self.update_foe_info)
        self.foe_info_timer.start(500)  # Оновлюємо кожну півсекунди

    def on_item_collected(self, item_name):
        self.inventory_list.update_inventory()
    
    def update_health(self, health):
        self.health_num.setText(f"Health -- {health}")

    def update_attack(self, attack):
        self.attack_num.setText(f"Attack -- {attack}")
    
    def update_armour(self, armour):
        self.armour_num.setText(f"Armour -- {armour}")
    
    def update_foe_info(self):
        if not self.game_state.enemies:
            self.foe_name_label.setText("Ім'я: Немає ворогів")
            self.foe_health_label.setText("Здоров'я: 0/0")
            self.foe_armor_label.setText("Броня: 0")
            self.foe_attack_label.setText("Атака: 0")
        else:
            # Беремо першого (і єдиного) ворога
            foe = self.game_state.enemies[0]
            self.foe_name_label.setText(f"Ім'я: {foe.name}")
            self.foe_health_label.setText(f"Здоров'я: {foe.health}/{foe.max_health}")
            self.foe_armor_label.setText(f"Броня: {foe.armor}")
            self.foe_attack_label.setText(f"Атака: {foe.atk}")
    
    def change_background(self):
        """
        Автоматична зміна фону з попередньо визначеного списку
        """
        # Якщо список порожній, нічого не робимо
        if not self.background_images:
            return
        
        # Вибираємо випадкове зображення з списку
        background_file = random.choice(self.background_images)
        
        # Формуємо повний шлях до файлу (припускаємо, що зображення в папці backgrounds)
        full_path = os.path.join("lackgrounds", background_file)
        
        # Перевіряємо чи файл існує
        if os.path.exists(full_path):
            self.game_widget.set_background(full_path)
        else:
            print(f"Файл {full_path} не знайдено")
        
        self.game_state.enemies.clear()
    
        # Створюємо одного нового ворога з випадковими характеристиками
        # Розташовуємо його на деякій відстані від гравця
        foe_x = self.game_state.player_x + random.choice([-150, 150])
        foe_y = self.game_state.player_y + random.choice([-150, 150])
        
        # Переконуємося, що ворог не випав за межі карти
        foe_x = max(50, min(450, foe_x))
        foe_y = max(50, min(550, foe_y))
        
        # Створюємо ворога з випадковими характеристиками
        health = random.randint(15, 30)
        armor = random.randint(0, 10)
        attack = random.randint(2, 7)
        
        # Типи ворогів
        foe_types = ["Скелет", "Гоблін", "Зомбі", "Вовк"]
        foe_name = random.choice(foe_types)
        
        # Додаємо ворога до списку
        foe = Foe(foe_x, foe_y, health, armor, attack, foe_name)
        self.game_state.enemies.append(foe)
        
        # Оновлюємо інформацію про ворога
        self.update_foe_info()
    
    def use_item(self):
        selected_items = self.inventory_list.selectedItems()
        if not selected_items:
            return
            
        item_name = selected_items[0].text()
        
        # Обробка використання різних типів предметів
        if "Зілля здоров'я" in item_name:
            self.game_state.health = min(self.game_state.max_health, self.game_state.health + 5)
            self.update_health(self.game_state.health)
            self.game_state.inventory.remove(item_name)
        elif "Potiondamage" in item_name:
            self.game_state.health = min(self.game_state.max_health, self.game_state.health - 5)
            self.update_health(self.game_state.health)
            self.game_state.inventory.remove(item_name)
        elif "Goldcoin" in item_name:
            self.game_state.score += 10
            self.game_state.inventory.remove(item_name)
        
        # Оновлюємо інвентар
        self.inventory_list.update_inventory()
    
    def drop_item(self):
        selected_items = self.inventory_list.selectedItems()
        if not selected_items:
            return
            
        item_name = selected_items[0].text()
        
            # Якщо викидаємо екіпіровану зброю, скидаємо її
        if (item_name == "Sword" and self.game_widget.current_weapon == "Sword") or \
        (item_name == "Bow" and self.game_widget.current_weapon == "Bow"):
            self.game_widget.current_weapon = None
            self.game_state.attack = 5  # Базове значення атаки
            self.update_attack(self.game_state.attack)
        
        # Видаляємо предмет і додаємо на карту біля гравця
        self.game_state.inventory.remove(item_name)
        drop_x = self.game_state.player_x + random.randint(-50, 50)
        drop_y = self.game_state.player_y + random.randint(-50, 50)
        
        # Переконуємося, що предмет не випав за межі карти
        drop_x = max(30, min(470, drop_x))
        drop_y = max(30, min(570, drop_y))
        
        self.game_state.items_on_ground.append({
            "name": item_name,
            "x": drop_x,
            "y": drop_y
        })
        
        # Оновлюємо інвентар
        self.inventory_list.update_inventory()

    def equip_item(self):
        selected_items = self.inventory_list.selectedItems()
        if not selected_items:
            return
            
        item_name = selected_items[0].text()

        # Логіка екіпірування зброї
        if item_name == "Sword":
            self.game_widget.current_weapon = "Sword"
        elif item_name == "Bow":
            self.game_widget.current_weapon = "Bow"
        
        # Додаткова логіка для зміни статів гравця
        if item_name == "Sword":
            self.game_state.attack = 10  # Більша атака
        elif item_name == "Bow":
            self.game_state.attack = 7   # Менша атака
            self.game_state.armour += 5
        else:
        # Якщо вибрано не зброю, не змінюємо поточну зброю
            pass
    
        # Оновлюємо відображення атаки
        self.update_attack(self.game_state.attack)
        self.update_armour(self.game_state.armour)

        
        # Оновлюємо інвентар
        self.inventory_list.update_inventory()

        #головна штука -- зробити зміну у арморі гравця та його атаки
        #також я думаю зробити механіки рандому для Swordа та Bowа 
        #коли Bow, то шкода менша, то шанс удару по собі менший, коли Sword то шкода більша, шанс удару по собі більший
    
    def unequip_weapon(self):
        self.game_widget.current_weapon = None
        self.game_state.attack = 5  # Базове значення атаки
        self.game_state.armour = 5 # Базове значення броні
        self.update_attack(self.game_state.attack)
        self.update_armour(self.game_state.armour)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameInterface()
    window.show()
    sys.exit(app.exec_())