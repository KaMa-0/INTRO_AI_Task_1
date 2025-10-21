import os
import time
import math
import random
import logging


# setup logger for debugging (creates a logfile in ./log/ directory)
time_stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    filename=os.path.join('log', f'{time_stamp}_logfile.log'))
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
    return None


# returns possible states for a given "current_state"
def neighbors(current_state):
    return None


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

    log.info("Application end. (exit: 0, program finished)")
    exit(0)
