"""
simpleAIs
    act: return the index
"""

import reversi
from copy import deepcopy
import random
import numpy as np
from scipy.stats import beta

class RandomAI:
    def __init__(self, color):
        self.color = color
    def act(self, state):
        enable = reversi.getPossiblePoints(state, self.color)
        if len(enable) == 0:
            return 65
        else:
            put = random.choice(enable)
            return put[0]*8 + put[1]

class MonteAI:
    def __init__(self, color, size):
        self.color = color
        self.size = size
        self.simulateEnv = reversi.ReversiEnv()
        self.simulateAIs = [RandomAI(c) for c in range(2)]
    
    def simulate(self, state, putPoint, color):
        """
        return winner (if draw: -1)
        """
        self.simulateEnv.setStones(state, color)
        self.simulateEnv.turn = color
        turn = color
        t = 0
        while True:
            obs, r, done, info = self.simulateEnv.step(putPoint)
            if done:
                if r == 1:
                    return turn
                elif r == -1:
                    return turn^1
                else: # draw
                    return -1
            turn ^= 1
            putPoint = self.simulateAIs[turn].act(obs) # next putPoint

    def act(self, state):
        enable = reversi.getPossiblePoints(state, self.color)
        if len(enable) == 0:
            return 65
        maxWin = -1
        putPoint = None
        for row, line in enable:
            win = 0
            for i in range(self.size):
                r = self.simulate(state, row*8+line, self.color)
                if r == self.color: # winner is me
                    win += 1
            if maxWin == -1 or maxWin < win:
                maxWin = win
                putPoint = row*8 + line
        return putPoint

class MonteTreeAI(MonteAI):
    def __init__(self, color, maxSize, depth):
        super(MonteTreeAI, self).__init__(color, maxSize)
        self.maxSize = maxSize
        self.depth = depth
        self.tree = [] # [[win, lose, children],...]
    
    def search(self, state, color, depth, subtree):
        """
        path: if you choose 19 from enable=[13,19,20,21] (choose enable[1]) 
            and then opponent choose 32 from enable=[14,24,32,53], (enable[2])
            the path is [1,2]
        """
        enable = reversi.getPossiblePoints(state, color)
        if depth == self.depth+1:
            # no thinking (simulate)
            if len(enable) == 0:
                return self.simulate(state, 65, color)
            row, line = random.choice(enable)
            return self.simulate(state, row*8+line, color)

        if len(enable) == 0:
            return self.search(state, color^1, depth+1, subtree)
        
        searchedLen = len(subtree)
        if len(enable) - searchedLen > 0:
            subtree.append([0, 0, []])
            row, line = enable[searchedLen]

            reversi.putStone(state, row, line, color)
            r = self.search(state, color^1, depth+1, subtree[-1][2])
            if r == color:
                subtree[-1][0] += 1
            else:
                subtree[-1][1] += 1
            return r
        else:
            wins = np.array([node[0] for node in subtree])
            loses = np.array([node[1] for node in subtree])
            values = beta.rvs(wins + 1, loses + 1)
            choice = values.argmax()
            row, line = enable[choice]
            reversi.putStone(state, row, line, color)
            r = self.search(state, color^1, depth+1, subtree[choice][2])
            if r == color:
                subtree[choice][0] += 1
            else:
                subtree[choice][1] += 1
            return r
    def act(self, state):
        enable = reversi.getPossiblePoints(state, self.color)
        if len(enable) == 0:
            return 65
        if len(enable) == 1:
            return enable[0][0] * 8 + enable[0][1]
        self.tree = []
        for i in range(self.maxSize):
            tmpState = deepcopy(state)
            self.search(tmpState, self.color, 1, self.tree)
        wins = np.array([node[0] for node in self.tree])
        loses = np.array([node[1] for node in self.tree])
        # best = (wins + loses).argmax()
        best = beta.median(wins+1, loses+1).argmax()
        return enable[best][0]*8 + enable[best][1]

"""        for ite in range(len(enable)):
            row, line = enable[ite]

            for i in range(self.size):
                r = self.simulate(state, row*8+line)
                if r == 1:
                    win += 1
            if maxWin == -1 or maxWin < win:
                maxWin = win
                putPoint = row*8 + line
        return putPoint        
"""
