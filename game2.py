import pygame
import sys
import random
import tkinter as tk
from tkinter import simpledialog

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Even Hunt MDM")

# Fonts and Colors
TITLE_FONT = pygame.font.SysFont(None, 72)
FONT = pygame.font.SysFont(None, 48)
SMALL_FONT = pygame.font.SysFont(None, 32)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (180, 180, 180)
GREEN = (0, 255, 0)

# Load intro image
intro_image = pygame.image.load("intro.png")
intro_image = pygame.transform.scale(intro_image, (WIDTH, HEIGHT))

# Helper function to draw text
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

# Helper function to draw button
def draw_button(rect, text, surface):
    pygame.draw.rect(surface, WHITE, rect)
    draw_text(text, SMALL_FONT, BLACK, surface, rect.centerx, rect.centery)

# Get odd input from user via tkinter dialog
def get_odd_n():
    root = tk.Tk()
    root.withdraw()
    while True:
        try:
            n = simpledialog.askinteger("Input", "Enter an odd number (n):")
            if n is not None and n % 2 == 1 and n > 0:
                return n
        except ValueError:
            pass

def run_game(n, skip_intro=False):
    show_intro = not skip_intro
    intro_start = pygame.time.get_ticks()
    game_done = False
    selected = []

    numbers = list(range(1, 2 * n + 1))
    table_buttons = []
    spacing = 80
    cols = min(8, 2 * n)  # Limit columns to at most 8
    rows = (2 * n + cols - 1) // cols

    total_width = cols * spacing
    total_height = rows * spacing
    start_x = (WIDTH - total_width) // 2
    start_y = 150

    for i, val in enumerate(numbers):
        row = i // cols
        col = i % cols
        rect = pygame.Rect(start_x + col * spacing, start_y + row * spacing, 60, 60)
        table_buttons.append({'rect': rect, 'value': val})

    restart_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)
    replace_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 160, 200, 40)

    title_displayed = False

    while True:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_done:
                for btn in table_buttons:
                    if btn['value'] != "" and btn['rect'].collidepoint(event.pos):
                        if btn in selected:
                            selected.remove(btn)  # unselect if already selected
                        elif len(selected) < 2:
                            selected.append(btn)

                if replace_button.collidepoint(event.pos) and len(selected) == 2:
                    a = selected[0]['value']
                    b = selected[1]['value']
                    diff = abs(a - b)

                    index1 = table_buttons.index(selected[0])
                    index2 = table_buttons.index(selected[1])

                    keep_index = min(index1, index2)
                    remove_index = max(index1, index2)

                    table_buttons[keep_index]['value'] = diff
                    table_buttons.pop(remove_index)

                    selected = []

                    # Re-layout
                    for i, btn in enumerate(table_buttons):
                        row = i // cols
                        col = i % cols
                        btn['rect'] = pygame.Rect(start_x + col * spacing, start_y + row * spacing, 60, 60)

                    if len(table_buttons) == 1:
                        game_done = True

            elif event.type == pygame.MOUSEBUTTONDOWN and game_done:
                if restart_button.collidepoint(event.pos):
                    run_game(n, skip_intro=True)

        if show_intro:
            if not title_displayed:
                draw_text("Even Hunt", TITLE_FONT, WHITE, screen, WIDTH//2, HEIGHT//2 - 50)
                if pygame.time.get_ticks() - intro_start > 2000:
                    title_displayed = True
                    intro_start = pygame.time.get_ticks()
            else:
                screen.blit(intro_image, (0, 0))
                if pygame.time.get_ticks() - intro_start > 5000:
                    show_intro = False
        else:
            draw_text("Even Hunt", TITLE_FONT, WHITE, screen, WIDTH//2, 60)

            for btn in table_buttons:
                color = GREEN if btn in selected else GRAY
                pygame.draw.rect(screen, color, btn['rect'])
                if btn['value'] != "":
                    draw_text(str(btn['value']), SMALL_FONT, BLACK, screen, btn['rect'].centerx, btn['rect'].centery)

            if len(selected) == 2 and not game_done:
                draw_button(replace_button, "Replace", screen)

            if game_done:
                final_value = table_buttons[0]['value']
                result_text = f"Final number: {final_value} - It's {'Even' if final_value % 2 == 0 else 'Odd'}!"
                draw_text(result_text, FONT, RED, screen, WIDTH//2, HEIGHT//2)
                draw_button(restart_button, "Restart", screen)

        pygame.display.flip()

# Initial setup
n = get_odd_n()
if n is not None:
    run_game(n)
else:
    pygame.quit()
    sys.exit()
