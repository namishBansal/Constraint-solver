"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for x in range(self.N) :
            for y in range(self.M) :
                cell = self.grid[x][y]

                if cell == 'P' :
                    self.player_start = (x,y)
                elif cell == 'B' :
                    self.boxes.append((x,y))
                elif cell == 'G' :
                    self.goals.append((x,y))

    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return 1 + t * (self.N + 1) * (self.M + 1) + x * (self.M + 1)+ y

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return (self.T + 1) * ((self.N + 1) * (self.M + 1)) + b * ((self.T+1) * (self.N + 1) * (self.M + 1)) + t * ((self.N + 1) * (self.M + 1)) + x * (self.M + 1) + y


    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditions
        # 6. Other conditions

        (x,y) = self.player_start

        # adding initial position of player to cnf
        self.cnf.append([self.var_player(x,y,0)])

        # adding initial position of boxes to cnf
        for b, (bx, by) in enumerate(self.boxes) :
            self.cnf.append([self.var_box(b,bx,by,0)])

        # at any point of time, a player can be at only one position,
        # only one position can be enforced by enforcing that at any point of time, a player is at aleast one position and at atmost one position
        for t in range(self.T + 1) :
            # atleast one
            clauses = []
            for x in range(self.N) :
                for y in range(self.M) :
                    # constraint that no player or box can be in a cell where there is a wall.
                    if self.grid[x][y] == '#' :
                        self.cnf.append([-self.var_player(x,y,t)])
                        for b in range(self.num_boxes) :
                            self.cnf.append([-self.var_box(b,x,y,t)])
                    # position (x,y)
                    else :
                        # adding the condition that a player is in atleast one cell at time t
                        clauses.append(self.var_player(x,y,t))

                        # no two boxes can be in the same cell at any given time t
                        for b1 in range(self.num_boxes) :
                            for b2 in range(b1 + 1, self.num_boxes) :
                                self.cnf.append([-self.var_box(b1,x,y,t), -self.var_box(b2,x,y,t)])
                        
                        # player and box not in same cell at any given time t
                        for b in range(self.num_boxes) :
                            self.cnf.append([-self.var_box(b,x,y,t), -self.var_player(x,y,t)])
            self.cnf.append(clauses)
            # every player is in atmost one cell at any given time t but to optimize we only check on positions that are not walls which was established above
            for i in range(len(clauses)) :
                for j in range(i + 1, len(clauses)) :
                    self.cnf.append([-clauses[i], -clauses[j]])

        # # players or boxes cannot be in cells where there are walls i.e. '#'
        # for t in range(self.T + 1) :
        #     for x in range(self.N) :
        #         for y in range(self.M) :
        #             if self.grid[x][y] == '#' :
        #                 self.cnf.append([-self.var_player(x,y,t)])
        #                 for b in range(self.num_boxes) :
        #                     self.cnf.append([-self.var_box(b,x,y,t)])

        # each box is in exactly one non-wall cell at any time : atleast and atmost
        for b in range(self.num_boxes) :
            for t in range(self.T + 1) :
                # atleast one cell
                clauses = []
                for x in range(self.N) :
                    for y in range(self.M) :
                        if self.grid[x][y] != '#' :
                            clauses.append(self.var_box(b,x,y,t))
                self.cnf.append(clauses)

                # atmost one cell
                for i in range(len(clauses)) :
                    for j in range(i + 1, len(clauses)) :
                        self.cnf.append([-clauses[i], -clauses[j]])

        # # at any time, no two boxes can be in same cell
        # for t in range(self.T + 1) :
        #     for x in range(self.N) :
        #         for y in range(self.M) :
        #             # cant have two boxes
        #             if self.grid[x][y] != '#' :
        #                 for b1 in range(self.num_boxes) :
        #                     for b2 in range(b1 + 1, self.num_boxes) :
        #                         self.cnf.append([-self.var_box(b1,x,y,t), -self.var_box(b2,x,y,t)])

        # player and box cannot be in same cell at any time
        # for t in range(self.T + 1) :
        #     for x in range(self.N) :
        #         for y in range(self.M) :
        #             # cant have a player AND a box
        #             if self.grid[x][y] != '#' :
        #                 for b in range(self.num_boxes) :
        #                     self.cnf.append([-self.var_box(b,x,y,t), -self.var_player(x,y,t)])

        # player movement constraints
        for t in range(self.T) :
            for x in range(self.N) :
                for y in range(self.M) :
                    if self.grid[x][y] != '#' :
                        neighbors = []
                        for dirx, diry in DIRS.values() :
                            newx = x + dirx
                            newy = y + diry

                            # check if valid neighbors
                            if 0 <= newx and newx < self.N and 0 <= newy and newy < self.M and self.grid[newx][newy] != '#' :
                                neighbors.append(self.var_player(newx, newy, t+1))
                        
                        if neighbors :
                            self.cnf.append([-self.var_player(x,y,t), self.var_player(x,y,t+1)] + neighbors)
        
        # box movement constraints
        for b in range(self.num_boxes) :
            for t in range(self.T) :
                for x in range(self.N) :
                    for y in range(self.M) :
                        if self.grid[x][y] != '#' :
                            neighbors = []
                            for dirx, diry in DIRS.values() :
                                newx = x + dirx
                                newy = y + diry

                                playerx = x - dirx
                                playery = y - diry

                                if 0 <= newx and newx < self.N and 0 <= newy and newy < self.M and self.grid[newx][newy] != '#' : 
                                    # if next cell is invalid, forbid this move
                                    if not (0 <= playerx and playerx < self.N and 0 <= playery and playery < self.M and self.grid[playerx][playery] != '#'):
                                        self.cnf.append([-self.var_box(b,x,y,t), -self.var_box(b,newx, newy, t+1)])
                                    else :
                                        self.cnf.append([-self.var_box(b,x,y,t), -self.var_box(b,newx, newy, t+1), self.var_player(playerx, playery, t)])
                                        self.cnf.append([-self.var_box(b, x, y, t), -self.var_box(b, newx, newy, t + 1),self.var_player(x, y, t + 1)])


                                    neighbors.append(self.var_box(b, newx, newy, t+1))
                            
                            if neighbors :
                                self.cnf.append([-self.var_box(b,x,y,t), self.var_box(b,x,y,t+1)] + neighbors)
        
        # # a box should move only if it is pushed
        # for b in range(self.num_boxes) :
        #     for t in range(self.T) :
        #         for x in range(self.N) :
        #             for y in range(self.M) :
        #                 if self.grid[x][y] != '#' :
        #                     for dirx, diry in DIRS.values() :
        #                         newx = x + dirx
        #                         newy = y + diry
        #                         playerx = x - dirx
        #                         playery = y - diry
        #                         if 0 <= newx and newx < self.N and 0 <= newy and newy < self.M and 0 <= playerx and playerx < self.N and 0<= playery and playery < self.M and self.grid[newx][newy] != '#' and self.grid[playerx][playery] != '#' :
        #                             # if box at x,y,t and newx,newy,t+1 then player at playerx,playery,t
        #                             self.cnf.append([-self.var_box(b,x,y,t), -self.var_box(b,newx,newy,t+1) , self.var_player(playerx, playery,t)])
        #                             self.cnf.append([-self.var_box(b,x,y,t), -self.var_box(b,newx,newy,t+1) , self.var_player(x, y,t + 1)])

        # # if we know player movement, then get box movement
        # # might be repetition CHECK
        # for t in range(self.T) :
        #     for x in range(self.N) :
        #         for y in range(self.M) :
        #             if self.grid[x][y] != '#' :
        #                 for dirx, diry in DIRS.values() :
        #                     playerx = x - dirx
        #                     playery = y - diry
        #                     newx = x + dirx
        #                     newy = y + diry
        #                     if 0 <= newx and newx < self.N and 0 <= newy and newy < self.M and 0 <= playerx and playerx < self.N and 0<= playery and playery < self.M :
        #                         for b in range(self.num_boxes) :
        #                             self.cnf.append([-self.var_player(playerx, playery, t) , -self.var_player(x,y,t+1), -self.var_box(b,x,y,t), self.var_box(b, newx, newy, t+1)])
        #                     # elif 0 <= newx and newx < self.N and 0 <= newy and newy < self.M:
        #                     #     for b in range(self.num_boxes) :
        #                     #         self.cnf.append([-self.var_player(x,y,t+1), -self.var_box(b,x,y,t), -self.var_box(b, newx, newy, t+1)])
        #                     elif 0 <= playerx and playerx < self.N and 0<= playery and playery < self.M:
        #                         for b in range(self.num_boxes) :
        #                             self.cnf.append([-self.var_player(playerx, playery, t) , -self.var_player(x,y,t+1), -self.var_box(b,x,y,t)])
        # self.grid[newx][newy] != '#' and self.grid[playerx][playery] != '#'
        # a box can't move into a

        # box moves only if pushed and only if next cell it has to move to is possible
        # for b in range(self.num_boxes) :
        #     for t in range(self.T) :
        #         for x in range(self.N) :
        #             for y in range(self.M) :
        #                 if self.grid[x][y] != '#' :
        #                     for dirx, diry in DIRS.values() :
        #                         newx = x + dirx
        #                         newy = y + diry
        #                         playerx = x - dirx
        #                         playery = y - diry
        #                         if 0 <= newx and newx < self.N and 0 <= newy and newy < self.M and self.grid[newx][newy] != '#' :
        #                             # if next cell is invalid, forbid this move
        #                             if not (0 <= playerx and playerx < self.N and 0 <= playery and playery < self.M and self.grid[playerx][playery] != '#'):
        #                                 self.cnf.append([-self.var_box(b,x,y,t), -self.var_box(b,newx, newy, t+1)])
        #                             else :
        #                                 self.cnf.append([-self.var_box(b,x,y,t), -self.var_box(b,newx, newy, t+1), self.var_player(playerx, playery, t)])
                                        # self.cnf.append([-self.var_box(b, x, y, t), -self.var_box(b, newx, newy, t + 1),self.var_player(x, y, t + 1)])


        for t in range(self.T + 1) :
            for y in range(self.M + 1) :
                self.cnf.append([-self.var_player(self.N,y,t)])
                for b in range(self.num_boxes) :
                    self.cnf.append([-self.var_box(b,self.N, y, t)])
            for x in range(self.N + 1) :
                self.cnf.append([-self.var_player(x,self.M,t)])
                for b in range(self.num_boxes) :
                    self.cnf.append([-self.var_box(b, x, self.M, t)])

        # goal condition
        for b in range(self.num_boxes) :
            clauses = []
            for (x,y) in self.goals :
                clauses.append(self.var_box(b,x,y,self.T))
            self.cnf.append(clauses)

        return self.cnf


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T

    pos = {}
    for t in range(encoder.T + 1) :
        for x in range(encoder.N) :
            for y in range(encoder.M) :
                if encoder.var_player(x,y,t) in model :
                    pos[t] = (x,y)
    
    moves = []
    for t in range(encoder.T + 1) :
        if t in pos and t+1 in pos :
            (x1, y1) = pos[t]
            (x2, y2) = pos[t+1]
            dx, dy = x2-x1, y2-y1
            for charac, (dirx, diry) in DIRS.items() :
                if (dx,dy) == (dirx,diry) :
                    moves.append(charac)

    # TODO: Map player positions at each timestep to movement directions
    return moves



def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1
        moves = decode(model,encoder)
        if not moves :
            return -1
        return decode(model, encoder)