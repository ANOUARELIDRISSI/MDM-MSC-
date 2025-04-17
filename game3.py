import pygame
import math
import sys
import time

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Magic Circle")
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SECTOR_COLOR = (100, 100, 255)
BUTTON_COLOR = (180, 180, 180)
HOVER_COLOR = (160, 160, 160)

# Game state
nums = [1, 0, 1, 0, 0, 0]
num_sectors = 6
radius = 200
center = (400, HEIGHT // 2)  # Adjusted for wider screen

intro_phase = 0  # 0 = show image, 1 = show title, 2 = done
intro_start_time = time.time()
intro_shown = True
intro_image = pygame.image.load("intro.png")
intro_image = pygame.transform.scale(intro_image, (WIDTH, HEIGHT))

# Buttons (on the right side)
buttons = {
    "check": pygame.Rect(900, 100, 200, 50),
    "invariant": pygame.Rect(900, 170, 200, 50),
    "reset": pygame.Rect(900, 240, 200, 50)
}

# Messages
message = ""
message_timer = 0

def draw_circle_sectors():
    angle_per_sector = 2 * math.pi / num_sectors
    for i in range(num_sectors):
        start_angle = i * angle_per_sector
        end_angle = (i + 1) * angle_per_sector

        points = [center]
        for angle in [start_angle, end_angle]:
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))

        pygame.draw.polygon(screen, SECTOR_COLOR, points)
        pygame.draw.polygon(screen, BLACK, points, 2)

        # Draw the number
        angle_mid = (start_angle + end_angle) / 2
        text_x = center[0] + (radius // 2) * math.cos(angle_mid)
        text_y = center[1] + (radius // 2) * math.sin(angle_mid)
        text = font.render(str(nums[i]), True, BLACK)
        text_rect = text.get_rect(center=(text_x, text_y))
        screen.blit(text, text_rect)

def get_sector_from_pos(pos):
    dx, dy = pos[0] - center[0], pos[1] - center[1]
    angle = (math.atan2(dy, dx) + 2 * math.pi) % (2 * math.pi)
    sector = int(angle / (2 * math.pi / num_sectors))
    return sector

def increase_neighbors(sector):
    nums[sector] += 1
    nums[(sector + 1) % num_sectors] += 1

def all_equal():
    return all(n == nums[0] for n in nums)

def compute_invariant():
    signs = [1, -1, 1, -1, 1, -1]
    return sum(signs[i] * nums[i] for i in range(6))

def draw_buttons():
    mouse = pygame.mouse.get_pos()
    for name, rect in buttons.items():
        color = HOVER_COLOR if rect.collidepoint(mouse) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        label = name.capitalize() if name != "check" else "Check Equal"
        text = font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

def show_message(msg):
    global message, message_timer
    message = msg
    message_timer = time.time()

def draw_message():
    if message and time.time() - message_timer < 3:
        text = font.render(message, True, BLACK)
        screen.blit(text, (WIDTH - 300, HEIGHT - 40))

def reset_game():
    global nums
    nums = [1, 0, 1, 0, 0, 0]

def draw_intro():
    global intro_phase, intro_start_time
    elapsed = time.time() - intro_start_time

    if intro_phase == 0:
        if elapsed < 2.5:
            screen.blit(intro_image, (0, 0))
            return True
        else:
            intro_phase = 1
            intro_start_time = time.time()
            return True

    elif intro_phase == 1:
        if elapsed < 2.5:
            screen.fill(BLACK)
            title = big_font.render("The Magic Circle", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(title, title_rect)
            return True
        else:
            intro_phase = 2
            return False

    return False

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    if intro_shown:
        intro_still = draw_intro()
        if not intro_still:
            intro_shown = False
    else:
        draw_circle_sectors()
        draw_buttons()
        draw_message()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if not intro_shown:
                if center[0] - radius <= pos[0] <= center[0] + radius and \
                   center[1] - radius <= pos[1] <= center[1] + radius:
                    sector = get_sector_from_pos(pos)
                    increase_neighbors(sector)

                if buttons["check"].collidepoint(pos):
                    result = "Yes" if all_equal() else "No"
                    show_message(f"All equal? {result}")

                elif buttons["invariant"].collidepoint(pos):
                    inv = compute_invariant()
                    show_message(f"Invariant: {inv}")

                elif buttons["reset"].collidepoint(pos):
                    reset_game()
                    show_message("Game Reset")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
