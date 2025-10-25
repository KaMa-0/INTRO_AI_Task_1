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
    
    Input: start_state - 3x3 board
           heuristic_name - "manhattan" or "hamming"
    Output: (success, iterations, nodes_expanded, time_taken)
    Function: Finds solution using A* with priority queue for efficiency
    
    Time Complexity: O(b^d) where b is branching factor, d is solution depth
    Space Complexity: O(b^d) for storing visited states
    """
    start_time = time.time()
    
    # Check if already at goal
    if state_to_string(start_state) == state_to_string(goal_state):
        return True, 0, 0, 0.0
    
    # Calculate initial costs
    g_cost = 0
    if heuristic_name == "manhattan":
        h_cost = manhattan(start_state)
    elif heuristic_name == "hamming":
        h_cost = hamming(start_state)
    else:
        return False, 0, 0, 0.0
    
    f_cost = g_cost + h_cost
    start_string = state_to_string(start_state)
    
    # Priority queue: stores (f_cost, counter, state_string, state, g_cost)
    open_heap = []
    heapq.heappush(open_heap, (f_cost, 0, start_string, start_state, g_cost))
    
    # Track visited states
    closed_set = set()
    
    nodes_expanded = 0
    iterations = 0
    counter = 1  # For tie-breaking in heap
    
    # Main A* loop
    while open_heap:
        iterations += 1
        
        # Safety limit
        if iterations > 1000000:
            return False, iterations, nodes_expanded, time.time() - start_time
        
        # Get state with lowest f_cost from heap
        current_f, _, current_string, current_state, current_g = heapq.heappop(open_heap)
        
        # Skip if already visited
        if current_string in closed_set:
            continue
        
        # Mark as visited
        closed_set.add(current_string)
        nodes_expanded += 1
        
        # Check if goal reached
        if current_string == state_to_string(goal_state):
            return True, iterations, nodes_expanded, time.time() - start_time
        
        # Generate neighbor states
        neighbor_states = neighbors(current_state)
        
        # Calculate costs for neighbors
        new_g_cost = current_g + 1
        neighbor_costs = calculateCosts(neighbor_states, heuristic_name, new_g_cost)
        
        # Add neighbors to heap
        for neighbor_state, neighbor_f in neighbor_costs:
            neighbor_string = state_to_string(neighbor_state)
            
            # Skip if already visited
            if neighbor_string in closed_set:
                continue
            
            # Add to priority queue
            heapq.heappush(open_heap, (neighbor_f, counter, neighbor_string, neighbor_state, new_g_cost))
            counter += 1
    
    # No solution found
    return False, iterations, nodes_expanded, time.time() - start_time


if __name__ == "__main__":
    log.info("Application start.")
    
    games_to_generate = 100  # Use 100 for full benchmark
    
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

        # Solve with Hamming heuristic
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
        
        print(f"Game {game_id+1}/{games_to_generate} completed")

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
