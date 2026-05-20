import random
import pygame
from typing import Tuple, Set, Optional

# Константы
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
BOARD_BACKGROUND_COLOR = (0, 0, 0)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
FPS = 15

# Все возможные ячейки поля
ALL_CELLS = {
    (x * CELL_SIZE, y * CELL_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

# Направления движения
RIGHT = (CELL_SIZE, 0)
LEFT = (-CELL_SIZE, 0)
UP = (0, -CELL_SIZE)
DOWN = (0, CELL_SIZE)

# Словарь для обработки нажатий клавиш
KEY_DIRECTION_MAP = {
    (pygame.K_RIGHT, RIGHT): RIGHT,
    (pygame.K_RIGHT, LEFT): RIGHT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
    (pygame.K_LEFT, RIGHT): LEFT,
    (pygame.K_LEFT, LEFT): LEFT,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, UP): UP,
    (pygame.K_UP, DOWN): UP,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, UP): DOWN,
    (pygame.K_DOWN, DOWN): DOWN,
}


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position: Tuple[int, int], body_color: Tuple[int, int, int]):
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """Абстрактный метод для отрисовки объекта."""
        self.draw_cell(surface, self.position, self.body_color)

    def draw_cell(self, surface: pygame.Surface, position: Tuple[int, int],
                  color: Tuple[int, int, int]) -> None:
        """Рисует одну ячейку на игровой поверхности."""
        pygame.draw.rect(
            surface,
            color,
            (position[0], position[1], CELL_SIZE, CELL_SIZE)
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self):
        super().__init__((0, 0), APPLE_COLOR)

    def randomize_position(self, occupied_cells: Optional[Set[Tuple[int, int]]] = None) -> None:
        """Устанавливает случайную позицию яблока."""
        if occupied_cells is None:
            occupied_cells = set()

        available_cells = ALL_CELLS - occupied_cells
        if available_cells:
            self.position = random.choice(tuple(available_cells))

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко."""
        self.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        self.length = 1
        self.positions = []
        self.direction = RIGHT
        self.next_direction = None
        self.record = 0
        self.reset()
        super().__init__(self.positions[0] if self.positions else (0, 0), SNAKE_COLOR)

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE
        self.positions = [(center_x, center_y)]
        self.direction = RIGHT
        self.next_direction = None

        if self.length > self.record:
            self.record = self.length

    def update_direction(self, key: Optional[int] = None) -> None:
        """Обновляет направление движения змейки."""
        if key is not None:
            new_direction = KEY_DIRECTION_MAP.get((key, self.direction), self.direction)
            if new_direction != self.direction:
                self.next_direction = new_direction

        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки."""
        head = self.get_head_position()

        new_head = (
            (head[0] + self.direction[0]) % SCREEN_WIDTH,
            (head[1] + self.direction[1]) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def grow(self) -> None:
        """Увеличивает длину змейки."""
        self.length += 1
        if self.length > self.record:
            self.record = self.length

    def check_self_collision(self) -> bool:
        """Проверяет столкновение змейки с собой."""
        if self.length < 4:
            return False
        head = self.get_head_position()
        return head in self.positions[1:]

    def get_occupied_cells(self) -> Set[Tuple[int, int]]:
        """Возвращает множество занятых змейкой ячеек."""
        return set(self.positions)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку."""
        for position in self.positions:
            self.draw_cell(surface, position, self.body_color)

    def draw_head(self, surface: pygame.Surface) -> None:
        """Отрисовывает только голову змейки."""
        if self.positions:
            self.draw_cell(surface, self.positions[0], self.body_color)

    def draw_tail(self, surface: pygame.Surface) -> None:
        """Отрисовывает только хвост змейки."""
        if len(self.positions) > 1:
            self.draw_cell(surface, self.positions[-1], BOARD_BACKGROUND_COLOR)


def main() -> None:
    """Основная функция игры."""
    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption(f'Изгиб Питона - Змейка (Рекорд: 0)')
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.get_occupied_cells())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    snake.update_direction(event.key)

        snake.move()

        # Проверка: съела ли змейка яблоко?
        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.get_occupied_cells())

        # Проверка: столкнулась ли змейка с собой?
        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position(snake.get_occupied_cells())

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()
        pygame.display.set_caption(
            f'Изгиб Питона - Змейка (Рекорд: {snake.record})'
        )

        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
