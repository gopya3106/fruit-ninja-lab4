import pygame
import random
from .fruit import Fruit
from .sounds import SoundManager

# Game Engine

WHITE = (255, 255, 255)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [(220, 60, 60), (230, 140, 40), (230, 200, 40), (90, 180, 90)]

# Difficulty settings: spawn_interval = frames between spawns (lower = faster)
DIFFICULTIES = {
    "Easy":   {"spawn_interval": 75, "bomb_chance": 0.08},
    "Medium": {"spawn_interval": 55, "bomb_chance": 0.15},
    "Hard":   {"spawn_interval": 35, "bomb_chance": 0.28},
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.speed_scale = 1.0
        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.sounds = SoundManager()
        self.difficulty = "Medium"
        self.reset(self.difficulty)

    def reset(self, difficulty):
        """Start a fresh game with the chosen difficulty."""
        self.difficulty = difficulty
        settings = DIFFICULTIES[difficulty]
        self.spawn_interval = settings["spawn_interval"]
        self.bomb_chance = settings["bomb_chance"]

        self.fruits = []
        self.trail = []  # recent mouse positions, drawn as the "blade"
        self._spawn_timer = 0
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(x, self.height + 30, vx, vy, gravity, kind=kind)
        fruit.color = BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)
        self.fruits.append(fruit)

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.reset("Easy")
                elif event.key == pygame.K_2:
                    self.reset("Medium")
                elif event.key == pygame.K_3:
                    self.reset("Hard")
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.type == pygame.MOUSEMOTION:
            self._handle_motion(event.pos)

    def _handle_motion(self, pos):
        # Previous mouse position (from the trail), or the current one on the first event
        prev = self.trail[-1] if self.trail else pos

        for fruit in self.fruits:
            if not fruit.sliced and fruit.intersects_segment(prev[0], prev[1], pos[0], pos[1]):
                self._slice(fruit)

        self.trail.append(pos)
        if len(self.trail) > 15:
            self.trail.pop(0)

    def _slice(self, fruit):
        fruit.sliced = True
        if fruit.kind == "bomb":
            self.sounds.play_bomb()
            self._end_game("You sliced a bomb!")
        else:
            self.score += 1
            self.sounds.play_slice()

    def _end_game(self, reason):
        if not self.game_over:
            self.game_over = True
            self.game_over_reason = reason
            self.sounds.play_game_over()

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []
        for fruit in self.fruits:
            fruit.update()
            if fruit.sliced:
                continue
            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue
            still_alive.append(fruit)
        self.fruits = still_alive

        if self.lives <= 0:
            self._end_game("You ran out of lives!")

    def render(self, screen):
        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)
            pygame.draw.circle(screen, color, (int(fruit.x), int(fruit.y)), fruit.radius)

        if len(self.trail) >= 2:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))

        if self.game_over:
            self._draw_game_over(screen)

    def _draw_game_over(self, screen):
        # Dim the background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        lines = [
            (self.big_font, "GAME OVER", (230, 60, 60), -140),
            (self.font, self.game_over_reason, WHITE, -85),
            (self.big_font, f"Final Score: {self.score}", (230, 200, 40), -25),
            (self.font, "Play again:  1 = Easy   2 = Medium   3 = Hard", WHITE, 55),
            (self.font, "Press Q or Esc to exit", WHITE, 100),
        ]
        for font, text, color, offset in lines:
            surf = font.render(text, True, color)
            rect = surf.get_rect(center=(self.width // 2, self.height // 2 + offset))
            screen.blit(surf, rect)
