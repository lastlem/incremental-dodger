import pygame
import random
import time
import math
import os
import sys

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (34, 139, 34)

WIDTH = HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Incremental Dodger")

FPS = 60
clock = pygame.time.Clock()

DEATH_DELAY = 0.3


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name: str, colorkey: int = None) -> pygame.Surface:
    """Загружает изображение и возвращает его как поверхность."""
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        terminate()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, max_health: int = 3, speed: int = 1, size_multiplier: float = 1.0, currency: int = 0):
        """Инициализация игрока с заданными параметрами."""
        super().__init__()
        self.base_image = pygame.Surface((50, 50))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = speed
        self.max_health = self.health = max_health
        self.size_multiplier = size_multiplier
        self.currency = currency
        self.alive = True
        self.damage_timer = 0
        self.player_area_x = self.player_area_y = 0
        self.player_area_size = 100
        self.update_player_area()

    def update_player_area(self):
        """Обновляет координаты области игрока в зависимости от его размера."""
        self.player_area_x = WIDTH // 2 - (self.player_area_size * self.size_multiplier) // 2
        self.player_area_y = HEIGHT // 2 - (self.player_area_size * self.size_multiplier) // 2

    def get_player_center(self) -> tuple:
        """Возвращает центр игрока."""
        return self.rect.center

    def update(self):
        """Обновляет состояние игрока."""
        self.update_image()
        self.update_player_area()

        if not self.alive:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if self.rect.left - self.speed >= self.player_area_x:
                self.rect.x -= self.speed
            else:
                self.rect.x = self.player_area_x

        if keys[pygame.K_RIGHT]:
            if self.rect.right + self.speed <= self.player_area_x + self.player_area_size * self.size_multiplier:
                self.rect.x += self.speed
            else:
                self.rect.right = self.player_area_x + self.player_area_size * self.size_multiplier

        if keys[pygame.K_UP]:
            if self.rect.top - self.speed >= self.player_area_y:
                self.rect.y -= self.speed
            else:
                self.rect.y = self.player_area_y

        if keys[pygame.K_DOWN]:
            if self.rect.bottom + self.speed <= self.player_area_y + self.player_area_size * self.size_multiplier:
                self.rect.y += self.speed
            else:
                self.rect.bottom = self.player_area_y + self.player_area_size * self.size_multiplier

    def take_damage(self):
        """Обрабатывает получение урона игроком."""
        self.damage_timer += 20
        if self.health > 0:
            self.health -= 1
        if self.health == 0:
            self.alive = False

    def update_image(self):
        """Обновляет изображение игрока в зависимости от здоровья."""
        health_height = 50 * self.health / self.max_health
        self.image = self.base_image.copy()

        if self.damage_timer > 0:
            self.damage_timer -= 1
            pygame.draw.rect(self.image, RED, (0, 50 - health_height, 50, health_height))
        else:
            pygame.draw.rect(self.image, GREEN, (0, 50 - health_height, 50, health_height))
        pygame.draw.rect(self.image, GREEN, (0, 0, 50, 50), 3)

    def increase_size(self):
        """Увеличивает размер игрока и его области."""
        self.size_multiplier += 0.2
        self.update_player_area()

    def increase_speed(self):
        """Увеличивает скорость игрока."""
        self.speed += 1

    def increase_max_health(self):
        """Увеличивает максимальное здоровье игрока."""
        self.max_health += 1

    def resurrect(self):
        """Воскрешает игрока, восстанавливая здоровье и сбрасывая состояние."""
        self.health = self.max_health
        self.alive = True
        self.damage_timer = 0
        self.rect.center = (WIDTH // 2, HEIGHT // 2)

    def add_currency(self, amount: int):
        """Добавляет валюту игроку."""
        self.currency += amount

    def spend_currency(self, amount: int) -> bool:
        """Пытается потратить валюту, возвращает True при успехе, иначе False."""
        if self.currency >= amount:
            self.currency -= amount
            return True
        return False

    def get_currency(self) -> int:
        """Возвращает количество валюты у игрока."""
        return self.currency

    def get_max_hp(self) -> int:
        """Возвращает максимальное здоровье игрока."""
        return self.max_health

    def get_speed(self) -> int:
        """Возвращает скорость игрока."""
        return self.speed

    def get_size_multiplier(self) -> float:
        """Возвращает множитель размера игрока."""
        return self.size_multiplier


def save_game_progress(player: Player, size_purchases: int, speed_purchases: int, hp_purchases: int):
    """Сохраняет прогресс игры в файл."""
    try:
        with open("game_progress.txt", "w") as file:
            file.write(f"{player.get_currency()}\n")
            file.write(f"{size_purchases}\n")
            file.write(f"{speed_purchases}\n")
            file.write(f"{hp_purchases}\n")
            file.write(f"{player.get_max_hp()}\n")
            file.write(f"{player.get_speed()}\n")
            file.write(f"{player.get_size_multiplier()}\n")
    except Exception:
        pass


def load_game_progress() -> tuple:
    """Загружает прогресс игры из файла."""
    if os.path.exists("game_progress.txt"):
        with open("game_progress.txt", "r") as file:
            currency = int(file.readline().strip())
            size_purchases = int(file.readline().strip())
            speed_purchases = int(file.readline().strip())
            hp_purchases = int(file.readline().strip())
            player_max_health = int(file.readline().strip())
            player_speed = int(file.readline().strip())
            player_size_multiplier = float(file.readline().strip())
            return (currency, size_purchases, speed_purchases, hp_purchases, player_max_health, player_speed,
                    player_size_multiplier)
    else:
        return 0, 0, 0, 0, 3, 1, 1.0


class Bullet(pygame.sprite.Sprite):
    bullet_image = load_image("bullet_image.png", colorkey=-1)
    particle_image = load_image('particles.png', colorkey=-1)

    def __init__(self, direction: str, player_center: tuple, speed: int):
        """Создает пулю с заданным направлением и начальной позицией."""
        super().__init__()
        self.image = pygame.transform.scale(self.bullet_image, (20, 20))
        self.rect = self.image.get_rect()
        self.direction = direction
        self.player_center = player_center
        self.speed = speed
        self.is_particle = False
        self.particle_timer = 0

        if direction == "top":
            self.rect.center = (random.randint(0, WIDTH), 0)
        elif direction == "bottom":
            self.rect.center = (random.randint(0, WIDTH), HEIGHT)
        elif direction == "left":
            self.rect.center = (0, random.randint(0, HEIGHT))
        elif direction == "right":
            self.rect.center = (WIDTH, random.randint(0, HEIGHT))

        offset_x = random.randint(-1, 1)
        offset_y = random.randint(-1, 1)

        target_x = player_center[0] + offset_x
        target_y = player_center[1] + offset_y

        self.angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
        self.image = pygame.transform.rotate(self.image, -math.degrees(self.angle) - 90)

    def update(self):
        """Обновляет позицию пули или превращает ее в частицы."""
        if self.is_particle:
            self.particle_timer += 1
            self.rect.x += random.randint(-1, 1)
            self.rect.y += random.randint(-1, 1)

            size_increase = self.particle_timer // 2
            self.image = pygame.transform.scale(self.particle_image, (20 + size_increase, 20 + size_increase))

            alpha = max(255 - (self.particle_timer * 5), 0)
            self.image.set_alpha(alpha)

            if self.particle_timer > 20:
                self.kill()
        else:
            self.rect.x += math.cos(self.angle) * self.speed
            self.rect.y += math.sin(self.angle) * self.speed

            if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT:
                self.kill()

    def on_collision(self):
        """При столкновении превращает пулю в частицы."""
        self.is_particle = True
        self.image = pygame.transform.scale(self.particle_image, (40, 40))
        self.rect = self.image.get_rect(center=self.rect.center)


# Магазин
class Shop:
    background_image = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))

    def __init__(self, player: Player, size_purchases: int, speed_purchases: int, hp_purchases: int):
        """Инициализация магазина с учетом покупок игрока."""
        self.player = player
        self.size_purchases = size_purchases
        self.speed_purchases = speed_purchases
        self.hp_purchases = hp_purchases

        self.size_max = 5
        self.speed_max = 3
        self.hp_max = 5
        self.font = pygame.font.Font(None, 28)

    def get_size_price(self) -> int:
        """Возвращает цену увеличения размера игрока."""
        return int(50 * (1.7 ** self.size_purchases))

    def get_speed_price(self) -> int:
        """Возвращает цену увеличения скорости игрока."""
        return int(30 * (3 ** self.speed_purchases))

    def get_hp_price(self) -> int:
        """Возвращает цену увеличения здоровья игрока."""
        return int(70 * (2 ** self.hp_purchases))

    def draw_button(self, button_rect: pygame.Rect, text: str, color: tuple, hover_color: tuple):
        """Рисует кнопку с текстом и цветами."""
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, button_rect)
        else:
            pygame.draw.rect(screen, color, button_rect)

        text_surface = self.font.render(text, True, BLACK)
        screen.blit(text_surface, (button_rect.x + (button_rect.width - text_surface.get_width()) // 2,
                                   button_rect.y + (button_rect.height - text_surface.get_height()) // 2))

    def show(self) -> bool:
        """Отображает магазин и обрабатывает покупки."""
        button_width = 300
        button_height = 60
        button_spacing = 20

        start_y = (HEIGHT - (5 * button_height + 4 * button_spacing)) // 2
        running = True

        while running:
            screen.fill(BLACK)
            screen.blit(self.background_image, (0, 0))

            currency_text = self.font.render(f"Currency: {self.player.get_currency()}", True, WHITE)
            screen.blit(currency_text, (10, 10))

            if self.size_purchases < self.size_max:
                size_button_text = \
                    f"Increase Player Area ({self.get_size_price()}) {self.size_purchases}/{self.size_max}"
            else:
                size_button_text = f"Increase Player Area MAX"

            self.draw_button(
                increase_size_button := pygame.Rect((WIDTH - button_width) // 2, start_y, button_width,
                                                    button_height), size_button_text, GREEN, LIGHT_GREEN)

            if self.speed_purchases < self.speed_max:
                speed_button_text = f"Increase Speed ({self.get_speed_price()}) {self.speed_purchases}/{self.speed_max}"
            else:
                speed_button_text = f"Increase Speed MAX"
            self.draw_button(increase_speed_button := pygame.Rect((WIDTH - button_width) // 2,
                                                                  start_y + button_height + button_spacing,
                                                                  button_width, button_height), speed_button_text, BLUE,
                             YELLOW)

            if self.hp_purchases < self.hp_max:
                hp_button_text = f"Increase HP ({self.get_hp_price()}) {self.hp_purchases}/{self.hp_max}"
            else:
                hp_button_text = f"Increase HP MAX"
            self.draw_button(increase_hp_button := pygame.Rect((WIDTH - button_width) // 2,
                                                               start_y + 2 * (button_height + button_spacing),
                                                               button_width, button_height), hp_button_text, RED,
                             LIGHT_GREEN)

            self.draw_button(restart_button := pygame.Rect((WIDTH - button_width) // 2,
                                                           start_y + 3 * (button_height + button_spacing), button_width,
                                                           button_height), "Restart Game", DARK_GREEN, LIGHT_GREEN)

            self.draw_button(exit_button := pygame.Rect((WIDTH - button_width) // 2,
                                                        start_y + 4 * (button_height + button_spacing), button_width,
                                                        button_height), "Exit Game", RED, LIGHT_GREEN)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (increase_size_button.collidepoint(event.pos) and self.size_purchases < self.size_max and
                            self.player.spend_currency(self.get_size_price())):
                        self.player.increase_size()
                        self.size_purchases += 1

                    elif (increase_speed_button.collidepoint(event.pos) and self.speed_purchases < self.speed_max and
                          self.player.spend_currency(self.get_speed_price())):
                        self.player.increase_speed()
                        self.speed_purchases += 1

                    elif (increase_hp_button.collidepoint(event.pos) and self.hp_purchases < self.hp_max and
                          self.player.spend_currency(self.get_hp_price())):
                        self.player.increase_max_health()
                        self.hp_purchases += 1

                    elif restart_button.collidepoint(event.pos):
                        save_game_progress(self.player, self.size_purchases, self.speed_purchases, self.hp_purchases)
                        return True

                    elif exit_button.collidepoint(event.pos):
                        save_game_progress(self.player, self.size_purchases, self.speed_purchases, self.hp_purchases)
                        terminate()

        return False


def game_loop():
    (currency, size_purchases, speed_purchases, hp_purchases, player_max_health, player_speed,
     player_size_multiplier) = load_game_progress()

    background_image = load_image('background.png')
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    player = Player(player_max_health, player_speed, player_size_multiplier, currency)
    shop = Shop(player, size_purchases, speed_purchases, hp_purchases)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    bullets = pygame.sprite.Group()
    start_time = time.time()
    last_bullet_time = time.time()

    last_currency_update = time.time()
    starting_currency_interval = currency_update_interval = 1
    min_currency_interval = 0.08
    currency_interval_decrease_factor = 0.003

    bullet_speed = starting_bullet_speed = 3
    bullet_interval = starting_bullet_interval = 1
    max_bullet_speed = 20
    min_bullet_spawn_interval = 0.1
    min_bullets_on_screen = 2

    speed_factor = 0.002
    spawn_interval_decrease_factor = 0.9985

    death_timer = 0
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if time.time() - last_bullet_time > bullet_interval or len(bullets) < min_bullets_on_screen:
            direction = random.choice(["top", "bottom", "left", "right"])
            bullet = Bullet(direction, (player.rect.centerx, player.rect.centery), bullet_speed)
            bullets.add(bullet)
            all_sprites.add(bullet)
            last_bullet_time = time.time()

        if time.time() - last_currency_update >= currency_update_interval:
            player.add_currency(1)
            last_currency_update = time.time()

        bullet_speed = min(bullet_speed + speed_factor, max_bullet_speed)
        bullet_interval = max(min_bullet_spawn_interval, bullet_interval * spawn_interval_decrease_factor)
        currency_update_interval = max(currency_update_interval - currency_interval_decrease_factor,
                                       min_currency_interval)

        all_sprites.update()

        collisions = pygame.sprite.spritecollide(player, bullets, False)
        if collisions:
            player.take_damage()
            for bullet in collisions:
                bullets.remove(bullet)
                bullet.on_collision()

        if player.health <= 0:
            if death_timer == 0:
                death_timer = time.time()
            elif time.time() - death_timer >= DEATH_DELAY:
                restart = shop.show()
                if restart:
                    all_sprites.empty()
                    bullets.empty()
                    player.resurrect()
                    all_sprites.add(player)
                    start_time = time.time()
                    currency_update_interval = starting_currency_interval
                    bullet_speed = starting_bullet_speed
                    bullet_interval = starting_bullet_interval
                    death_timer = 0

        screen.fill(BLACK)
        screen.blit(background_image, (0, 0))

        pygame.draw.rect(screen, WHITE,
                         (player.player_area_x, player.player_area_y,
                          player.player_area_size * player.size_multiplier,
                          player.player_area_size * player.size_multiplier), 3)

        all_sprites.draw(screen)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Time: {int(time.time() - start_time)}s", True, WHITE)
        currency_text = font.render(f"Currency: {player.get_currency()}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(currency_text, (10, 50))

        pygame.display.flip()


def start_screen():
    """Экран начала игры."""
    intro_text = [
        "Incremental Dodger!",
        "",
        "",
        "Правила игры:",
        "1. Управляйте игроком с помощью стрелок.",
        "2. Избегайте пуль, которые будут появляться.",
        "3. Зарабатывайте валюту и улучшайте своего персонажа.",
        "",
        "",
        "",
        "",
        "Нажмите любую клавишу или кликните мышью, чтобы начать!"
    ]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 36)
    text_coord = 180

    for line in intro_text:
        string_rendered = font.render(line, 1, WHITE)
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        if line == 'Incremental Dodger!':
            intro_rect.x = 300
        text_coord += intro_rect.height + 5
        screen.blit(string_rendered, intro_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        clock.tick(FPS)


start_screen()
game_loop()
