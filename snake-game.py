import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Set up game variables
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (169, 169, 169)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Initialize clock
clock = pygame.time.Clock()

# Load sounds
eat_sound = pygame.mixer.Sound("C:/Jects/Python Snake Game/eat.wav")
game_over_sound = pygame.mixer.Sound("C:/Jects/Python Snake Game/game_over.wav")

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Snake class
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [((WIDTH / 2), (HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = WHITE
        self.last_direction = self.direction

    def get_head_position(self):
        return self.positions[0]

    def update(self, obstacles, vertical_obstacles):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0] + (x * GRID_SIZE)) % WIDTH), (cur[1] + (y * GRID_SIZE)) % HEIGHT)

        # Check for collisions with obstacles
        if len(self.positions) > 2 and any(new == (obs.x + i * GRID_SIZE, obs.y) for obs in obstacles for i in range(obs.length)):
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

        # Check for collisions with vertical obstacles
        for vertical_obstacle in vertical_obstacles:
            if (
                new[0] == vertical_obstacle.x
                and new[1] >= vertical_obstacle.y
                and new[1] < vertical_obstacle.y + vertical_obstacle.length * GRID_SIZE
            ):
                self.reset()

    def reset(self):
        self.length = 1
        self.positions = [((WIDTH / 2), (HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        game_over_sound.play()

    def render(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color, (p[0], p[1], GRID_SIZE, GRID_SIZE))

# Fruit class
class Fruit:
    def __init__(self, obstacles):
        self.position = (0, 0)
        self.color = RED
        self.obstacles = obstacles
        self.randomize_position()

    def randomize_position(self):
        while True:
            new_position = (
                random.randint(0, (WIDTH // GRID_SIZE - 1)) * GRID_SIZE,
                random.randint(0, (HEIGHT // GRID_SIZE - 1)) * GRID_SIZE,
            )
            if all(new_position != (obs.x, obs.y) for obs in self.obstacles):
                break
        self.position = new_position

    def render(self, surface):
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

# Obstacle class
class Obstacle:
    def __init__(self, position, length):
        self.x, self.y = position
        self.color = GRAY
        self.length = length

    def render(self, surface):
        for i in range(self.length):
            pygame.draw.rect(surface, self.color, (self.x + i * GRID_SIZE, self.y, GRID_SIZE, GRID_SIZE))

class VerticalObstacle:
    def __init__(self, position, length):
        self.x, self.y = position
        self.color = GRAY
        self.length = length

    def render(self, surface):
        for i in range(self.length):
            pygame.draw.rect(surface, self.color, (self.x, self.y + i * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Scoring variables
score = 0
high_score = 0

# Display scoring
font = pygame.font.Font(None, 36)
score_text = font.render("Score: {}".format(score), True, WHITE)
high_score_text = font.render("High Score: {}".format(high_score), True, WHITE)

# Pause state
paused = False
pause_text = font.render("Paused", True, WHITE)

# Game over state
game_over = False
game_over_text = font.render("Game Over. Press 'R' to restart.", True, WHITE)

# Obstacles
obstacles = [Obstacle((100, 100), 4), Obstacle((200, 200), 6), Obstacle((300, 300), 8)]
vertical_obstacles = [VerticalObstacle((400, 100), 4), VerticalObstacle((500, 200), 6), VerticalObstacle((100, 300), 8)]
fruit = Fruit(obstacles)

# Main function
def main():
    global score, high_score, paused, game_over, obstacles, vertical_obstacles, fruit

    snake = Snake()
    level = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.last_direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.last_direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.last_direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.last_direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == pygame.K_r:
                    snake.reset()
                    level = 1
                    score = 0
                    game_over = False
                    fruit.randomize_position()  # Change fruit position when restarting
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused and not game_over:
            snake.last_direction = snake.direction
            snake.update(obstacles, vertical_obstacles)
            if snake.get_head_position() == fruit.position:
                snake.length += 1
                fruit.randomize_position()
                eat_sound.play()
                score += 10 * level
                if level < 5:
                    level += 1

            if score > high_score:
                high_score = score

            if (
                snake.get_head_position()[0] < 0
                or snake.get_head_position()[0] >= WIDTH
                or snake.get_head_position()[1] < 0
                or snake.get_head_position()[1] >= HEIGHT
            ):
                game_over = True

            for segment in snake.positions[1:]:
                if segment == snake.get_head_position():
                    game_over = True

            for obstacle in obstacles:
                if snake.get_head_position() == (obstacle.x, obstacle.y):
                    game_over = True

            for vertical_obstacle in vertical_obstacles:
                if snake.get_head_position() == (vertical_obstacle.x, vertical_obstacle.y):
                    game_over = True

        screen.fill(BLACK)
        snake.render(screen)
        fruit.render(screen)
        render_obstacles()
        render_vertical_obstacles()
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WIDTH - 200, 10))

        if paused:
            screen.blit(pause_text, (WIDTH // 2 - 50, HEIGHT // 2 - 20))

        if game_over:
            screen.blit(game_over_text, (WIDTH // 2 - 180, HEIGHT // 2 - 20))
            pygame.display.flip()
            game_over_sound.play()  # Play game over sound immediately
            time.sleep(2)  # Pause for 2 seconds after game over
            game_over = False
            snake.reset()
            fruit.randomize_position()  # Change fruit position when restarting
            score = 0  # Reset the score

        pygame.display.flip()
        clock.tick(FPS)

def render_obstacles():
    for obstacle in obstacles:
        obstacle.render(screen)

def render_vertical_obstacles():
    for vertical_obstacle in vertical_obstacles:
        vertical_obstacle.render(screen)

if __name__ == "__main__":
    main()
