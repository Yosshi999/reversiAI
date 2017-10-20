import numpy as np
from copy import deepcopy

def putStone(state, row, line, color, flip=True):
    assert color == 0 or color == 1
    opponentColor = color ^ 1
    
    if state[row, line] == color or state[row, line] == opponentColor:
        return False

    canflip = False
    
    for _r, _l in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
        opponentExist = False
        ite_r, ite_l = row + _r, line + _l
        while ite_r >= 0 and ite_r < 8 and ite_l >= 0 and ite_l < 8:
            currentPoint = state[ite_r, ite_l]
            if currentPoint == opponentColor:
                opponentExist = True

            elif currentPoint == color:
                if opponentExist:
                    # can flip
                    canflip = True
                    if not flip:
                        # just check can flip
                        return True

                    while not (ite_r == row and ite_l == line):
                        state[ite_r, ite_l] = color
                        ite_r -= _r
                        ite_l -= _l
                    break
                else:
                    # unable to flip
                    break
            else:
                # unable to flip
                break
            # next point
            ite_r += _r
            ite_l += _l
        # next direction
    if canflip and flip:
        state[row, line] = color
        return True
    else:
        return False


def canFlip(state, row, line, color):
    if putStone(state, row, line, color, flip=False):
        return True
    else:
        return False


def getPossiblePoints(state, color):
    ret = []
    for i in range(8):
        for j in range(8):
            if canFlip(state, i, j, color):
                ret.append((i,j))
    return ret

class ReversiEnv:
    def __init__(self):
        self.board = np.array([
            [-1,-1,-1,-1, -1,-1,-1,-1],
            [-1,-1,-1,-1, -1,-1,-1,-1],
            [-1,-1,-1,-1, -1,-1,-1,-1],
            [-1,-1,-1, 1,  0,-1,-1,-1],

            [-1,-1,-1, 0,  1,-1,-1,-1],
            [-1,-1,-1,-1, -1,-1,-1,-1],
            [-1,-1,-1,-1, -1,-1,-1,-1],
            [-1,-1,-1,-1, -1,-1,-1,-1],
        ])
        self.turn = 0 # black:0 white:1
        self.stones = [2, 2]
        self.possiblePoints = [getPossiblePoints(self.board, c) for c in range(2)]
    
    def setStones(self, arr, turn):
        self.board = arr
        self.turn = turn
        for c in range(2):
            self.stones[c] = len(np.where(self.board == c)[0])
            self.possiblePoints[c] = getPossiblePoints(self.board, c)

    def step(self, index):
        """
        index: row*8 + line (pass is 65)
        return obs, reward, done, info
        """

        reward = 0
        done = False
        info = None


        # pass check
        if index == 65:
            if len(self.possiblePoints[self.turn]) > 0:
                # invalid pass
                return self.board, -1, True, None
            
            else:
                reward = 0
        
        # put stone
        else:
            row = index // 8
            line = index % 8
            if not putStone(self.board, row, line, self.turn):
                # invalid put
                return self.board, -1, True, None
            else:
                # valid put
                for c in range(2):
                    self.stones[c] = len(np.where(self.board == c)[0])
                    self.possiblePoints[c] = getPossiblePoints(self.board, c)
            

        if len(self.possiblePoints[0]) == 0 and len(self.possiblePoints[1]) == 0:
            # game set
            done = True
            if self.stones[0] == self.stones[1]:
                # draw
                reward = 0
            else:
                winner = np.argmax(self.stones)
                if winner == self.turn:
                    # win
                    reward = 1
                else:
                    reward = -1

        else:
            self.turn ^= 1

        return self.board, reward, done, info
            
