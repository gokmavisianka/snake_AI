import pygame
import numpy as np
from datetime import datetime
import random


pygame.init()

FPS = 5

# possible_moves = direction[previous_move]
direction = {"right": ('right', 'down', 'up'),
             "left" : ('left', 'down', 'up'),
             "down" : ('right', 'left', 'down'),
             "up"   : ('right', 'left', 'up'),
             None   : ('right', 'left', 'down', 'up')}

opposite = {"right": "left",
            "left" : "right",
            "down" : "up",
            "up"   : "down",
            None: None}

forbidden_index = {"right": 0,
                   "left" : 1,
                   "down" : 2,
                   "up"   : 3,
                   None: 4}

# row += velocity[action]['x']
# column += velocity[action]['y']
velocity = {"right": {'x': 1, 'y': 0},
            "left" : {'x': -1, 'y': 0},
            "down" : {'x': 0, 'y': 1},
            "up"   : {'x': 0, 'y': -1}}

# 0: empty, 1: wall, 2: apple, 3: snake.
color = {0: (0, 200, 100),
         1: (0, 0, 0),
         2: (200, 0, 0),
         3: (35, 35, 35),
         4: (15, 15, 15)}


def situation():
    _tuple_ = (apple.row < snake.row,
               apple.row == snake.row,
               apple.row > snake.row,
               apple.column < snake.column,
               apple.column == snake.column,
               apple.column > snake.column)
    _dictionary_ = {(1, 0, 0, 1, 0, 0): 'top-left',
                    (1, 0, 0, 0, 1, 0): 'left',
                    (1, 0, 0, 0, 0, 1): 'bottom-left',
                    (0, 1, 0, 1, 0, 0): 'top',
                    (0, 1, 0, 0, 1, 0): None,
                    (0, 1, 0, 0, 0, 1): 'bottom',
                    (0, 0, 1, 1, 0, 0): 'top-right',
                    (0, 0, 1, 0, 1, 0): 'right',
                    (0, 0, 1, 0, 0, 1): 'bottom-right'}
    return _dictionary_[_tuple_]

def condition():
    _tuple_ = (apple.row < snake.row,
               apple.row == snake.row,
               apple.row > snake.row,
               apple.column < snake.column,
               apple.column == snake.column,
               apple.column > snake.column)
    _dictionary_ = {(1, 0, 0, 1, 0, 0): ('up', 'left'),
                    (1, 0, 0, 0, 1, 0): ('left'),
                    (1, 0, 0, 0, 0, 1): ('bottom', 'left'),
                    (0, 1, 0, 1, 0, 0): ('top'),
                    (0, 1, 0, 0, 1, 0): (None),
                    (0, 1, 0, 0, 0, 1): ('bottom'),
                    (0, 0, 1, 1, 0, 0): ('up', 'right'),
                    (0, 0, 1, 0, 1, 0): ('right'),
                    (0, 0, 1, 0, 0, 1): ('bottom', 'right')}
    return _dictionary_[_tuple_]

def check():
    row, column = snake.head
    _tuple_ = (map.matrix[row + 1, column] in (1, 3),
               map.matrix[row - 1, column] in (1, 3),
               map.matrix[row, column + 1] in (1, 3),
               map.matrix[row, column - 1] in (1, 3))
    return _tuple_


class Cell:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Text:
    def __init__(self, base_string, function, color=(255, 0, 0)):
        # base_string can be "FPS: " or "Score: " to represent the remaining part.
        self.base_string = base_string
        self.color = color
        # function is used to get the remaining part (It can be fps value or score etc.) of the string.
        # So {base_string + remaining} will be shown on the screen.
        self.function = function
        # Size of the font can be changed.
        self.font = pygame.font.SysFont("Helvetica", 32)

    def show(self, display, position, string=None):
        # If a string is given, use that. Otherwise, use the base_string and add the remaining part to it.
        if string is None:
            string = self.base_string
            remaining = self.function()
            # Check if the type of the remaining part is str. If not, Convert it to the str type before merging strings.
            if type(remaining) is str:
                string += remaining
            else:
                string += str(remaining)
        text = self.font.render(string, True, self.color)
        display.blit(text, position)


