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
    return None


# calculate manhattan distance of a given "current_state"
def manhattan(current_state):
    return None


# returns possible states for a given "current_state"
def neighbors(current_state):
    rows = len(current_state)
    columns = len(current_state[0])
    null_row = None
    null_col = None
    possible_moves = ['u', 'd', 'r', 'l']   # up, down, right, left
    possible_states = []

    # get the position/coordinates of the "null" ( 0 ) element inside the board
    for row in range(rows):
        for column in range(columns):
            if current_state[row][column] == 0:
                null_row = row
                null_col = column
                log.debug(f"Found null at board position:")
                log.debug(f"[{null_row}:{null_col}]")

    # check where "null" ( 0 ) element can move to in next iteration
    if null_row == (rows - 1):      # on bottom-most edge, cannot move down
        possible_moves.remove('d')
    if null_row == 0:               # on top-most edge, cannot move up
        possible_moves.remove('u')
    if null_col == (columns - 1):   # on right-most edge, cannot move right
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
def calculateCosts(possible_states):
    return None


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
        for column in range(len(new_board[row])):
            new_board[row][column] = possible_values[next_value]
            next_value += 1

    return new_board


if __name__ == "__main__":
    log.info("Application start.")
    start_state = generateRandomSolvableBoard();

    # check if start_state is solvable, generate a new one in case it isn't
    while not is_solvable(start_state):
        log.debug(f"Generated unsolvable board : {start_state}")
        start_state = generateRandomSolvableBoard()

    log.info("Found solvable board.")
    log.debug(f"Board: {start_state}")

    states = neighbors(start_state) 
    for state in states:
        log.debug(f"\n-- possible state --\n{state[0]}\n{state[1]}\n{state[2]}")

    log.info("Application end. (exit: 0, program finished)")
    exit(0)
