import pygame
import sys
import random

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu de Nim - Moroccan Math Day Edition")

# --- Fonts & Colors ---
FONT = pygame.font.SysFont(None, 40)
BIG_FONT = pygame.font.SysFont(None, 48)
BG_COLOR = (30, 30, 30)

# --- Load Intro Image ---
try:
    intro_image = pygame.image.load("intro.png").convert_alpha()
    intro_image = pygame.transform.scale(intro_image, (400, 300))
except:
    intro_image = pygame.Surface((400, 300))
    intro_image.fill((200, 50, 50))  # placeholder if image not found
intro_rect = intro_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

# --- Intro Texts ---
intro_lines = [
    "Welcome to the Invariance Principle",
    "Jeu de Nim — Moroccan Day of Mathematics"
]

# --- Confetti & Fireworks Class ---
class ConfettiParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.size = random.randint(4, 8)
        self.color = random.choice([(255,0,0), (0,255,0), (0,255,255), (255,255,0), (255,105,180)])
        self.speed = random.uniform(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = random.randint(-HEIGHT, 0)
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# --- Restart Button ---
BUTTON_RECT = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 50)

# --- Game Config ---
ROWS = 7
TOTAL_MATCHES = 20
MATCH_HEIGHT = 100
MATCH_WIDTH = 20
GAP_Y = 100
GAP_X = 60

# --- Generate pyramid match positions ---
matches = []
count = 0
for row in range(ROWS):
    for col in range(row + 1):
        if count >= TOTAL_MATCHES:
            break
        x = WIDTH // 2 - (row * (GAP_X // 2)) + col * GAP_X
        y = 100 + row * GAP_Y
        matches.append({
            "rect": pygame.Rect(x, y, MATCH_WIDTH, MATCH_HEIGHT),
            "alive": True,
            "index": count
        })
        count += 1

selected = []
current_player = 1
game_over = False
confetti = [ConfettiParticle() for _ in range(100)]  # 100 flying bits

# --- Draw Matches ---
def draw_matches():
    for match in matches:
        if not match["alive"]:
            continue
        idx = match["index"]
        color = (255, 0, 0) if idx == 0 else (255, 255, 0)
        if idx in selected:
            color = (100, 255, 100)
        pygame.draw.rect(screen, color, match["rect"], border_radius=4)

def draw_button():
    pygame.draw.rect(screen, (0, 120, 250), BUTTON_RECT, border_radius=8)
    label = FONT.render("Restart", True, (255, 255, 255))
    screen.blit(label, (BUTTON_RECT.x + 15, BUTTON_RECT.y + 10))

def draw_text(text):
    label = FONT.render(text, True, (255, 255, 255))
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 30))

# --- Game Logic ---
def handle_done():
    global current_player, game_over
    if 1 <= len(selected) <= 3:
        for idx in selected:
            matches[idx]["alive"] = False
        if not matches[0]["alive"]:  # red match taken
            game_over = True
        else:
            current_player = 2 if current_player == 1 else 1
    selected.clear()

# --- Show Intro ---
def show_intro():
    start_time = pygame.time.get_ticks()
    fade_duration = 5000  # 5 seconds
    clock = pygame.time.Clock()

    running = True
    while running:
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        alpha = max(0, 255 - int((elapsed / fade_duration) * 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BG_COLOR)

        # Draw and fade image
        img = intro_image.copy()
        img.set_alpha(alpha)
        screen.blit(img, intro_rect)

        # Draw and fade text
        for i, line in enumerate(intro_lines):
            text = BIG_FONT.render(line, True, (255, 255, 255))
            text.set_alpha(alpha)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 180 + i * 50))
            screen.blit(text, rect)

        pygame.display.flip()
        clock.tick(60)

        if elapsed >= fade_duration:
            running = False

# --- Main Game Loop ---
show_intro()

while True:
    screen.fill(BG_COLOR)
    draw_matches()

    # --- Victory Message Update ---
    if game_over:
        # Show Fireworks
        for c in confetti:
            c.update()
            c.draw(screen)

        # Show Flipping Text for Victory (centered and bigger)
        if pygame.time.get_ticks() % 1000 < 500:
            # Use a larger font for the victory message
            winner_text = BIG_FONT.render(f"🎉 Player {current_player} wins! 🎉", True, (255, 255, 255))
            
            # Center the text horizontally and vertically
            winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(winner_text, winner_rect)

        # Trophy Image (you can replace it with a better image)
        trophy = FONT.render("🏆", True, (255, 215, 0))
        screen.blit(trophy, (WIDTH // 2 - trophy.get_width() // 2, HEIGHT // 2 + 50))

        draw_button()  # Restart Button


    else:
        draw_button()  # Restart Button
        draw_text(f"Player {current_player}'s turn")

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BUTTON_RECT.collidepoint(event.pos):
                    # Restart the Game
                    matches = []
                    count = 0
                    for row in range(ROWS):
                        for col in range(row + 1):
                            if count >= TOTAL_MATCHES:
                                break
                            x = WIDTH // 2 - (row * (GAP_X // 2)) + col * GAP_X
                            y = 100 + row * GAP_Y
                            matches.append({
                                "rect": pygame.Rect(x, y, MATCH_WIDTH, MATCH_HEIGHT),
                                "alive": True,
                                "index": count
                            })
                            count += 1
                    selected.clear()
                    current_player = 1
                    game_over = False
                    confetti = [ConfettiParticle() for _ in range(100)]  # Reset fireworks
                continue

        if game_over:
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            if BUTTON_RECT.collidepoint(event.pos):
                handle_done()
            else:
                for m in matches:
                    if m["alive"] and m["index"] not in selected and len(selected) < 3:
                        if m["rect"].collidepoint(event.pos):
                            selected.append(m["index"])
