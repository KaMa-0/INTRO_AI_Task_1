import os
import time
import math
import copy
import random
import logging


# setup logger for debugging (creates a logfile in ../log/ directory)
time_stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    filename=os.path.abspath(
                        os.path.join(os.path.dirname(__file__),
                        os.pardir, 'log', f'{time_stamp}_logfile.log')))
log = logging.getLogger(__name__)



# definition of the goal state, as defined in task slides on Moodle
goal_state = [[ 0, 1, 2 ],
              [ 3, 4, 5 ],
              [ 6, 7, 8 ]]


# calculate hamming distance of a given "current_state"
def hamming(current_state):
    misplaced_count = 0
    for row in range(3):
        for col in range(3):
            current_tile = current_state[row][col]
            goal_tile = goal_state[row][col]
            if current_tile == 0:
                continue
            if current_tile != goal_tile:
                misplaced_count += 1
    return misplaced_count



# calculate manhattan distance of a given "current_state"
def manhattan(current_state):
    total_distance = 0
    for row in range(3):
        for col in range(3):
            current_tile = current_state[row][col]
            if current_tile == 0:
                continue  # Skip the blank tile
            # calculate the goal position of the current tile
            goal_row = current_tile // 3
            goal_col = current_tile % 3
            # add the Manhattan distance for this tile
            total_distance += abs(row - goal_row) + abs(col - goal_col)
    return total_distance


# returns possible states for a given "current_state"
def neighbors(current_state):
    rows = len(current_state)
    cols = len(current_state[0])
    null_row = None
    null_col = None
    possible_moves = ['u', 'd', 'r', 'l']   # up, down, right, left
    possible_states = []

    # get the position/coordinates of the "null" ( 0 ) element inside the board
    for row in range(rows):
        for col in range(cols):
            if current_state[row][col] == 0:
                null_row = row
                null_col = col
                log.debug(f"Found null at board position:")
                log.debug(f"[{null_row}:{null_col}]")

    # check where "null" ( 0 ) element can move to in next iteration
    if null_row == (rows - 1):      # on bottom-most edge, cannot move down
        possible_moves.remove('d')
    if null_row == 0:               # on top-most edge, cannot move up
        possible_moves.remove('u')
    if null_col == (cols - 1):   # on right-most edge, cannot move right
        possible_moves.remove('r')
    if null_col == 0:               # on left-most edge, cannot move leftI
        possible_moves.remove('l')

    log.debug("Available moves: ")
    log.debug(possible_moves)

    # create a list of possible states, given the possible moves
    for direction in possible_moves:
        new_state = copy.deepcopy(current_state)
        swap_row = null_row
        swap_col = null_col
        if direction == 'd':
            swap_row = null_row + 1
        elif direction == 'u':
            swap_row = null_row - 1
        elif direction == 'r':
            swap_col = null_col + 1
        elif direction == 'l':
            swap_col = null_col - 1
        new_state[null_row][null_col] = new_state[swap_row][swap_col]
        new_state[swap_row][swap_col] = 0
        possible_states.append(new_state)

    return possible_states


# provide list with states, calculates cost for each state f(s) = g(s) + h(s)
def calculateCosts(possible_states, heuristic, g_cost=0):
    state_costs = []
    for state in possible_states:
        if heuristic == "manhattan":
            h_cost = manhattan(state)
        elif heuristic == "hamming":
            h_cost = hamming(state)
        else:
            log.critical("Selected heuristic for 'calculateCosts' no valid!")
            exit(11)
        f_cost = g_cost + h_cost   # f(s) = g(s) + h(s)
        state_costs.append((state, f_cost))
    return state_costs


# checks if state is solvable or not
def is_solvable(start_state):
    inv_count = 0
    value_array = []
    
    # create an array which stores all the values of the board in order
    for row in start_state:
        for value in row:
            value_array.append(value)

    # sum all the inversions of each element in the ordered array of values
    n = len(value_array)
    for i in range(n):
        for j in range(i + 1, n):
            if value_array[i] > value_array[j]:
                inv_count += 1
     
    # give back the solvability depending on if number of inversions even/odd
    return (inv_count % 2 == 0)


# generate a random start_state for the board
def generateRandomSolvableBoard():
    possible_values = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    next_value = 0
    new_board = [[9, 9, 9], [9, 9, 9], [9, 9, 9]]
    
    # create a randomly shuffled list based on all possible values (for 8puzzle)
    random.shuffle(possible_values)

    # fill the new_board with the next (random) value from the shuffled list
    for row in range(len(new_board)):
        for col in range(len(new_board[row])):
            new_board[row][col] = possible_values[next_value]
            next_value += 1

    return new_board


if __name__ == "__main__":
    log.info("Application start.")

    games_to_generate = 100

    for game_id in range(games_to_generate):
        log.info(f"Creating game with ID {game_id}")
        start_state = generateRandomSolvableBoard();

        # check if start_state is solvable, generate a new one in case it isn't
        while not is_solvable(start_state):
            log.debug(f"Generated unsolvable board : {start_state}")
            start_state = generateRandomSolvableBoard()

        log.info("Found solvable board.")
        log.debug(f"Board: {start_state}")

        hamming_distance = hamming(start_state)
        log.info(f"Hamming distance of generated board: {hamming_distance}")
        log.debug(f"Goal state: {goal_state}")

        states = neighbors(start_state) 
        for state in states:
            log.debug(f"\n-- possible state --\n{state[0]}\n{state[1]}\n{state[2]}")

        log.info(f"Game ({game_id+1} has completed.)") 

    log.info("Application end. (exit: 0, program finished)")
    exit(0)
