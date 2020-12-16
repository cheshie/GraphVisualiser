import functools
import itertools
import operator
from numpy import split, array, transpose
from itertools import permutations
from collections import deque

"""
A  B  C  D  E  F
B  E -D -A -C -F
C -D -B  E  A -F
D -A  E  C -B -F
E -C  A -B  D -F
F -F  F -F  F -F
"""

"""
Tresc zadania:

DCT-VIII, N = 6:
      __                __    __  __
      | A  B  C  D  E  F |    | x0 |
      | B  E -D -A -C -F |    | x1 |
      | C -D -B  E  A -F |    | x2 |
A6=   | D -A  E  C -B -F |  x | x3 |
      | E -C  A -B  D -F |    | x4 |
      | F -F  F -F  F -F |    | x5 |
      --                --    --  --
"""

schemes = {
    1: [['a', 'a'], ['b', 'c']],  # lambda mx : True if mx[0] == mx[1] and mx[1] != mx[2] and mx[2] != mx[3] else False
    2: [['a', 'b'], ['a', 'c']],
    3: [['a', 'b'], ['c', 'a']],
    4: [['a', 'b'], ['c', '-a']],
    5: [['a', 'b'], ['b', '-a']],
    6: [['a', 'b'], ['b', 'a']],
    7: [['a', 'b'], ['-b', '-a']],
    8: [['a', 'b'], ['b', 'b']],
    9: [['a', '-b'], ['b', 'b']],
    10: [['a', 'a'], ['b', '-b']],
    11: [['a', 'b'], ['a', '-b']],
    12: [['a', 'a'], ['b', 'b']],
    13: [['a', 'b'], ['a', 'b']],
    14: [['a', 'a'], ['a', 'a']],
    15: [['-a', 'a'], ['a', '-a']],
}


# Input: matrix in txt. Output: column-like matrix
def get_columns_of_matrix(mx, N):
    return [[mx.split()[x] for x in range(i, N * N, N)] for i in range(0, N)]


# Input: matrix in txt. Output: row-like matrix
def get_rows_of_matrix(mx, N):
    return [list(x) for x in split(array(mx.split()), N)]


# Having matrix nxn, divide it into lists that contain elements of its quarter
#     | A | B |
# M = |--- ---|
#     | C | D |
#
def split_into_quarter(mx, N):
    # Divide into upper half and bottom half
    uh, bh = mx.split()[:(N * N) // 2], mx.split()[(N * N) // 2:]
    quarters = []
    for x in [uh, bh]:
        # divide upper half into lists containing N/2 elements
        lsts = [[x[a] for a in range(i, i + 3)] for i in range(0, (N * N) // 2, N // 2)]
        # glue these lists to create quarters
        quarters += [lsts[::2], lsts[1::2]]

    return quarters


# Take matrix with negative elements, return without any minuses (helper function for comparison)
def get_matrix_wo_minus(mx, N):
    return get_rows_of_matrix(mx_to_txt(mx).replace('-', ''), N)


# Convert list of lists to a string
def mx_to_txt(mx):
    return ' '.join(array(mx).flatten())


# Check given matrix against schemes
def check_scheme(mx, N):
    # Split into quarters
    a, b, c, d = split_into_quarter(mx, N)

    # First probable solution
    sol = [
        ['a', a],
        ['b', b],
        ['c', c],
        ['d', d]
    ]

    # For first quarter, check whether it equals second, third, fourth
    # For second, whether it equals third, fourth ...
    for i in range(4):
        for j in range(i + 1, 4):
            # Check whether these matrices equal, not taking minuses into account
            if get_matrix_wo_minus(sol[i][1], N // 2) == get_matrix_wo_minus(sol[j][1], N // 2):
                # If yes, take minuses into account
                if sol[i][1] == sol[j][1]:
                    sol[j][0] = sol[i][0]
                else:
                    # If the do not equal, maybe it is situation i.e. a and -a
                    # To check that, iterate over matrix and check each character
                    guard = True
                    for ltr in range(len(sol[i][1])):
                        if '-' in array(sol[i][1]).flatten()[ltr] and '-' in array(sol[j][1]).flatten()[ltr] \
                                or '-' not in array(sol[i][1]).flatten()[ltr] and '-' not in array(sol[j][1]).flatten()[
                            ltr]:
                            guard = False

                    if guard:
                        sol[j][0] = '-' + sol[i][0]

    # Change matrix so that it will represent consecutive letter for ex.
    # instead of [a, a, c, d] => [a, a, b, c]
    for i in range(4):
        if sol[i][0] == 'a':
            continue
        # We must only "correct" values that do not have minus
        if '-' not in sol[i][0]:
            if chr(ord(sol[i][0]) - 1) not in [x[0] for x in sol]:
                sol[i][0] = chr(ord(sol[i][0]) - 1)

    print([x[0] for x in sol])


N = 6  # size of matrix
mx = \
    """
    A  B  C -H -I -J
    A  B  C -D -A -E
    A  B  C -F -F -F
    H  I  J -H -I -J
    D  A  E -D -A -E
    F  F  F -F -F -F
    """

# x = split_into_quarter(mx, N)
check_scheme(mx, N)

# v mx = get_rows_of_matrix(mx, N)
# for x in permutations(get_columns_of_matrix(mx, N)):
#     print(x)
