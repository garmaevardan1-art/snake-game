import random

import pygame

from typing import Tuple


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int],
        body_color: Tuple[int, int, int]
    ):
        """
        Инициализация базового игрового объекта.

        Args:
            position: Позиция объекта на игровом поле (x, y)
            body_color: Цвет объекта в формате RGB
        """
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """
        Абстрактный метод для отрисовки объекта.

        Args:
            surface: Поверхность Pygame для отрисовки
        """
        pass


class Apple(GameObject):
    """Класс яблока, которое ест змейка."""

    def __init__(self, screen_size: Tuple[int, int], cell_size: int):
        """
        Инициализация яблока.

        Args:
            screen_size: Размер игрового поля (ширина, высота)
            cell_size: Размер одной ячейки в пикселях
        """
        self.screen_width, self.screen_height = screen_size
        self.cell_size = cell_size
        self.grid_width = self.screen_width // self.cell_size
        self.grid_height = self.screen_height // self.cell_size
        super().__init__((0, 0), (255, 0, 0))
        self.randomize_position()

    def randomize_position(self) -> None:
        """Устанавливает случайную позицию яблока в пределах игрового поля."""
        random_x = random.randint(0, self.grid_width - 1)
        random_y = random.randint(0, self.grid_height - 1)
        self.position = (
            random_x * self.cell_size,
            random_y * self.cell_size
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        pygame.draw.rect(
            surface,
            self.body_color,
            (
                self.position[0],
                self.position[1],
                self.cell_size,
                self.cell_size
            )
        )


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self, screen_size: Tuple[int, int], cell_size: int):
        """
        Инициализация змейки.

        Args:
            screen_size: Размер игрового поля (ширина, высота)
            cell_size: Размер одной ячейки в пикселях
        """
        self.screen_width, self.screen_height = screen_size
        self.cell_size = cell_size
        self.grid_width = self.screen_width // self.cell_size
        self.grid_height = self.screen_height // self.cell_size
        self.body_color = (0, 255, 0)
        self.last = None
        self.reset()
        super().__init__(self.positions[0], self.body_color)

    def reset(self) -> None:
        """
        Сбрасывает змейку в начальное состояние после столкновения.
        """
        self.length = 1

        center_x = (self.grid_width // 2) * self.cell_size
        center_y = (self.grid_height // 2) * self.cell_size
        self.positions = [(center_x, center_y)]

        directions = [(self.cell_size, 0), (0, self.cell_size)]
        self.direction = random.choice(directions)
        self.next_direction = None

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction is not None:
            is_opposite = (
                self.direction[0] == -self.next_direction[0]
                and self.direction[1] == -self.next_direction[1]
            )
            if not is_opposite:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки."""
        head = self.get_head_position()

        new_head = (
            (head[0] + self.direction[0]) % self.screen_width,
            (head[1] + self.direction[1]) % self.screen_height
        )

        if self.positions:
            self.last = self.positions[-1]

        if new_head in self.positions:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def grow(self) -> None:
        """Увеличивает длину змейки."""
        self.length += 1

    def check_self_collision(self) -> bool:
        """Проверяет столкновение змейки с собой."""
        head = self.get_head_position()
        return head in self.positions[1:]

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку на игровой поверхности."""
        for position in self.positions:
            pygame.draw.rect(
                surface,
                self.body_color,
                (
                    position[0],
                    position[1],
                    self.cell_size,
                    self.cell_size
                )
            )


def handle_keys(snake: Snake, event: pygame.event.Event) -> None:
    """
    Обрабатывает нажатия клавиш для изменения направления движения змейки.

    Args:
        snake: Объект змейки
        event: Событие Pygame
    """
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            snake.next_direction = (0, -snake.cell_size)
        elif event.key == pygame.K_DOWN:
            snake.next_direction = (0, snake.cell_size)
        elif event.key == pygame.K_LEFT:
            snake.next_direction = (-snake.cell_size, 0)
        elif event.key == pygame.K_RIGHT:
            snake.next_direction = (snake.cell_size, 0)


def main() -> None:
    """Основная функция игры."""
    pygame.init()

    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    CELL_SIZE = 20
    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
    BOARD_BACKGROUND_COLOR = (0, 0, 0)
    FPS = 15

    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Изгиб Питона - Змейка')
    clock = pygame.time.Clock()

    snake = Snake(SCREEN_SIZE, CELL_SIZE)
    apple = Apple(SCREEN_SIZE, CELL_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            handle_keys(snake, event)

        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position()

        if snake.check_self_collision():
            snake.reset()

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()

        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
