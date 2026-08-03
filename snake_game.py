"""Classic Snake game built with pygame.

Controls:
  1 / 2 / 3 — choose speed on the menu
  Arrow keys / WASD — move
  R — restart after game over (same speed)
  M — back to speed menu (from game over)
  Esc / Q — quit
"""

from __future__ import annotations

import random
import sys

import pygame

# --- Config ---
CELL_SIZE = 24
GRID_WIDTH = 28
GRID_HEIGHT = 20

WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + 40  # extra strip for score

BLACK = (18, 18, 22)
GRID = (28, 28, 34)
SNAKE_HEAD = (80, 220, 120)
SNAKE_BODY = (50, 170, 90)
FOOD = (230, 70, 70)
TEXT = (230, 230, 235)
MUTED = (140, 140, 150)
ACCENT = (80, 220, 120)
OVERLAY = (0, 0, 0, 160)

# label -> ticks per second
SPEEDS = (
    ("Slow", 8),
    ("Normal", 12),
    ("Fast", 18),
)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def random_empty_cell(snake: list[tuple[int, int]]) -> tuple[int, int]:
    occupied = set(snake)
    free = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in occupied
    ]
    return random.choice(free)


def draw_cell(surface: pygame.Surface, pos: tuple[int, int], color: tuple[int, int, int], inset: int = 1) -> None:
    x, y = pos
    rect = pygame.Rect(
        x * CELL_SIZE + inset,
        y * CELL_SIZE + inset,
        CELL_SIZE - inset * 2,
        CELL_SIZE - inset * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=4)


def draw_grid(surface: pygame.Surface) -> None:
    for x in range(GRID_WIDTH + 1):
        px = x * CELL_SIZE
        pygame.draw.line(surface, GRID, (px, 0), (px, GRID_HEIGHT * CELL_SIZE))
    for y in range(GRID_HEIGHT + 1):
        py = y * CELL_SIZE
        pygame.draw.line(surface, GRID, (0, py), (GRID_WIDTH * CELL_SIZE, py))


def new_game() -> tuple[list[tuple[int, int]], tuple[int, int], tuple[int, int], int]:
    mid_x, mid_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
    snake = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
    direction = RIGHT
    food = random_empty_cell(snake)
    score = 0
    return snake, direction, food, score


def draw_menu(
    screen: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    selected: int,
) -> None:
    screen.fill(BLACK)
    title = big_font.render("Snake", True, ACCENT)
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))

    subtitle = font.render("Choose speed", True, TEXT)
    screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 160)))

    for i, (label, fps) in enumerate(SPEEDS):
        prefix = ">" if i == selected else " "
        color = ACCENT if i == selected else MUTED
        line = font.render(f"{prefix}  {i + 1}. {label}  ({fps} fps)", True, color)
        screen.blit(line, line.get_rect(center=(WINDOW_WIDTH // 2, 230 + i * 40)))

    hint = font.render("Up/Down or 1-3  |  Enter to start  |  Esc quit", True, MUTED)
    screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 28)))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Snake")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)
    big_font = pygame.font.SysFont("consolas", 36, bold=True)

    state = "menu"  # menu | playing | game_over
    selected_speed = 1  # Normal by default
    speed_label, fps = SPEEDS[selected_speed]

    snake, direction, food, score = new_game()
    pending_direction = direction
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif state == "menu":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_speed = (selected_speed - 1) % len(SPEEDS)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_speed = (selected_speed + 1) % len(SPEEDS)
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        selected_speed = 0
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        selected_speed = 1
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        selected_speed = 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        speed_label, fps = SPEEDS[selected_speed]
                        snake, direction, food, score = new_game()
                        pending_direction = direction
                        state = "playing"
                elif state == "game_over":
                    if event.key == pygame.K_r:
                        snake, direction, food, score = new_game()
                        pending_direction = direction
                        state = "playing"
                    elif event.key == pygame.K_m:
                        state = "menu"
                elif state == "playing":
                    key_map = {
                        pygame.K_UP: UP,
                        pygame.K_w: UP,
                        pygame.K_DOWN: DOWN,
                        pygame.K_s: DOWN,
                        pygame.K_LEFT: LEFT,
                        pygame.K_a: LEFT,
                        pygame.K_RIGHT: RIGHT,
                        pygame.K_d: RIGHT,
                    }
                    if event.key in key_map:
                        new_dir = key_map[event.key]
                        if new_dir != OPPOSITE[direction]:
                            pending_direction = new_dir

        if state == "menu":
            draw_menu(screen, font, big_font, selected_speed)
            pygame.display.flip()
            clock.tick(30)
            continue

        if state == "playing":
            direction = pending_direction
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            hit_wall = (
                new_head[0] < 0
                or new_head[0] >= GRID_WIDTH
                or new_head[1] < 0
                or new_head[1] >= GRID_HEIGHT
            )
            hit_self = new_head in snake

            if hit_wall or hit_self:
                state = "game_over"
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    if len(snake) >= GRID_WIDTH * GRID_HEIGHT:
                        state = "game_over"
                    else:
                        food = random_empty_cell(snake)
                else:
                    snake.pop()

        # --- Draw game ---
        screen.fill(BLACK)
        draw_grid(screen)

        for i, segment in enumerate(snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            draw_cell(screen, segment, color)

        draw_cell(screen, food, FOOD, inset=3)

        score_surf = font.render(f"Score: {score}   Speed: {speed_label}", True, TEXT)
        screen.blit(score_surf, (12, GRID_HEIGHT * CELL_SIZE + 8))

        hint = font.render("Arrows/WASD  |  Esc quit", True, MUTED)
        screen.blit(hint, (WINDOW_WIDTH - hint.get_width() - 12, GRID_HEIGHT * CELL_SIZE + 8))

        if state == "game_over":
            overlay = pygame.Surface((WINDOW_WIDTH, GRID_HEIGHT * CELL_SIZE), pygame.SRCALPHA)
            overlay.fill(OVERLAY)
            screen.blit(overlay, (0, 0))

            title = big_font.render("Game Over", True, TEXT)
            sub = font.render(f"Score: {score}  —  R restart  |  M change speed", True, MUTED)
            screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, GRID_HEIGHT * CELL_SIZE // 2 - 20)))
            screen.blit(sub, sub.get_rect(center=(WINDOW_WIDTH // 2, GRID_HEIGHT * CELL_SIZE // 2 + 20)))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
