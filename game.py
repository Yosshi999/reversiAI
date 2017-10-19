import reversi
import simpleAIs
import sys
from time import sleep

AI = [simpleAIs.MonteTreeAI(0, 10, 1), simpleAIs.RandomAI(1)]

print("0:\033[46m  \033[0m 1:\033[43m  \033[49m")
def printObs(obs):
    for i in range(8):
        for j in range(8):
            if obs[i, j] == 0:
                print("\033[46m  \033[49m", end="")
            elif obs[i, j] == 1:
                print("\033[43m  \033[49m", end="")
            else:
                print("\033[47m  \033[49m", end="")
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
    
    print("wins:", win)
    # print("\033[8B", end="")
    print("\n"*7)
    print("\033[8A\r", end="")
    printObs(obs)

    while not done:
        obs, r, done, info = env.step(AI[turn].act(obs))
        print("\033[8A\r", end="")
        printObs(obs)
        
        if r == 1:
            print("win:", turn)
            win[turn] += 1
            break
        elif r == -1:
            print("win:", turn^1)
            win[turn^1] += 1
            break
        turn ^= 1
        sleep(0.1)

print()
print("wins:", win)
