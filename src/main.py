import os
import time
import math
import copy
import random
import logging
import heapq


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
    """
    Calculate Hamming distance heuristic.
    
    Input: current_state - 3x3 board (list of lists)
    Output: misplaced_count - number of misplaced tiles (integer)
    Function: Counts how many tiles are not in their goal position (blank excluded)
    """
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
    """
    Calculate Manhattan distance heuristic.
    
    Input: current_state - 3x3 board (list of lists)
    Output: total_distance - sum of Manhattan distances (integer)
    Function: Calculates sum of distances of each tile from its goal position
    """
    total_distance = 0
    for row in range(3):
        for col in range(3):
            current_tile = current_state[row][col]
            if current_tile == 0:
                continue
            # Calculate goal position
            goal_row = current_tile // 3
            goal_col = current_tile % 3
            # Add Manhattan distance
            total_distance += abs(row - goal_row) + abs(col - goal_col)
    return total_distance


# returns possible states for a given "current_state"
def neighbors(current_state):
    """
    Generate all possible next states.
    
    Input: current_state - 3x3 board
    Output: possible_states - list of all possible next states
    Function: Moves blank tile (0) in all valid directions
    """
    rows = len(current_state)
    cols = len(current_state[0])
    blank_row = None
    blank_col = None
    possible_moves = ['u', 'd', 'r', 'l']
    possible_states = []

    # Find blank tile (0) position
    for row in range(rows):
        for col in range(cols):
            if current_state[row][col] == 0:
                blank_row = row
                blank_col = col

    # Check valid moves
    if blank_row == (rows - 1):
        possible_moves.remove('d')
    if blank_row == 0:
        possible_moves.remove('u')
    if blank_col == (cols - 1):
        possible_moves.remove('r')
    if blank_col == 0:
        possible_moves.remove('l')

    # Create new states for each valid move
    for direction in possible_moves:
        new_state = copy.deepcopy(current_state)
        swap_row = blank_row
        swap_col = blank_col
        
        if direction == 'd':
            swap_row = blank_row + 1
        elif direction == 'u':
            swap_row = blank_row - 1
        elif direction == 'r':
            swap_col = blank_col + 1
        elif direction == 'l':
            swap_col = blank_col - 1
        
        # Swap blank with target tile
        new_state[blank_row][blank_col] = new_state[swap_row][swap_col]
        new_state[swap_row][swap_col] = 0
        possible_states.append(new_state)

    return possible_states


def calculateCosts(possible_states, heuristic, g_cost):
    """
    Calculate f-cost for each state.
    
    Input: possible_states - list of states
           heuristic - "manhattan" or "hamming"
           g_cost - current path cost
    Output: state_costs - list of (state, f_cost) tuples
    Function: Calculates f(s) = g(s) + h(s) for each state
    """
    state_costs = []
    for state in possible_states:
        if heuristic == "manhattan":
            h_cost = manhattan(state)
        elif heuristic == "hamming":
            h_cost = hamming(state)
        else:
            log.critical("Invalid heuristic for calculateCosts!")
            exit(11)
        f_cost = g_cost + h_cost
        state_costs.append((state, f_cost))
    return state_costs


def state_to_string(state):
    """
    Convert state to string for comparison.
    
    Input: state - 3x3 board
    Output: string representation (e.g., "012345678")
    Function: Converts board to string for fast comparison
    """
    result = ""
    for row in state:
        for tile in row:
            result += str(tile)
    return result


def is_solvable(start_state):
    """
    Check if puzzle is solvable.
    
    Input: start_state - 3x3 board
    Output: True if solvable, False otherwise
    Function: Counts inversions to determine solvability
    """
    inv_count = 0
    value_array = []
    
    # Create array without blank tile
    for row in start_state:
        for value in row:
            if value != 0:
                value_array.append(value)

    # Count inversions
    n = len(value_array)
    for i in range(n):
        for j in range(i + 1, n):
            if value_array[i] > value_array[j]:
                inv_count += 1
     
    # Solvable if inversions are even
    return (inv_count % 2 == 0)