class Screen:
    def __init__(self, background_color=(100, 100, 100), resolution=(1000, 750)):
        self.background_color = background_color
        self.width, self.height = resolution
        self.display = pygame.display.set_mode(resolution)
        self.FPS = self.FPS()

    # This functions is used to convert row and column values to x and y values. Or vice versa...
    def convert_position(self, value: int, axis: str):
        if axis == "x":
            result = value * map.cell.width
        elif axis == "y":
            result = value * map.cell.height
        else:
            raise ValueError(f"axis have to be 'x' or 'y' but {axis} is given instead.")
        return result
    
    def draw(self):
        for row in range(map.width):
            for column in range(map.height):
                value = map.matrix[row, column]
                x = self.convert_position(row, axis='x')
                y = self.convert_position(column, axis='y')
                width = map.cell.width
                height = map.cell.height
                geometry = (x, y, width, height)
                pygame.draw.rect(self.display, color[value], geometry)

    def fill(self, color=None):
        if color is None:
            color = self.background_color
        # fill the screen with specific color.
        self.display.fill(color)

    @staticmethod
    def update():
        # Update the whole window.
        pygame.display.flip()

    class FPS:
        def __init__(self):
            self.clock = pygame.time.Clock()
            self.text = Text(base_string="FPS: ", function=self.get)

        def set(self, value):
            self.clock.tick(value)

        def get(self):
            return round(self.clock.get_fps())  # clock.get_fps() returns a float.


class Map:
    def __init__(self, size):
        self.width, self.height = size
        cell_width = screen.width // self.width
        cell_height = screen.height // self.height
        self.cell = Cell(cell_width, cell_height)
        self.matrix = None
        self.create()

    def create(self):
        self.matrix = np.ones((self.width, self.height), dtype=int)
        self.matrix[1: (self.width - 1), 1: (self.height - 1)] = 0

    def random_position(self):
        try:
            empty_cells = np.where(self.matrix == 0)
            index = random.randint(0, len(empty_cells[0]) - 1)
        except ValueError:
            index = 0
        finally:
            cell = empty_cells[0][index], empty_cells[1][index]
        return cell


class Apple:
    def __init__(self):
        self.row, self.column = None, None

    def create(self):
        self.row, self.column = map.random_position()
        map.matrix[self.row, self.column] = 2


class Snake:
    def __init__(self):
        self.row, self.column = None, None
        self.length = 1
        self.tail = []
        self.head = (1, 1)
        self.reward = 0

    def create(self):
        self.row, self.column = map.random_position()
        self.tail.append((self.row, self.column))
        map.matrix[self.row, self.column] = 3
        self.head = (self.row, self.column)

    def reset(self):
        map.matrix[map.matrix == 2] = 0
        map.matrix[map.matrix == 3] = 0
        map.matrix[map.matrix == 4] = 0
        score.value = 0
        self.reward = -100
        self.length = 1
        self.tail = []
        self.create()
        apple.create()

    def move(self, action):
        Q.actions = direction[action]
        if action in condition():
            self.reward = 10
        else:
            self.reward = -10      
        self.row += velocity[action]['x']
        self.column += velocity[action]['y']
        value = map.matrix[self.row, self.column]
        if value == 2:
            self.reward = 100
            self.length += 1
            score.add(1)
            if self.length == (map.width - 2) * (map.height - 2):
                print("Successful!")
                self.reset()
            else:
                apple.create()
        elif value == 1 or (value == 3 and (self.row, self.column) != self.tail[0]):
            self.reset()
        self.tail.append((self.row, self.column))
        if len(self.tail) > self.length:
            self.tail.pop(0)
        map.matrix[map.matrix == 3] = 0
        map.matrix[map.matrix == 4] = 0
        for cell in self.tail:
            row, column = cell
            map.matrix[row, column] = 3
        row, column = self.tail[-1]
        map.matrix[row, column] = 4
        self.head = (row, column)


