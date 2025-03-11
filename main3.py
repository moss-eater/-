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
        self.armour = 8
        self.max_armour = 10
        self.score = 0
        self.inventory = ["Меч", "Зілля здоров'я", "Ключ"]
        self.player_x = 100
        self.player_y = 100
        self.items_on_ground = [
            {"name": "Золота монета", "x": 200, "y": 150},
            {"name": "Лук", "x": 150, "y": 300}
        ]
class Foe():
    def __init__(self, hp, arm):
        self.hp = hp

class PyGameWidget(QWidget):
    item_collected = pyqtSignal(str)
    health_changed = pyqtSignal(int)
    armour_changed = pyqtSignal(int)
    attck_changed = pyqtSignal(int)
    
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
    
    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())
    
    def keyReleaseEvent(self, event):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())
    
    def update_game(self):
        # Рух персонажа
        speed = 5
        if Qt.Key_A in self.keys_pressed and self.game_state.player_x > 20:
            self.game_state.player_x -= speed
            self.game_state.armour = max(0, self.game_state.armour - 0.1)
            self.armour_changed.emit(self.game_state.armour)
        if Qt.Key_D in self.keys_pressed and self.game_state.player_x < 480:
            self.game_state.player_x += speed
            self.game_state.armour = max(0, self.game_state.armour - 0.1)
            self.armour_changed.emit(self.game_state.armour)
        if Qt.Key_W in self.keys_pressed and self.game_state.player_y > 20:
            self.game_state.player_y -= speed
            self.game_state.armour = max(0, self.game_state.armour - 0.1)
            self.armour_changed.emit(self.game_state.armour)
        if Qt.Key_S in self.keys_pressed and self.game_state.player_y < 580:
            self.game_state.player_y += speed
            self.game_state.armour = max(0, self.game_state.armour - 0.1)
            self.armour_changed.emit(self.game_state.armour)
        
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
                elif "Зілля енергії" in item["name"]:
                    self.game_state.armour = min(self.game_state.max_armour, self.game_state.armour + 30)
                    self.armour_changed.emit(self.game_state.armour)
        
        # Випадкові пошкодження (для демонстрації)
        #if random.random() < 0.005:  # 0.5% шанс пошкодження щотику
            #damage = random.randint(1, 5)
            #self.game_state.health = max(0, self.game_state.health - damage)
            #self.health_changed.emit(self.game_state.health)
        
        # Рендеринг гри
        self.surface.fill((50, 50, 50))  # Темний фон
        
        # Малюємо границю світу
        pygame.draw.rect(self.surface, (100, 100, 100), (10, 10, 480, 580), 2)
        
        # Малюємо персонажа
        pygame.draw.circle(self.surface, (0, 0, 255), 
                           (self.game_state.player_x, self.game_state.player_y), 15)
        
        # Малюємо предмети на землі
        for item in self.game_state.items_on_ground:
            pygame.draw.rect(self.surface, (255, 215, 0), 
                            (item["x"] - 10, item["y"] - 10, 20, 20))
        
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
        
        # Енергія
        armour_layout = QVBoxLayout()
        armour_label = QLabel("Енергія:")
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
        drop_button = QPushButton("Викинути")
        
        button_layout.addWidget(use_button)
        button_layout.addWidget(drop_button)
        
        # Обробники подій
        use_button.clicked.connect(self.use_item)
        drop_button.clicked.connect(self.drop_item)
        
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
    
    def on_item_collected(self, item_name):
        self.inventory_list.update_inventory()
    
    def update_health(self, health):
        self.health_bar.setValue(int(health))
    
    def update_armour(self, armour):
        self.armour_bar.setValue(int(armour))
    
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
        elif "Зілля енергії" in item_name:
            self.game_state.armour = min(self.game_state.max_armour, self.game_state.armour + 40)
            self.update_armour(self.game_state.armour)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameInterface()
    window.show()
    sys.exit(app.exec_())