def generateRandomSolvableBoard():
    """
    Generate random solvable board.
    
    Input: None
    Output: new_board - random 3x3 board
    Function: Creates random board configuration
    """
    while True:
        possible_values = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        next_value = 0
        new_board = [[9, 9, 9], [9, 9, 9], [9, 9, 9]]
        
        # Shuffle values
        random.shuffle(possible_values)

        # Fill board
        for row in range(len(new_board)):
            for col in range(len(new_board[row])):
                new_board[row][col] = possible_values[next_value]
                next_value += 1
        if is_solvable(new_board):
            break

    return new_board


def solve_puzzle(start_state, heuristic_name):
    """
    Solve 8-puzzle using A* algorithm with heapq.
    Includes parent mapping for optional path reconstruction.
    """
    start_time = time.time()
    start_string = state_to_string(start_state)
    goal_string = state_to_string(goal_state)

    # Check if already at goal
    if start_string == goal_string:
        return True, 0, 0, 0.0

    # Initialize
    g_cost = 0
    if heuristic_name == "manhattan":
        h_cost = manhattan(start_state)
    elif heuristic_name == "hamming":
        h_cost = hamming(start_state)
    else:
        return False, 0, 0, 0.0

    f_cost = g_cost + h_cost
    open_heap = []
    heapq.heappush(open_heap, (f_cost, 0, start_string, start_state, g_cost))

    closed_set = set()
    parent_map = {start_string: None}   # store each state's parent
    state_map = {start_string: start_state}  # keep full board to reconstruct later

    nodes_expanded = 0
    iterations = 0
    counter = 1

    while open_heap:
        iterations += 1
        if iterations > 1_000_000:
            return False, iterations, nodes_expanded, time.time() - start_time

        current_f, _, current_string, current_state, current_g = heapq.heappop(open_heap)
        if current_string in closed_set:
            continue

        closed_set.add(current_string)
        nodes_expanded += 1

        if current_string == goal_string:
            elapsed = time.time() - start_time

            # reconstruct path using parent_map (for optional debugging / printing)
            path = []
            s = current_string
            while s is not None:
                path.append(s)
                s = parent_map[s]
            path.reverse()

            # print solution length (not required)
            log.info(f"Solution length: {len(path)-1} moves")

            return True, iterations, nodes_expanded, elapsed

        for neighbor_state in neighbors(current_state):
            neighbor_string = state_to_string(neighbor_state)
            if neighbor_string in closed_set:
                continue

            new_g = current_g + 1
            if heuristic_name == "manhattan":
                h = manhattan(neighbor_state)
            else:
                h = hamming(neighbor_state)
            new_f = new_g + h

            if neighbor_string not in parent_map:
                parent_map[neighbor_string] = current_string
                state_map[neighbor_string] = neighbor_state

            heapq.heappush(open_heap, (new_f, counter, neighbor_string, neighbor_state, new_g))
            counter += 1

    return False, iterations, nodes_expanded, time.time() - start_time


