import numpy as np
import random
import pygame
import pickle
import matplotlib.pyplot as plt  # Add this import for plotting


class QLearningSnake:
    def __init__(self, grid_size, cell_size, alpha, gamma, epsilon):
        self.num_cells = grid_size // cell_size
        self.cell_size = cell_size
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = {}  # Initialize Q-table as a dictionary
        self.reset()

    def reset(self):
        self.snake = [(5, 5), (5, 6), (5, 7)]
        self.direction = (0, -1)  # Initial direction
        self.place_fruit()
        self.steps = 0
        return self.get_state()

    def get_state(self):
        head_x, head_y = self.snake[0]
        rel_fruit_x = self.fruit[0] - head_x
        rel_fruit_y = self.fruit[1] - head_y
        return (rel_fruit_x, rel_fruit_y, self.direction)

    def place_fruit(self):
        while True:
            x, y = random.randint(0, self.num_cells - 1), random.randint(0, self.num_cells - 1)
            if (x, y) not in self.snake:
                self.fruit = (x, y)
                break

    def step(self, action):
        self.direction = action
        head_x, head_y = self.snake[0]
        new_head = (head_x + action[0], head_y + action[1])

        # Wrap-around logic
        new_head = (
            new_head[0] % self.num_cells,
            new_head[1] % self.num_cells
        )

        if new_head in self.snake:
            return -10, True  # Collision penalty

        reward = 1 if new_head == self.fruit else -0.01
        if new_head == self.fruit:
            self.snake.insert(0, new_head)
            self.place_fruit()
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

        return reward, False

    def choose_action(self, state):
        actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(actions)  # Explore
        q_values = [self.q_table.get((state, a), 0) for a in actions]
        max_q_value = max(q_values)
        best_actions = [a for a, q in zip(actions, q_values) if q == max_q_value]
        return random.choice(best_actions)  # Exploit with tie-breaking

    def update_q_table(self, state, action, reward, next_state):
        actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        max_future_q = max([self.q_table.get((next_state, a), 0) for a in actions], default=0)
        current_q = self.q_table.get((state, action), 0)
        new_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_future_q)
        self.q_table[(state, action)] = new_q

    def train(self, episodes, max_steps_per_episode=200):
        pygame.init()
        total_rewards = []
        avg_rewards = []  # List to store average rewards

        for episode in range(episodes):
            state = self.reset()
            done = False
            total_reward = 0
            steps_taken = 0

            while not done and steps_taken < max_steps_per_episode:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

                action = self.choose_action(state)
                reward, done = self.step(action)
                next_state = self.get_state()
                self.update_q_table(state, action, reward, next_state)
                state = next_state
                total_reward += reward
                steps_taken += 1

            total_rewards.append(total_reward)
            self.epsilon = max(0.01, self.epsilon * 0.995)

            if episode % 100 == 0:
                avg_reward = np.mean(total_rewards[-100:])
                avg_rewards.append(avg_reward)  # Store average reward
                print(f"Episode {episode}, Avg Reward: {avg_reward:.2f}, Epsilon: {self.epsilon:.4f}")

        pygame.quit()

        # Plot the average rewards
        plt.plot(avg_rewards)
        plt.xlabel('Episode (x100)')
        plt.ylabel('Average Reward')
        plt.title('Episode vs Average Reward')
        plt.show()

        return self.q_table


if __name__ == "__main__":
    grid_size = 500
    cell_size = 50
    alpha = 0.1
    gamma = 0.9
    epsilon = 1.0

    snake_game = QLearningSnake(grid_size, cell_size, alpha, gamma, epsilon)
    trained_q_table = snake_game.train(episodes=50000)

    with open('q_table.pkl', 'wb') as f:
        pickle.dump(trained_q_table, f)
