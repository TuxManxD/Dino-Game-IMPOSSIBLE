import pygame
import random
import sys
import os

# Initialize Pygame with hardware acceleration
pygame.init()
pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF)

# Constants
WIDTH, HEIGHT = 800, 200
GROUND_HEIGHT = HEIGHT - 30
FPS = 60
FONT = pygame.font.Font(None, 36)
OBSTACLE_FREQUENCY = 0.008  # Adjust frequency of obstacle spawning
BOSS_FREQUENCY = 0.002  # Adjust frequency of boss spawning
OBSTACLE_VELOCITY = -10  # Adjust velocity of obstacles
BOSS_VELOCITY = 5  # Adjust velocity of boss movement
DINO_VELOCITY = 100  # Adjust velocity of dino
DINO_HEALTH = 100  # Adjust dino's health
BOSS_HEALTH = 200  # Adjust boss's health

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load assets
current_dir = os.path.dirname(__file__)
dino_image = pygame.image.load(os.path.join(current_dir, 'dino.png')).convert_alpha()
crouch_image = pygame.image.load(os.path.join(current_dir, 'crouch.png')).convert_alpha()
boss_image = pygame.image.load(os.path.join(current_dir, 'boss.png')).convert_alpha()

# Classes
class Dino(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(dino_image, (40, 60))
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_HEIGHT
        self.velocity_y = 0
        self.gravity = 1
        self.is_crouching = False  # Flag to track if dino is crouching
        self.health = DINO_HEALTH  # Dino's health attribute

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        if self.rect.bottom >= GROUND_HEIGHT:
            self.rect.bottom = GROUND_HEIGHT
            self.velocity_y = 0

    def jump(self):
        if self.rect.bottom == GROUND_HEIGHT:
            self.velocity_y = -18

    def crouch(self):
        if not self.is_crouching and self.rect.bottom == GROUND_HEIGHT:  # If dino is not already crouching and on the ground
            self.is_crouching = True
            self.image = pygame.transform.scale(crouch_image, (40, 30))
            self.rect.height = 30
            self.rect.bottom = GROUND_HEIGHT  # Adjust dino's position

    def stand_up(self):
        if self.is_crouching:  # If dino is crouching
            self.is_crouching = False
            self.image = pygame.transform.scale(dino_image, (40, 60))
            self.rect.height = 60
            self.rect.bottom = GROUND_HEIGHT  # Adjust dino's position

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 40))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WIDTH, GROUND_HEIGHT)  # Start from the right side of the screen
        self.velocity_x = OBSTACLE_VELOCITY

    def update(self):
        self.rect.x += self.velocity_x
        if self.rect.right < 0:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(boss_image, (80, 100))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WIDTH, GROUND_HEIGHT - 50)  # Start from the right side of the screen
        self.velocity_y = random.choice([-1, 1]) * BOSS_VELOCITY  # Random initial vertical velocity
        self.health = BOSS_HEALTH

    def update(self):
        self.rect.x -= 5
        self.rect.y += self.velocity_y

        # Reverse direction if hitting top or bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.velocity_y *= -1

# Function to display game over screen
def game_over_screen(screen, clock):
    game_over_text = FONT.render("Game Over", True, RED)
    retry_text = FONT.render("Press R to Retry", True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
    retry_rect = retry_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))

    screen.fill(WHITE)
    screen.blit(game_over_text, game_over_rect)
    screen.blit(retry_text, retry_rect)

    pygame.display.flip()

    # Wait for player input to retry
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart the game
    return False  # Quit the game

# Game setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrome Dino")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

# Function to initialize game
def initialize_game():
    # Create Dino
    dino = Dino()
    all_sprites.add(dino)

    return dino

# Function to restart game
def restart_game():
    all_sprites.empty()
    return initialize_game()

# Initialize game
dino = initialize_game()

# Game loop
game_over = False
while not game_over:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # If up arrow key is pressed
                dino.jump()
            elif event.key == pygame.K_DOWN:  # If down arrow key is pressed
                dino.crouch()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:  # If down arrow key is released
                dino.stand_up()

    # Update
    all_sprites.update()

    # Spawn obstacles
    if random.random() < OBSTACLE_FREQUENCY:
        obstacle = Obstacle()
        all_sprites.add(obstacle)

    # Spawn boss
    if random.random() < BOSS_FREQUENCY:
        boss = Boss()
        all_sprites.add(boss)

    # Check for collisions with obstacles and boss
    for obstacle in pygame.sprite.spritecollide(dino, all_sprites, False, collided=pygame.sprite.collide_mask):
        if isinstance(obstacle, Obstacle):
            # Reduce dino's health when colliding with an obstacle
            dino.health -= 10
            if dino.health <= 0:
                game_over = True
        elif isinstance(obstacle, Boss):
            # Reduce dino's health when colliding with the boss
            dino.health -= 20
            if dino.health <= 0:
                game_over = True

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

    # Display game over screen if game over
    if game_over:
        if game_over_screen(screen, clock):
            # Restart the game
            dino = restart_game()
            game_over = False

pygame.quit()
sys.exit()
