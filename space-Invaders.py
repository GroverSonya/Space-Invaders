import pygame
import random
import sys
from pygame import mixer

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (147, 0, 211)
DARK_GRAY = (40, 40, 40)

# Fonts
TITLE_FONT = pygame.font.Font(None, 74)
GAME_FONT = pygame.font.Font(None, 36)
SCORE_FONT = pygame.font.Font(None, 48)

class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        self.rect.x = self.x

    def draw(self):
        # Draw a more detailed spaceship
        pygame.draw.rect(screen, BLUE, (self.x, self.y + 10, self.width, self.height - 10))
        pygame.draw.polygon(screen, BLUE, [
            (self.x + self.width//2, self.y),
            (self.x + self.width, self.y + 10),
            (self.x, self.y + 10)
        ])
        # Add some details
        pygame.draw.rect(screen, WHITE, (self.x + self.width//2 - 2, self.y + 5, 4, self.height - 5))

class Bullet:
    def __init__(self, x, y):
        self.width = 4
        self.height = 15
        self.x = x
        self.y = y
        self.speed = 7
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True

    def move(self):
        self.y -= self.speed
        self.rect.y = self.y
        if self.y < 0:
            self.active = False

    def draw(self):
        # Draw a glowing effect for the bullet
        pygame.draw.rect(screen, WHITE, (self.x - 1, self.y, self.width + 2, self.height))
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y):
        self.width = 40
        self.height = 40
        self.x = x
        self.y = y
        self.speed = 2
        self.direction = 1
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.animation_frame = 0
        self.animation_speed = 0.1

    def move(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x
        self.animation_frame = (self.animation_frame + self.animation_speed) % 2

    def draw(self):
        # Draw a more interesting alien design
        color = PURPLE
        if self.animation_frame >= 1:
            # Alternate enemy appearance for animation
            pygame.draw.rect(screen, color, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
            pygame.draw.rect(screen, color, (self.x, self.y + 15, self.width, 10))
        else:
            pygame.draw.rect(screen, color, (self.x, self.y + 5, self.width, self.height - 10))
            pygame.draw.rect(screen, color, (self.x + 10, self.y, self.width - 20, self.height))

class Game:
    def __init__(self):
        self.reset_game()
        self.high_score = 0

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.create_enemies()

    def create_enemies(self):
        for row in range(5):
            for col in range(8):
                x = col * (50 + 20) + 50
                y = row * (40 + 20) + 80
                self.enemies.append(Enemy(x, y))

    def handle_collisions(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.score += 10
                    if self.score > self.high_score:
                        self.high_score = self.score

    def draw_stars(self):
        # Draw animated starfield background
        for i in range(50):
            x = random.randint(0, WIDTH)
            y = (random.randint(0, HEIGHT) + pygame.time.get_ticks() // 50) % HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)

    def update(self):
        if not self.game_over and self.game_started:
            self.player.move()
            
            for bullet in self.bullets[:]:
                bullet.move()
                if not bullet.active:
                    self.bullets.remove(bullet)

            move_down = False
            for enemy in self.enemies:
                enemy.move()
                if enemy.x <= 0 or enemy.x >= WIDTH - enemy.width:
                    move_down = True

            if move_down:
                for enemy in self.enemies:
                    enemy.direction *= -1
                    enemy.y += 20
                    if enemy.y >= HEIGHT - 100:
                        self.game_over = True

            self.handle_collisions()

    def draw_menu(self):
        title_text = TITLE_FONT.render("SPACE INVADERS", True, GREEN)
        start_text = GAME_FONT.render("Press SPACE to Start", True, WHITE)
        high_score_text = GAME_FONT.render(f"High Score: {self.high_score}", True, WHITE)
        
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        
        screen.blit(title_text, title_rect)
        screen.blit(start_text, start_rect)
        screen.blit(high_score_text, high_score_rect)

    def draw_game_ui(self):
        # Draw score with a nice background
        score_bg = pygame.Surface((200, 40))
        score_bg.fill(DARK_GRAY)
        score_bg.set_alpha(150)
        screen.blit(score_bg, (10, 10))
        
        score_text = SCORE_FONT.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 15))

    def draw(self):
        screen.fill(BLACK)
        self.draw_stars()
        
        if not self.game_started:
            self.draw_menu()
        else:
            self.player.draw()
            for bullet in self.bullets:
                bullet.draw()
            for enemy in self.enemies:
                enemy.draw()
            
            self.draw_game_ui()

            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill(BLACK)
                overlay.set_alpha(128)
                screen.blit(overlay, (0, 0))
                
                game_over_text = TITLE_FONT.render("GAME OVER", True, RED)
                restart_text = GAME_FONT.render("Press SPACE to Restart", True, WHITE)
                final_score_text = GAME_FONT.render(f"Final Score: {self.score}", True, WHITE)
                
                game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
                restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
                final_score_rect = final_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
                
                screen.blit(game_over_text, game_over_rect)
                screen.blit(restart_text, restart_rect)
                screen.blit(final_score_text, final_score_rect)

        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game.game_started:
                        game.game_started = True
                    elif game.game_over:
                        game.reset_game()
                        game.game_started = True
                    else:
                        bullet = Bullet(game.player.x + game.player.width//2 - 2, game.player.y)
                        game.bullets.append(bullet)

        game.update()
        game.draw()
        clock.tick(60)

if __name__ == "__main__":
    main()