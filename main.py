import pygame
import random
import numpy as np

class SnakeGame:
    def __init__(self, grid_size=500, cell_size=20):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.num_cells = grid_size // cell_size
        self.reset()

    def reset(self):
        # Initialize the grid
        self.grid = np.zeros((self.num_cells, self.num_cells), dtype=int)

        # Initialize the snake
        self.snake = [(5, 5), (5, 6), (5, 7)]  # Start with 3 segments
        for segment in self.snake:
            self.grid[segment] = 1  # Mark the snake's position

        # Place the first fruit
        self.place_fruit()

        # Set initial direction (moving left)
        self.direction = (0, -1)  # (row_change, col_change)

        return self.get_state()

    def place_fruit(self):
        while True:
            x, y = random.randint(0, self.num_cells - 1), random.randint(0, self.num_cells - 1)
            if self.grid[x, y] == 0:  # Place fruit in an empty cell
                self.grid[x, y] = 2
                self.fruit = (x, y)
                break

    def step(self):
        # Move the snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Wrap-around logic (snake re-enters from the other side)
        new_head = (
            new_head[0] % self.num_cells,  # Wrap around vertically
            new_head[1] % self.num_cells   # Wrap around horizontally
        )

        # Check for collisions with the snake's body
        if new_head in self.snake:
            return False  # Game over (self-collision)

        # Check if the snake eats a fruit
        if new_head == self.fruit:
            self.snake.insert(0, new_head)
            self.place_fruit()
        else:
            tail = self.snake.pop()  # Remove tail if no fruit eaten
            self.grid[tail] = 0

        # Update snake's position
        self.snake.insert(0, new_head)
        self.grid[new_head] = 1

        return True  # Game continues

    def change_direction(self, new_direction):
        # Prevent the snake from reversing directly
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def get_state(self):
        return self.grid

    def render(self, screen):
        screen.fill((0, 0, 0))  # Clear screen
        # Draw the snake
        for segment in self.snake:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                pygame.Rect(segment[1] * self.cell_size, segment[0] * self.cell_size, self.cell_size, self.cell_size)
            )
        # Draw the fruit
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            pygame.Rect(self.fruit[1] * self.cell_size, self.fruit[0] * self.cell_size, self.cell_size, self.cell_size)
        )
        pygame.display.flip()  # Update the display

    def show_score(self, screen):
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {len(self.snake)}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))


# Function to play manual game
def play_manual_game():
    pygame.init()
    grid_size = 500
    cell_size = 50
    game = SnakeGame(grid_size, cell_size)

    screen = pygame.display.set_mode((grid_size, grid_size))
    pygame.display.set_caption("Snake Game - Manual")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.change_direction((-1, 0))
                elif event.key == pygame.K_DOWN:
                    game.change_direction((1, 0))
                elif event.key == pygame.K_LEFT:
                    game.change_direction((0, -1))
                elif event.key == pygame.K_RIGHT:
                    game.change_direction((0, 1))

        # Step the game forward
        if not game.step():
            print(f"Score: {len(game.snake)}")
            print("Game Over!")
            running = False

        # Render the game
        game.render(screen)
        game.show_score(screen)
        clock.tick(50)  # Control game speed (10 frames per second)
    pygame.quit()

# Main function to run the game
def main():
    play_manual_game()

if __name__ == "__main__":
    main()
