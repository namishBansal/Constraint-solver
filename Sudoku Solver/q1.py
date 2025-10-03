"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def bij(r,c,d):
    return r * 100 + c * 10 + d

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT
    cnf = CNF()

    # Giving grid values as it is and if place is empty then ensuring there is one number there
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                cnf.append([bij(r, c, grid[r][c])])
            else:
                cnf.append([bij(r, c, d) for d in range(1, 10)])  # at least one
                for d1 in range(1,9):
                    for d2 in range (d1+1,10):
                        cnf.append([-bij(r,c,d1),-bij(r,c,d2)])
    
    for r in range(9) :
        for digit in range(1,10) :
            clauses = []
            for column in range(9) :
                # (r,c,d) disjunction
                clauses.append(bij(r,column,digit))
            # print(clauses)
            cnf.append(clauses)
            for c1 in range(9):
                for c2 in range(c1 + 1, 9):
                    cnf.append([-bij(r, c1, digit), -bij(r, c2, digit)])

    for column in range(9) :
        for digit in range(1,10) :
            clauses = []
            for row in range(9) :
                # (r,c,d) disjunction
                clauses.append(bij(row,column,digit))
            # print(clauses)
            cnf.append(clauses)
            for r1 in range(9):
                for r2 in range(r1 + 1, 9):
                    cnf.append([-bij(r1, column, digit), -bij(r2, column, digit)])

    for row in range(0,9,3) :
        for column in range(0,9,3) :
            #block
            
            for digit in range(1,10) :
                clauses = []
                for r in range(row, row+3) :
                    for c in range(column, column + 3) :
                        clauses.append(bij(r,c,digit))
                # print(clauses)
                cnf.append(clauses)
                for i in range(len(clauses)):
                    for j in range(i + 1, len(clauses)):
                        cnf.append([-clauses[i], -clauses[j]])


    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        solved_grid = [[0 for _ in range(9)] for _ in range(9)]
        if solver.solve():
            model = solver.get_model()
            for i in model:
                if i >0:
                    d = i % 10
                    c = (i // 10) % 10
                    r = i // 100
                    solved_grid[int(r)][int(c)] = d
            return solved_grid        
        else:
            return []

        