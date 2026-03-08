import pygame
import random
import sys
from enum import Enum
from collections import deque

# Initialize Pygame at module level
pygame.init()

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Window and Grid Settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE

# Colors (RGB - Forest Green Theme)
COLOR_BLACK = (20, 20, 20)
COLOR_GREEN = (34, 139, 34)
COLOR_LIGHT_GREEN = (60, 180, 60)
COLOR_RED = (220, 50, 50)
COLOR_GRAY = (100, 100, 100)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_GREEN = (25, 100, 25)


# Game State Enumeration
class GameState(Enum):
    """Represents different states the game can be in."""

    MENU = 1
    PLAYING = 2
    GAME_OVER = 3


# Difficulty Level Enumeration
class Difficulty(Enum):
    """Defines difficulty levels with their parameters."""

    EASY = {"obstacles": 5, "speed": 10, "name": "Easy"}
    MEDIUM = {"obstacles": 10, "speed": 15, "name": "Medium"}
    HARD = {"obstacles": 20, "speed": 20, "name": "Hard"}


# Direction Enumeration
class Direction(Enum):
    """Represents movement directions as (dx, dy) tuples."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


# ============================================================================
# MAIN GAME CLASS
# ============================================================================


class SnakeGame:
    """Main game controller for Snake Game."""

    def __init__(self):
        """Initialize the game engine and Pygame."""
        # Display Setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)

        # Game State
        self.state = GameState.MENU
        self.difficulty = None
        self.score = 0
        self.game_speed = 0

        # Snake
        self.snake = deque()
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

        # Game Objects
        self.food = None
        self.obstacles = set()

        # Timing
        self.move_counter = 0

    def reset_game(self):
        """Reset game state for a new game based on selected difficulty."""
        self.score = 0
        self.move_counter = 0

        # Initialize snake in center moving right with 3 segments
        start_x = GRID_SIZE // 2
        start_y = GRID_SIZE // 2
        self.snake = deque(
            [(start_x - 2, start_y), (start_x - 1, start_y), (start_x, start_y)]
        )

        # Reset direction
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

        # Generate obstacles based on difficulty
        self.generate_obstacles()

        # Spawn initial food
        self.food = self.spawn_food()

        # Set game speed based on difficulty
        if self.difficulty:
            self.game_speed = self.difficulty.value["speed"]

        self.state = GameState.PLAYING

    def generate_obstacles(self):
        """Generate random obstacles based on difficulty level."""
        self.obstacles.clear()
        if not self.difficulty:
            return

        num_obstacles = self.difficulty.value["obstacles"]

        # Get all occupied cells (snake, food)
        occupied = set(self.snake)
        if self.food:
            occupied.add(self.food)

        # Place obstacles avoiding occupied cells
        attempts = 0
        max_attempts = num_obstacles * 10

        while len(self.obstacles) < num_obstacles and attempts < max_attempts:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)

            if (x, y) not in occupied and (x, y) not in self.obstacles:
                self.obstacles.add((x, y))

            attempts += 1

    def spawn_food(self):
        """Spawn food at a random unoccupied cell."""
        occupied = set(self.snake) | self.obstacles

        # Prevent infinite loop on full board
        attempts = 0
        max_attempts = GRID_SIZE * GRID_SIZE

        while attempts < max_attempts:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)

            if (x, y) not in occupied:
                return (x, y)

            attempts += 1

        # Fallback: find first available cell
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if (x, y) not in occupied:
                    return (x, y)

        # Should never happen in normal gameplay
        return (0, 0)

    def handle_input(self):
        """Handle keyboard input and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.state == GameState.MENU:
                    if event.key == pygame.K_1:
                        self.difficulty = Difficulty.EASY
                        self.reset_game()
                    elif event.key == pygame.K_2:
                        self.difficulty = Difficulty.MEDIUM
                        self.reset_game()
                    elif event.key == pygame.K_3:
                        self.difficulty = Difficulty.HARD
                        self.reset_game()

                elif self.state == GameState.PLAYING:
                    # Handle direction changes with reversal prevention
                    if (
                        event.key == pygame.K_UP
                        and self.direction != Direction.DOWN
                        and self.next_direction != Direction.DOWN
                    ):
                        self.next_direction = Direction.UP
                    elif (
                        event.key == pygame.K_DOWN
                        and self.direction != Direction.UP
                        and self.next_direction != Direction.UP
                    ):
                        self.next_direction = Direction.DOWN
                    elif (
                        event.key == pygame.K_LEFT
                        and self.direction != Direction.RIGHT
                        and self.next_direction != Direction.RIGHT
                    ):
                        self.next_direction = Direction.LEFT
                    elif (
                        event.key == pygame.K_RIGHT
                        and self.direction != Direction.LEFT
                        and self.next_direction != Direction.LEFT
                    ):
                        self.next_direction = Direction.RIGHT

                elif self.state == GameState.GAME_OVER:
                    self.state = GameState.MENU

        return True

    def update_game(self):
        """Update game logic."""
        if self.state != GameState.PLAYING:
            return

        # Increment move counter
        self.move_counter += 1

        # Move snake at specified speed (avoid division by zero)
        if self.game_speed > 0 and self.move_counter >= 60 // self.game_speed:
            self.move_counter = 0
            self.direction = self.next_direction

            # Calculate new head position
            head_x, head_y = self.snake[-1]
            dx, dy = self.direction.value
            new_head = (head_x + dx, head_y + dy)

            # Check collisions
            if self.check_collisions(new_head):
                self.state = GameState.GAME_OVER
                return

            # Add new head
            self.snake.append(new_head)

            # Check if food eaten
            if new_head == self.food:
                self.score += 1
                self.food = self.spawn_food()
            else:
                # Remove tail if no food eaten
                self.snake.popleft()

    def check_collisions(self, position):
        """Check if position causes collision. Returns True if collision occurs."""
        x, y = position

        # Check wall collision
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return True

        # Check self collision
        if position in self.snake:
            return True

        # Check obstacle collision
        if position in self.obstacles:
            return True

        return False

    def draw_menu(self):
        """Draw the difficulty selection menu."""
        self.screen.fill(COLOR_BLACK)

        # Title
        title = self.font_large.render("SNAKE GAME", True, COLOR_LIGHT_GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_small.render("Select Difficulty:", True, COLOR_WHITE)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)

        # Options
        easy_text = self.font_medium.render(
            "1 - Easy (5 obstacles, slow)", True, COLOR_GREEN
        )
        easy_rect = easy_text.get_rect(center=(WINDOW_WIDTH // 2, 280))
        self.screen.blit(easy_text, easy_rect)

        medium_text = self.font_medium.render(
            "2 - Medium (10 obstacles)", True, COLOR_LIGHT_GREEN
        )
        medium_rect = medium_text.get_rect(center=(WINDOW_WIDTH // 2, 360))
        self.screen.blit(medium_text, medium_rect)

        hard_text = self.font_medium.render(
            "3 - Hard (20 obstacles, fast)", True, COLOR_RED
        )
        hard_rect = hard_text.get_rect(center=(WINDOW_WIDTH // 2, 440))
        self.screen.blit(hard_text, hard_rect)

        # Instructions
        instruction = self.font_small.render("Press ESC to quit", True, COLOR_GRAY)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 540))
        self.screen.blit(instruction, instruction_rect)

    def draw_game(self):
        """Draw the game board, snake, food, and obstacles."""
        self.screen.fill(COLOR_BLACK)

        # Draw grid background (subtle)
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(
                self.screen, COLOR_DARK_GREEN, (x, 0), (x, WINDOW_HEIGHT), 1
            )
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(
                self.screen, COLOR_DARK_GREEN, (0, y), (WINDOW_WIDTH, y), 1
            )

        # Draw obstacles
        for obs_x, obs_y in self.obstacles:
            rect = pygame.Rect(
                obs_x * CELL_SIZE, obs_y * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_GRAY, rect)
            pygame.draw.rect(self.screen, COLOR_WHITE, rect, 1)

        # Draw food
        if self.food:
            food_x, food_y = self.food
            rect = pygame.Rect(
                food_x * CELL_SIZE + 2,
                food_y * CELL_SIZE + 2,
                CELL_SIZE - 4,
                CELL_SIZE - 4,
            )
            pygame.draw.ellipse(self.screen, COLOR_RED, rect)

        # Draw snake
        for i, (seg_x, seg_y) in enumerate(self.snake):
            rect = pygame.Rect(
                seg_x * CELL_SIZE + 2,
                seg_y * CELL_SIZE + 2,
                CELL_SIZE - 4,
                CELL_SIZE - 4,
            )

            # Head is brighter
            if i == len(self.snake) - 1:
                pygame.draw.rect(self.screen, COLOR_LIGHT_GREEN, rect, 0)
                pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2)
            else:
                pygame.draw.rect(self.screen, COLOR_GREEN, rect, 0)
                pygame.draw.rect(self.screen, COLOR_LIGHT_GREEN, rect, 1)

        # Draw score
        score_text = self.font_small.render(f"Score: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw difficulty level
        if self.difficulty:
            difficulty_name = self.difficulty.value["name"]
            difficulty_text = self.font_small.render(
                f"Level: {difficulty_name}", True, COLOR_LIGHT_GREEN
            )
            self.screen.blit(difficulty_text, (10, 40))

    def draw_game_over(self):
        """Draw the game over screen."""
        # Semi-transparent overlay with per-pixel alpha
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game Over message
        game_over_text = self.font_large.render("GAME OVER", True, COLOR_RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(game_over_text, game_over_rect)

        # Final score
        score_text = self.font_medium.render(
            f"Score: {self.score}", True, COLOR_LIGHT_GREEN
        )
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)

        # Instructions
        instruction = self.font_small.render(
            "Press any key to return to menu", True, COLOR_WHITE
        )
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 400))
        self.screen.blit(instruction, instruction_rect)

    def draw(self):
        """Draw based on current game state."""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        try:
            while running:
                running = self.handle_input()
                self.update_game()
                self.draw()

                # Frame rate cap
                self.clock.tick(60)
        except Exception as e:
            print(f"Error during gameplay: {e}")
        finally:
            pygame.quit()
            sys.exit()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    game = SnakeGame()
    game.run()