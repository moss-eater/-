import sys
import os
import random
import pygame
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QProgressBar, QListWidget, 
                             QListWidgetItem, QPushButton, QFrame)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QColor, QFont, QPixmap, QIcon


class GameState:
    """Клас для зберігання стану гри, доступного і для PyGame, і для PyQt5"""
    def __init__(self):
        self.health = 10
        self.max_health = 10
        self.armour = 5
        self.max_armour = 50
        self.score = 0
        self.inventory = ["Меч", "Зілля здоров'я", "Ключ"]
        self.player_x = 250
        self.player_y = 100
        self.items_on_ground = [
            {"name": "Золота монета", "x": 200, "y": 150},
            {"name": "Лук", "x": 150, "y": 300}
        ]
        self.atk = 5



class PyGameWidget(QWidget):
    item_collected = pyqtSignal(str)
    health_changed = pyqtSignal(int)
    armour_changed = pyqtSignal(int)
    
    def __init__(self, game_state, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 600)
        self.game_state = game_state
        
        # Ініціалізуємо pygame
        pygame.init()
        self.surface = pygame.Surface((500, 600))
        
        # Таймер для оновлення гри
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # ~60 FPS
        
        # Ігрові змінні
        self.keys_pressed = set()
        
        # Завантажуємо зображення персонажа та предметів
        self.player_img = pygame.Surface((30, 30))
        self.player_img.fill((0, 0, 255))
        
        self.item_img = pygame.Surface((20, 20))
        self.item_img.fill((255, 215, 0))  # Gold
        
        # Встановлюємо фокус, щоб отримувати події клавіатури
        self.setFocusPolicy(Qt.StrongFocus)

        try:
            # Завантаження зображень зброї
            self.sword_img = pygame.image.load("sord.png")
            self.sword_img = pygame.transform.scale(self.sword_img, (40, 40))
            
            self.bow_img = pygame.image.load("luck.png")
            self.bow_img = pygame.transform.scale(self.bow_img, (50, 30))
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
        
        # Малюємо границю світу
        #pygame.draw.rect(self.surface, (100, 100, 100), (10, 10, 480, 580), 2)
        
        # Малюємо персонажа
        pygame.draw.circle(self.surface, (0, 0, 255), 
                           (self.game_state.player_x, self.game_state.player_y), 15)
        
        if self.current_weapon == "Меч" and self.sword_img:
            # Позиціонування меча трохи праворуч від центру персонажа
            weapon_x = self.game_state.player_x + 20
            weapon_y = self.game_state.player_y - 10
            self.surface.blit(self.sword_img, (weapon_x, weapon_y))
        
        elif self.current_weapon == "Лук" and self.bow_img:
            # Позиціонування лука трохи ліворуч від центру персонажа
            weapon_x = self.game_state.player_x - 40
            weapon_y = self.game_state.player_y - 10
            self.surface.blit(self.bow_img, (weapon_x, weapon_y))
        
        
        
        # Відображаємо трохи інформації про гру
        font = pygame.font.SysFont(None, 24)
        pos_text = font.render(f"X: {self.game_state.player_x}, Y: {self.game_state.player_y}", 
                              True, (255, 255, 255))
        self.surface.blit(pos_text, (10, 10))
        
        # Оновлюємо віджет
        self.update()
    
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
                padding: 5px;
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
                border-radius: 5px;
                text-align: center;
                background-color: #2D2D30;
                color: white;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
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
        stats_frame.setStyleSheet("background-color: #252526; padding: 10px; border-radius: 5px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        # Здоров'я
        health_layout = QVBoxLayout()
        health_label = QLabel("Здоров'я:")
        self.health_bar = StatBar(self.game_state.health, self.game_state.max_health, "#E74C3C")
        health_layout.addWidget(health_label)
        health_layout.addWidget(self.health_bar)
        
        # Щит
        armour_layout = QVBoxLayout()
        armour_label = QLabel("Щит:")
        self.armour_bar = StatBar(self.game_state.armour, self.game_state.max_armour, "#3498DB")
        armour_layout.addWidget(armour_label)
        armour_layout.addWidget(self.armour_bar)
        
        # Додаємо статистику до рамки
        stats_layout.addLayout(health_layout)
        stats_layout.addLayout(armour_layout)
        
        # Інвентар
        inventory_group = QFrame()
        inventory_group.setFrameShape(QFrame.StyledPanel)
        inventory_group.setStyleSheet("background-color: #252526; padding: 10px; border-radius: 5px;")
        inventory_layout = QVBoxLayout(inventory_group)
        
        inventory_label = QLabel("Інвентар:")
        inventory_label.setStyleSheet("font-weight: bold;")
        self.inventory_list = InventoryWidget(self.game_state)
        
        inventory_layout.addWidget(inventory_label)
        inventory_layout.addWidget(self.inventory_list)
        
        # Кнопки
        button_layout = QHBoxLayout()
        use_button = QPushButton("Використати")
        equip_button = QPushButton("Взяти/Надягнути")
        drop_button = QPushButton("Викинути")

        change_bg_button = QPushButton("Змінити фон")
        change_bg_button.clicked.connect(self.change_background)
        interface_layout.addWidget(change_bg_button)
        
        button_layout.addWidget(use_button)
        button_layout.addWidget(drop_button)
        button_layout.addWidget(equip_button)
        
        # Обробники подій
        use_button.clicked.connect(self.use_item)
        drop_button.clicked.connect(self.drop_item)
        equip_button.clicked.connect(self.equip_item)
        
        # Інструкції
        instructions_frame = QFrame()
        instructions_frame.setFrameShape(QFrame.StyledPanel)
        instructions_frame.setStyleSheet("background-color: #252526; padding: 10px; border-radius: 5px;")
        instructions_layout = QVBoxLayout(instructions_frame)
        
        instructions_label = QLabel("Керування:")
        instructions_label.setStyleSheet("font-weight: bold;")
        
        instructions_text = QLabel(
            "Стрілки: рух персонажа\n"
            "Підійдіть до предмета, щоб підібрати його\n"
            "Використовуйте зілля для відновлення\n"
            "Рух витрачає енергію"
        )
        instructions_text.setWordWrap(True)
        
        instructions_layout.addWidget(instructions_label)
        instructions_layout.addWidget(instructions_text)
        
        # Додаємо всі елементи до інтерфейсу
        interface_layout.addWidget(title_label)
        interface_layout.addWidget(stats_frame)
        interface_layout.addWidget(inventory_group)
        interface_layout.addLayout(button_layout)
        interface_layout.addWidget(instructions_frame)
        interface_layout.addStretch()
        
        # Додаємо всі частини до головного лейауту
        main_layout.addWidget(self.game_widget, 1)
        main_layout.addWidget(interface_widget, 1)

        self.change_background()

    def on_item_collected(self, item_name):
        self.inventory_list.update_inventory()
    
    def update_health(self, health):
        self.health_bar.setValue(int(health))
    
    def update_armour(self, armour):
        self.armour_bar.setValue(int(armour))
    
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
    
    def use_item(self):
        selected_items = self.inventory_list.selectedItems()
        if not selected_items:
            return
            
        item_name = selected_items[0].text()
        
        # Обробка використання різних типів предметів
        if "Зілля здоров'я" in item_name:
            self.game_state.health = min(self.game_state.max_health, self.game_state.health + 25)
            self.update_health(self.game_state.health)
            self.game_state.inventory.remove(item_name)
        elif "Золота монета" in item_name:
            self.game_state.score += 10
            self.game_state.inventory.remove(item_name)
        
        # Оновлюємо інвентар
        self.inventory_list.update_inventory()
    
    def drop_item(self):
        selected_items = self.inventory_list.selectedItems()
        if not selected_items:
            return
            
        item_name = selected_items[0].text()
        
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
        if item_name == "Меч":
            self.game_widget.current_weapon = "Меч"
        elif item_name == "Лук":
            self.game_widget.current_weapon = "Лук"
        
        # Додаткова логіка для зміни статів гравця
        if item_name == "Меч":
            self.game_state.atk = 10  # Більша атака
        elif item_name == "Лук":
            self.game_state.atk = 7   # Менша атака
            self.game_state.armour += 10
        # Оновлюємо інвентар
        self.inventory_list.update_inventory()

        #головна штука -- зробити зміну у арморі гравця та його атаки
        #також я думаю зробити механіки рандому для меча та лука 
        #коли лук, то шкода менша, то шанс удару по собі менший, коли меч то шкода більша, шанс удару по собі більший


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameInterface()
    window.show()
    sys.exit(app.exec_())