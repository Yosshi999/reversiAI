import reversi

class Human:
    def __init__(self, color):
        self.color = color
    
    def act(self, state):
        print("\033[K\n"*2 + "\033[2A", end="")
        if len(reversi.getPossiblePoints(state, self.color)) == 0:
            # pass turn
            print("\rplayer: pass\033[K", end="")
            return 65
        while True:
            print("\r\033[K>>> ", end="")
            query = input()
            try:
                row, line = map(int, query.split(","))
            except:
                print("input row, line (0-7)\033[1A", end="")
                continue
        
            if 0 <= row and row < 8 and 0 <= line and line < 8:
                # valid query
                print("\033[1A", end="")
                return row * 8 + line
            else:
                print("input row, line (0-7)\033[1A", end="")