def run_benchmark(games_to_generate=100, heuristics=["manhattan", "hamming"]):
    # Store results
    results_manhattan = []
    results_hamming = []

    # Generate and solve games
    for game_id in range(games_to_generate):
        log.info(f"=== Creating game with ID {game_id} ===")
        start_state = generateRandomSolvableBoard()

        # Check solvability
        while not is_solvable(start_state):
            log.debug(f"Generated unsolvable board, trying again...")
            start_state = generateRandomSolvableBoard()

        log.info("Found solvable board.")
        log.debug(f"Board: {start_state}")

        # Solve with Manhattan heuristic
        if "manhattan" in heuristics:
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
                log.warning(f"Unable to find goal_state, given: {start_state}")

            print(f"Game {game_id+1}/{games_to_generate} completed. (manhattan)")

        # Solve with Hamming heuristic
        if "hamming" in heuristics:
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
                log.warning(f"Unable to find goal_state, given: {start_state}")
        
            print(f"Game {game_id+1}/{games_to_generate} completed. (hamming)")

    if "manhattan" in heuristics:
        # Calculate statistics for Manhattan
        print("\n" + "="*50)
        print("RESULTS - MANHATTAN HEURISTIC")
        print("="*50)
        
        solved_manhattan = [r for r in results_manhattan if r['success']]
        if len(solved_manhattan) > 0:
            avg_nodes_m = sum(r['nodes_expanded'] for r in solved_manhattan) / len(solved_manhattan)
            avg_time_m = sum(r['time'] for r in solved_manhattan) / len(solved_manhattan)
            
            # Calculate standard deviation
            variance_nodes_m = sum((r['nodes_expanded'] - avg_nodes_m)**2 for r in solved_manhattan) / len(solved_manhattan)
            std_nodes_m = math.sqrt(variance_nodes_m)
            
            variance_time_m = sum((r['time'] - avg_time_m)**2 for r in solved_manhattan) / len(solved_manhattan)
            std_time_m = math.sqrt(variance_time_m)
            
            print(f"Solved: {len(solved_manhattan)}/{games_to_generate}")
            print(f"Average nodes expanded: {avg_nodes_m:.2f} ± {std_nodes_m:.2f}")
            print(f"Average execution time: {avg_time_m:.4f}s ± {std_time_m:.4f}s")
        else:
            print("No games solved!")

    if "hamming" in heuristics:
        # Calculate statistics for Hamming
        print("\n" + "="*50)
        print("RESULTS - HAMMING HEURISTIC")
        print("="*50)
        
        solved_hamming = [r for r in results_hamming if r['success']]
        if len(solved_hamming) > 0:
            avg_nodes_h = sum(r['nodes_expanded'] for r in solved_hamming) / len(solved_hamming)
            avg_time_h = sum(r['time'] for r in solved_hamming) / len(solved_hamming)
            
            # Calculate standard deviation
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


def get_user_configuration():
    print("-------------------------------------------------------")
    print("---              Puzzle 8 Solver                    ---") 
    print("-------------------------------------------------------")
    games_to_generate = input("How many puzzles to run/benchmark: ")

    available_heuristics = ["manhattan", "hamming"]
    os.system('cls' if os.name == 'nt' else 'clear') 
    selection = [' ', ' ']
    while True:
        print("-how_to_select-----------------------------------------\n")
        print("Make a slection by entering numbers + ENTER to confirm.")
        print("Then press ENTER to start the benchmark.")
        print("-------------------------------------------------------\n")
        print("-current_selection-------------------------------------\n")
        print(f"(0) [{selection[0]}] {available_heuristics[0]}")
        print(f"(1) [{selection[1]}] {available_heuristics[1]}")
        print("-------------------------------------------------------")
        i = input("\nWhich heuristics to run (min. 1): ")
        if not i and 'x' in selection:
            break
        elif not i and not 'x' in selection:
            input("MUST SELECT AT LEAST ONE! Press [ENTER] to try again.")
        elif i.isdigit() and int(i) == 0 or int(i) == 1:
            if selection[int(i)] == ' ':
                selection[int(i)] = 'x'
            else:
                selection[int(i)] = ' '
        else:
            input("INPUT INVALID! Press [ENTER] to try again.")
        os.system('cls' if os.name == 'nt' else 'clear') 

    heuristics = []
    for i in range(len(selection)):
        if selection[i] == 'x':
            heuristics.append(available_heuristics[i])

    print(f"Will use heuristics: {heuristics}")
    return games_to_generate, heuristics


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear') 
    log.info("Application start.") 

    # simple user interaction/interface for configuring the benchmark
    games_to_generate, heuristics = get_user_configuration() 
    run_benchmark(int(games_to_generate), heuristics)
