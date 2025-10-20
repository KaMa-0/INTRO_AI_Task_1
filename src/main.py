import math


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
    return None


# provide list with states, calculates cost for each state f(s) = g(s) + h(s)
def calculateCosts(possible_states):
    return None


# checks if state is solvable or not
def is_solvable(start_state):
    return None


# generate a random start_state for the board
def generateRandomSolvableBoard():
    return None


if __name__ == "__main__":
    print("Hello World")

    start_state = generateRandomSolvableBoard();    
    if not is_solvable(start_state):
        exit(2)

    exit(0)
