"""
simpleAIs
    act: return the index
"""
from abc import ABCMeta, abstractmethod

import reversi
from copy import deepcopy
import random
import numpy as np
from scipy.stats import beta

def allSearch(state, color, enables, nowDepth, maxDepth):
        """
        全探索

        enables: list
        colorから見た勝ち石の数listを返す
        """
        if nowDepth >= maxDepth:
            # stop searching
            return [len(np.where(state == color)[0]) - len(np.where(state == color^1)[0])]

        myWins = []
        if len(enables) == 0:
            # pass
            opponentEnables = reversi.getPossiblePoints(state, color^1)
            if len(opponentEnables) == 0:
                # game set
                myWins.append(len(np.where(state == color)[0]) - len(np.where(state == color^1)[0]))
            else:
                opponentWins = allSearch(state, color^1, opponentEnables, nowDepth+1, maxDepth)
                mybest = min(opponentWins)
                myWins.append(-mybest)
        else:
            board = deepcopy(state)
            for row, line in enables:
                reversi.putStone(board, row, line, color)
                opponentEnables = reversi.getPossiblePoints(board, color^1)
                opponentWins = allSearch(board, color^1, opponentEnables, nowDepth+1, maxDepth)
                mybest = min(opponentWins)
                myWins.append(-mybest)
        return myWins

class AI:
    def __init__(self, color, allSearchDepth=0):
        self.color = color
        self.allSearchDepth = allSearchDepth
    
    def act(self, state):
        leftStones = len(np.where(state == -1)[0])
        if leftStones <= self.allSearchDepth:
            enables = reversi.getPossiblePoints(state, self.color)
            if len(enables) == 0:
                return 65
            myWins = allSearch(state, self.color, enables, 0, self.allSearchDepth)
            choice = np.argmax(myWins)
            row, line = enables[choice]
            return row * 8 + line
        else:
            return self.play(state)
    
    @abstractmethod
    def play(self, state):
        pass


class RandomAI(AI):
    def __init__(self, color, allSearchDepth=0):
        super(RandomAI, self).__init__(color, allSearchDepth)
        
    def play(self, state):
        enable = reversi.getPossiblePoints(state, self.color)
        if len(enable) == 0:
            return 65
        else:
            put = random.choice(enable)
            return put[0]*8 + put[1]

class MonteAI(AI):
    def __init__(self, color, size, allSearchDepth=0, limit=5):
        super(MonteAI, self).__init__(color, allSearchDepth)
        self.size = size
        self.simulateEnv = reversi.ReversiEnv()
        self.allSearchDepth_simulate = limit
        self.simulateAIs = [
            RandomAI(c, self.allSearchDepth_simulate) for c in range(2)
        ]
        
    def simulate(self, state, putPoint, color):
        """
        途中までランダムに打ち、終盤(残りlimit手)は全探索を行う
        頻繁に呼ぶのでlimitは少なめ

        return winner (if draw: -1)
        """
        self.simulateEnv.setStones(state, color)
        
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
            leftStones = len(np.where(obs == -1)[0])
            """if leftStones <= self.allSearchDepth_simulate:
                enables = reversi.getPossiblePoints(obs, turn)
                r = max(allSearch(obs, turn, enables, 0, self.allSearchDepth_simulate))
                if r > 0:
                    return turn
                elif r < 0:
                    return turn^1
                else: # draw
                    return -1
            else:
                putPoint = self.simulateAIs[turn].act(obs) # next putPoint"""
            putPoint = self.simulateAIs[turn].act(obs) # next putPoint
    
    def play(self, state):
        enable = reversi.getPossiblePoints(state, self.color)
        if len(enable) == 0:
            return 65
        maxWin = -1
        putPoint = None
        for row, line in enable:
            win = 0
            for i in range(self.size):
                tmpState = deepcopy(state)
                r = self.simulate(tmpState, row*8+line, self.color)
                if r == self.color: # winner is me
                    win += 1
            if maxWin == -1 or maxWin < win:
                maxWin = win
                putPoint = row*8 + line
        return putPoint

class MonteTreeAI(MonteAI):
    def __init__(self, color, maxSize, depth, allSearchDepth=0, limit=5):
        super(MonteTreeAI, self).__init__(color, maxSize, allSearchDepth, limit)
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
        
        if len(subtree) == 0:
            # first visit
            subtree.extend([ [0, 0, []] for _ in enable ])
    
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
    
    def play(self, state):
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
