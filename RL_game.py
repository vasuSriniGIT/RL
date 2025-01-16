import pygame
import random
import pickle

class RLGame:
    def __init__(self, grid_size, cell_size, q_table):
        self.num_cells = grid_size // cell_size
        self.cell_size = cell_size
        self.q_table = q_table  # Use the trained Q-table
        self.reset()

    def reset(self):
        # Initialize the snake's position and place the first fruit
        self.snake = [(5, 5), (5, 6), (5, 7)]
        self.direction = (0, -1)  # Initial direction (moving up)
        self.place_fruit()
        self.steps = 0
        return self.get_state()

    def get_state(self):
        # State includes relative fruit position and current direction
        head_x, head_y = self.snake[0]
        rel_fruit_x = self.fruit[0] - head_x
        rel_fruit_y = self.fruit[1] - head_y
        return (rel_fruit_x, rel_fruit_y, self.direction)

    def place_fruit(self):
        # Place fruit in a random position
        while True:
            x, y = random.randint(0, self.num_cells - 1), random.randint(0, self.num_cells - 1)
            if (x, y) not in self.snake:  # Make sure fruit is not on the snake
                self.fruit = (x, y)
                break

    def step(self, action):
        # Prevent reversing direction
        if action == (-self.direction[0], -self.direction[1]):
            action = self.direction  # Ignore invalid action

        # Update direction
        self.direction = action
        head_x, head_y = self.snake[0]
        new_head = (head_x + action[0], head_y + action[1])

        # Wrap-around logic (snake re-enters from the other side)
        new_head = (
            new_head[0] % self.num_cells,
            new_head[1] % self.num_cells
        )

        # Check for collisions with the snake's body
        if new_head in self.snake:
            print("Collision detected! Game over.")
            print(f"Score: {len(self.snake)}")
            return -10, True  # Negative reward for collision with own body

        # Check for fruit
        reward = 1 if new_head == self.fruit else -0.01  # Reward for eating fruit, penalty for not
        if new_head == self.fruit:
            self.snake.insert(0, new_head)
            self.place_fruit()
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

        return reward, False

    def choose_action(self, state):
        # Choose the best action using the trained Q-table (exploitation only)
        actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        q_values = [self.q_table.get((state, a), 0) for a in actions]
        max_q_value = max(q_values)
        best_actions = [a for a, q in zip(actions, q_values) if q == max_q_value]
        return random.choice(best_actions)  # Break ties randomly

    def play(self):
        pygame.init()
        screen = pygame.display.set_mode((self.num_cells * self.cell_size, self.num_cells * self.cell_size))
        pygame.display.set_caption("Snake Game - RL Agent")
        clock = pygame.time.Clock()

        running = True
        while running:
            state = self.reset()
            done = False
            while not done:
                # Handle events like pressing ESC to exit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        done = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:  # Escape to stop the game
                            running = False
                            done = True

                # Get the current state
                state = self.get_state()

                # Choose action using the trained Q-table
                action = self.choose_action(state)

                # Step the game forward
                reward, done = self.step(action)

                # Render the game
                self.render(screen)

                # Show the score (snake length) at the top
                self.show_score(screen)

                clock.tick(100)  # Control game speed (10 frames per second)

        pygame.quit()

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


# Function to load the Q-table from the .pkl file
def load_q_table(filename="q_table.pkl"):
    try:
        with open(filename, "rb") as f:
            q_table = pickle.load(f)
        print("Q-table loaded successfully.")
        return q_table
    except Exception as e:
        print(f"Error loading Q-table: {e}")
        return None


# Main function to run the RL game
def main():
    q_table = load_q_table("q_table.pkl")
    if q_table:
        game = RLGame(500, 50, q_table)
        game.play()
    else:
        print("Failed to load Q-table, exiting...")


if __name__ == "__main__":
    main()