class Score:
    def __init__(self):
        self.text = Text(base_string="Score: ", function=self.get)
        self.max_value = 0
        self.value = 0

    def add(self, value):
        self.value += value
        if self.value > self.max_value:
            self.max_value = self.value
            print("New Best:", self.max_value)

    def get(self):
        return self.value


class QLearning:
    def __init__(self, actions, learning_rate=0.5, discount_factor=0.9, exploration_rate=0.9, exploration_decay_rate=0.9):
        self.q_table = {}
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay_rate = exploration_decay_rate
        
    def get_q_value(self, state, action):
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0
        return self.q_table[(state, action)]
    
    def update_q_value(self, state, action, reward, next_state):
        current_q_value = self.get_q_value(state, action)
        max_next_q_value = max([self.get_q_value(next_state, a) for a in self.actions])
        new_q_value = (1 - self.learning_rate) * current_q_value + self.learning_rate * (reward + self.discount_factor * max_next_q_value)
        self.q_table[(state, action)] = new_q_value
        
    def choose_action(self, state):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.actions)
        else:
            q_values = [self.get_q_value(state, a) for a in self.actions]
            max_q_value = max(q_values)
            if q_values.count(max_q_value) > 1:
                best_actions = [i for i in range(len(self.actions)) if q_values[i] == max_q_value]
                return self.actions[random.choice(best_actions)]
            else:
                return self.actions[np.argmax(q_values)]
        
    def update_exploration_rate(self):
        self.exploration_rate *= self.exploration_decay_rate
    

class Keyboard:
    @staticmethod
    def update():
        global FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # Press 'Q' to quit.
                if event.key == pygame.K_q:
                    print(Q.q_table)
                    pygame.quit()
                    quit()
                if event.key == pygame.K_f:
                    if FPS == 5:
                        FPS = 999999
                    else:
                        FPS = 5
                if event.key == pygame.K_RIGHT:
                    snake.move(action="right")
                elif event.key == pygame.K_LEFT:
                    snake.move(action="left")
                elif event.key == pygame.K_DOWN:
                    if Q.exploration_rate > 0.1:
                        Q.exploration_rate = round(Q.exploration_rate - 0.1, 1)
                    else:
                        Q.exploration_rate = 0.0
                    print(f"--- Exploration rate: {Q.exploration_rate}")
                elif event.key == pygame.K_UP:
                    if Q.exploration_rate < 0.9:
                        Q.exploration_rate = round(Q.exploration_rate + 0.1, 1)
                    else:
                        Q.exploration_rate = 1.0
                    print(f"+++ Exploration rate: {Q.exploration_rate}")


screen = Screen(resolution=(720, 600))
keyboard = Keyboard()
map = Map(size=(18, 15))
apple = Apple()
snake = Snake()
apple.create()
snake.create()
score = Score()
Q = QLearning(actions=("right", "left", "down", "up"))
start = datetime.now()
n = 0

while True:
    keyboard.update()
    # _state_ = tuple(tuple(row) for row in (map.matrix))
    # _state_ = (snake.head, check(), situation())
    _state_ = (check(), situation())
    _action_ = Q.choose_action(_state_)
    snake.move(_action_)
    _reward_ = snake.reward
    _new_state_ = (check(), situation())
    Q.update_q_value(_state_, _action_, _reward_, _new_state_)
    screen.fill()
    screen.draw()
    screen.FPS.text.show(screen.display, position=(0, 0))
    score.text.show(screen.display, position=(200, 0))
    if FPS == 999999:
        if n > 250:
            screen.update()
            n = 0
    else:
        screen.update()
    n += 1
    screen.FPS.set(FPS)
    end = datetime.now()
    difference = end - start
    if difference.total_seconds() > 300:
        start = end
        if Q.exploration_rate > 0.2:
            Q.exploration_rate = round(Q.exploration_rate - 0.1, 1)
        else:
            Q.exploration_rate = 0.0
        print(f"Exploration rate: {Q.exploration_rate}")
            
