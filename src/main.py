import os
import time
import math
import copy
import random
import logging


# setup logger for debugging (creates a logfile in ../log/ directory)
time_stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(level=logging.INFO, 
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
    if null_col == (cols - 1):      # on right-most edge, cannot move right
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
    
    # create an array which stores all the values of the board in order, ignoring the blank tile (0)
    for row in start_state:
        for value in row:
            if value != 0:
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

def states_are_equal(state1, state2):
    """
    Check if two states are equal
    """
    for row in range(3):
        for col in range(3):
            if state1[row][col] != state2[row][col]:
                return False
    return True


def state_in_list(state, state_list):
    """
    Check if a state exists in a list of states
    """
    for s in state_list:
        if states_are_equal(state, s):
            return True
    return False

def state_to_string(state):
    """
    Convert state to string for fast comparison
    
    Input: state - a 3x3 board
    Output: string representation
    Function: Converts board to string like "012345678"
    """
    result = ""
    for row in state:
        for tile in row:
            result += str(tile)
    return result


def solve_puzzle(start_state, heuristic_name):
    start_time = time.time()
    
    if states_are_equal(start_state, goal_state):
        return True, 0, 0, 0.0
    
    # open_list: dictionary {state_string: (state, g_cost, f_cost)}
    open_dict = {}
    closed_set = set()
    
    # calculate initial heuristic
    if heuristic_name == "manhattan":
        h_cost = manhattan(start_state)
    elif heuristic_name == "hamming":
        h_cost = hamming(start_state)
    else:
        return False, 0, 0, 0.0
    
    g_cost = 0
    f_cost = g_cost + h_cost
    start_string = state_to_string(start_state)
    open_dict[start_string] = (start_state, g_cost, f_cost)
    
    nodes_expanded = 0
    iteration = 0
    max_iterations = 50000
    
    while len(open_dict) > 0:
        iteration += 1
        
        if iteration > max_iterations:
            end_time = time.time()
            return False, iteration, nodes_expanded, (end_time - start_time)
        
        min_string = None
        min_f = float('inf')
        for state_string, (state, g, f) in open_dict.items():
            if f < min_f:
                min_f = f
                min_string = state_string
        
        # get and remove best node
        current_state, current_g, current_f = open_dict.pop(min_string)
        closed_set.add(min_string)
        nodes_expanded += 1
        
        # check goal
        if states_are_equal(current_state, goal_state):
            end_time = time.time()
            return True, iteration, nodes_expanded, (end_time - start_time)
        
        # generate neighbors
        next_states = neighbors(current_state)
        
        for next_state in next_states:
            next_string = state_to_string(next_state)
            
            if next_string in closed_set:
                continue
            
            new_g = current_g + 1
            
            if heuristic_name == "manhattan":
                h = manhattan(next_state)
            else:
                h = hamming(next_state)
            
            new_f = new_g + h
            
            # ⭐ if in open_dict, update if better
            if next_string in open_dict:
                old_g = open_dict[next_string][1]
                if new_g < old_g:
                    open_dict[next_string] = (next_state, new_g, new_f)
            else:
                # add to open_dict
                open_dict[next_string] = (next_state, new_g, new_f)
    
    end_time = time.time()
    return False, iteration, nodes_expanded, (end_time - start_time)

if __name__ == "__main__":
    log.info("Application start.")
    
    games_to_generate = 10
    
    # lists to store results
    results_manhattan = []
    results_hamming = []

    # generate and solve games
    for game_id in range(games_to_generate):
        log.info(f"=== Creating game with ID {game_id} ===")
        start_state = generateRandomSolvableBoard()

        # check if start_state is solvable, generate a new one if not
        while not is_solvable(start_state):
            log.debug(f"Generated unsolvable board, trying again...")
            start_state = generateRandomSolvableBoard()

        log.info("Found solvable board.")
        log.debug(f"Board: {start_state}")

        # solve with Manhattan heuristic
        log.info(f"Solving with MANHATTAN heuristic...")
        success_m, iter_m, nodes_m, time_m = solve_puzzle(start_state, "manhattan")
        results_manhattan.append({
            'game_id': game_id,
            'success': success_m,
            'iterations': iter_m,
            'nodes_expanded': nodes_m,
            'time': time_m
        })
        if success_m:
            log.info(f"Manhattan SUCCESS: nodes={nodes_m}, time={time_m:.4f}s")
        else:
            log.warning(f"Manhattan FAILED")

        # solve with Hamming heuristic (same board)
        log.info(f"Solving with HAMMING heuristic...")
        success_h, iter_h, nodes_h, time_h = solve_puzzle(start_state, "hamming")
        results_hamming.append({
            'game_id': game_id,
            'success': success_h,
            'iterations': iter_h,
            'nodes_expanded': nodes_h,
            'time': time_h
        })
        if success_h:
            log.info(f"Hamming SUCCESS: nodes={nodes_h}, time={time_h:.4f}s")
        else:
            log.warning(f"Hamming FAILED")
        
        print(f"Game {game_id+1}/{games_to_generate} completed")

    # calculate statistics for Manhattan
    print("\n" + "="*50)
    print("RESULTS - MANHATTAN HEURISTIC")
    print("="*50)
    
    solved_manhattan = [r for r in results_manhattan if r['success']]
    if len(solved_manhattan) > 0:
        avg_nodes_m = sum(r['nodes_expanded'] for r in solved_manhattan) / len(solved_manhattan)
        avg_time_m = sum(r['time'] for r in solved_manhattan) / len(solved_manhattan)
        
        # calculate standard deviation
        variance_nodes_m = sum((r['nodes_expanded'] - avg_nodes_m)**2 for r in solved_manhattan) / len(solved_manhattan)
        std_nodes_m = math.sqrt(variance_nodes_m)
        
        variance_time_m = sum((r['time'] - avg_time_m)**2 for r in solved_manhattan) / len(solved_manhattan)
        std_time_m = math.sqrt(variance_time_m)
        
        print(f"Solved: {len(solved_manhattan)}/{games_to_generate}")
        print(f"Average nodes expanded: {avg_nodes_m:.2f} ± {std_nodes_m:.2f}")
        print(f"Average execution time: {avg_time_m:.4f}s ± {std_time_m:.4f}s")
    else:
        print("No games solved!")

    # calculate statistics for Hamming
    print("\n" + "="*50)
    print("RESULTS - HAMMING HEURISTIC")
    print("="*50)
    
    solved_hamming = [r for r in results_hamming if r['success']]
    if len(solved_hamming) > 0:
        avg_nodes_h = sum(r['nodes_expanded'] for r in solved_hamming) / len(solved_hamming)
        avg_time_h = sum(r['time'] for r in solved_hamming) / len(solved_hamming)
        
        # calculate standard deviation
        variance_nodes_h = sum((r['nodes_expanded'] - avg_nodes_h)**2 for r in solved_hamming) / len(solved_hamming)
        std_nodes_h = math.sqrt(variance_nodes_h)
        
        variance_time_h = sum((r['time'] - avg_time_h)**2 for r in solved_hamming) / len(solved_hamming)
        std_time_h = math.sqrt(variance_time_h)
        
        print(f"Solved: {len(solved_hamming)}/{games_to_generate}")
        print(f"Average nodes expanded: {avg_nodes_h:.2f} ± {std_nodes_h:.2f}")
        print(f"Average execution time: {avg_time_h:.4f}s ± {std_time_h:.4f}s")
    else:
        print("No games solved!")

    print("\n" + "="*50)
    log.info("Application end. (exit: 0, program finished)")
    exit(0)
