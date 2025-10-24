import os
import time
import math
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
goal_state = [[0, 1, 2],
              [3, 4, 5],
              [6, 7, 8]]

# ---------- helpers: grid <-> flat, goal lookup ----------

def to_flat(state_3x3):
    """3x3 list -> flat tuple (length 9)"""
    return tuple(tile for row in state_3x3 for tile in row)

def to_string_flat(state_flat):
    """flat tuple -> '012345678' string"""
    return ''.join(str(x) for x in state_flat)

# precompute goal positions for tiles 0..8
_goal_pos = {tile: (tile // 3, tile % 3) for tile in range(9)}
_goal_flat = to_flat(goal_state)

# ---------- heuristics (fast, on flat tuples) ----------

def hamming_flat(s):
    """
    Input: s flat tuple of 9 ints
    Output: misplaced tiles (excluding 0)
    """
    cnt = 0
    for i, v in enumerate(s):
        if v != 0 and v != _goal_flat[i]:
            cnt += 1
    return cnt

def manhattan_flat(s):
    """
    Input: s flat tuple of 9 ints
    Output: sum of Manhattan distances to goal (excluding 0)
    """
    total = 0
    for i, v in enumerate(s):
        if v == 0:
            continue
        r, c = divmod(i, 3)
        gr, gc = _goal_pos[v]
        total += abs(r - gr) + abs(c - gc)
    return total

# keep these names to match your earlier code (they’re thin wrappers now)
def hamming(current_state):
    return hamming_flat(to_flat(current_state))

def manhattan(current_state):
    return manhattan_flat(to_flat(current_state))

# ---------- neighbors on flat tuples (no deepcopy) ----------

# for a zero index i, these are the legal swaps (computed from row/col)
def _neighbor_indices(z):
    r, c = divmod(z, 3)
    if r > 0:
        yield z - 3  # up
    if r < 2:
        yield z + 3  # down
    if c > 0:
        yield z - 1  # left
    if c < 2:
        yield z + 1  # right

def neighbors_flat(s):
    """
    Generate neighbor states by swapping 0 with adjacent tiles.
    Returns a list of flat tuples.
    """
    z = s.index(0)
    res = []
    for j in _neighbor_indices(z):
        lst = list(s)
        lst[z], lst[j] = lst[j], lst[z]
        res.append(tuple(lst))
    return res

# legacy signature (not used by solver now, but kept if you need it elsewhere)
def neighbors(current_state):
    return [ [list(n[0:3]), list(n[3:6]), list(n[6:9])] for n in neighbors_flat(to_flat(current_state)) ]

# ---------- solvability & start generation ----------

def is_solvable(state_3x3):
    """
    3x3 list solvability using inversion count (blank ignored).
    """
    flat = [v for v in to_flat(state_3x3) if v != 0]
    inv = 0
    n = len(flat)
    for i in range(n):
        for j in range(i + 1, n):
            if flat[i] > flat[j]:
                inv += 1
    return (inv % 2 == 0)

def generateRandomSolvableBoard():
    """
    Returns a random solvable 3x3 board as list of lists.
    """
    vals = list(range(9))  # 0..8
    while True:
        random.shuffle(vals)
        state = [vals[0:3], vals[3:6], vals[6:9]]
        if is_solvable(state):
            return state

# ---------- A* with heapq (fast) ----------

def solve_puzzle(start_state, heuristic_name):
    """
    A* using a min-heap (open list). States are flat tuples.
    Returns: (success:bool, iterations:int, nodes_expanded:int, elapsed:float)
    """
    start_t = time.time()

    s0 = to_flat(start_state)
    if s0 == _goal_flat:
        return True, 0, 0, 0.0

    # choose heuristic
    if heuristic_name == "manhattan":
        h_fn = manhattan_flat
    elif heuristic_name == "hamming":
        h_fn = hamming_flat
    else:
        return False, 0, 0, 0.0

    g0 = 0
    h0 = h_fn(s0)
    f0 = g0 + h0

    # open heap entries: (f, g, tie_breaker, state_string, state_flat)
    counter = 0
    open_heap = [(f0, g0, counter, to_string_flat(s0), s0)]
    # best g we have seen for a state
    best_g = {s0: g0}
    # closed set not strictly necessary if we keep best_g, but we count expanded nodes
    nodes_expanded = 0
    iteration = 0
    max_iterations = 1_000_000  # keep a high safety ceiling

    while open_heap:
        iteration += 1
        if iteration > max_iterations:
            return False, iteration, nodes_expanded, (time.time() - start_t)

        f, g, _, s_str, s = heapq.heappop(open_heap)
        nodes_expanded += 1

        if s == _goal_flat:
            return True, iteration, nodes_expanded, (time.time() - start_t)

        new_g = g + 1
        for n in neighbors_flat(s):
            # skip if we already found a cheaper path
            if n in best_g and new_g >= best_g[n]:
                continue

            h = h_fn(n)
            fn = new_g + h
            best_g[n] = new_g
            counter += 1
            heapq.heappush(open_heap, (fn, new_g, counter, to_string_flat(n), n))

    return False, iteration, nodes_expanded, (time.time() - start_t)

# ---------- reporting ----------

def summarize(label, results):
    """
    Print summary stats over ALL runs (not just solved).
    """
    print("\n" + "="*50)
    print(f"RESULTS - {label.upper()} HEURISTIC")
    print("="*50)

    total = len(results)
    solved = sum(1 for r in results if r['success'])
    nodes = [r['nodes_expanded'] for r in results]
    times = [r['time'] for r in results]

    avg_nodes = sum(nodes) / total if total else 0.0
    avg_time = sum(times) / total if total else 0.0

    var_nodes = sum((x - avg_nodes)**2 for x in nodes) / total if total else 0.0
    var_time = sum((t - avg_time)**2 for t in times) / total if total else 0.0

    std_nodes = math.sqrt(var_nodes)
    std_time = math.sqrt(var_time)

    print(f"Solved: {solved}/{total}")
    print(f"Average nodes expanded: {avg_nodes:.2f} ± {std_nodes:.2f}")
    print(f"Average execution time: {avg_time:.4f}s ± {std_time:.4f}s")

# ---------- main ----------

if __name__ == "__main__":
    log.info("Application start.")

    games_to_generate = 100
    results_manhattan = []
    results_hamming = []

    for game_id in range(games_to_generate):
        log.info(f"=== Creating game with ID {game_id} ===")
        start_state = generateRandomSolvableBoard()
        log.debug(f"Board: {start_state}")

        # Manhattan
        log.info("Solving with MANHATTAN heuristic...")
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
            log.warning("Manhattan FAILED")

        # Hamming
        log.info("Solving with HAMMING heuristic...")
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
            log.warning("Hamming FAILED")

        print(f"Game {game_id+1}/{games_to_generate} completed")

    summarize("manhattan", results_manhattan)
    summarize("hamming", results_hamming)

    print("\n" + "="*50)
    log.info("Application end. (exit: 0, program finished)")
    exit(0)
