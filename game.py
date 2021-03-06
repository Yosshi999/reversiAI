import reversi
import simpleAIs
import sys
from time import sleep
import human

AI = [simpleAIs.MonteTreeAI(0, 100, 5), simpleAIs.RandomAI(1)]

print("0:\033[46m  \033[0m 1:\033[43m  \033[49m")
def printObs(obs, lastRow, lastLine):
    print("\033[9A\r", end="")
    print(" 0 1 2 3 4 5 6 7")
    for i in range(8):
        print(i, end="")
        for j in range(8):
            if i == lastRow and j == lastLine:
                st = "::"
            else:
                st = "  "
            if obs[i, j] == 0:
                print("\033[46m%s\033[49m"%st, end="")
            elif obs[i, j] == 1:
                print("\033[43m%s\033[49m"%st, end="")
            else:
                print("\033[47m%s\033[49m"%st, end="")
        print()
    #print()

n_episodes = 100
env = reversi.ReversiEnv()

win = [0, 0]
for i in range(1, n_episodes+1):
    env.__init__()
    turn = 0
    obs = env.board
    done = False
    
    print("wins:", win, "\033[K")
    # print("\033[8B", end="")
    print("\n"*8)
    printObs(obs, -1, -1)

    while not done:
        action = AI[turn].act(obs)
        obs, r, done, info = env.step(action)

        printObs(obs, action//8, action%8)
        
        if r == 1:
            print("win:", turn, "\033[K")
            win[turn] += 1
            break
        elif r == -1:
            print("win:", turn^1, "\033[K")
            win[turn^1] += 1
            break
        turn ^= 1
        sleep(0.1)

print()
print("wins:", win, "\033[K")
