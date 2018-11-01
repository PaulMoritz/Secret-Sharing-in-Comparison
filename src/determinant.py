import numpy as np
from reconstruction_tools import print_matrix


def determinant(matrix, prime):
    if len(matrix) >= 15:
        print_matrix(matrix)
    if len(matrix) == 1:
        return matrix[0][0]
    elif len(matrix) == 2:
        return (int(matrix[0][0]) * int(matrix[1][1])) - (int(matrix[0][1]) * int(matrix[1][0])) % prime

    elif len(matrix) == 3:
        a = int(matrix[0][0]) * ((int(matrix[1][1]) * int(matrix[2][2]))
                                 - (int(matrix[1][2]) * int(matrix[2][1]))) % prime
        b = int(matrix[0][1]) * ((int(matrix[1][0]) * int(matrix[2][2]))
                                 - (int(matrix[1][2]) * int(matrix[2][0]))) % prime
        c = int(matrix[0][2]) * ((int(matrix[1][0]) * int(matrix[2][1]))
                                 - (int(matrix[1][1]) * int(matrix[2][0]))) % prime
        return (a - b + c) % prime
    else:
        det = 0
        for i in range(len(matrix)):
            if matrix[i][0] == 0:
                continue
            minor = get_minor(matrix, i, 0)
            det += int((((-1) ** i) * (int(matrix[i][0]) * determinant(minor, prime))))
            # print(det, "+= -1 **", i, "*", int(matrix[i][0]), "*", int(determinant(minor, prime)), "( ", minor, ")")
        return det % prime


# m without i - th row and j - th column
def get_minor(m, i, j):
    minor = np.zeros((len(m) - 1, len(m) - 1))
    for ii in range(i):
        for jj in range(j):
            minor[ii][jj] = m[ii][jj]
        for jj in range(j + 1, len(m)):
            minor[ii][jj - 1] = m[ii][jj]
    for ii in range(i + 1, len(m)):
        for jj in range(j):
            minor[ii - 1][jj] = m[ii][jj]
        for jj in range(j + 1, len(m)):
            minor[ii - 1][jj - 1] = m[ii][jj]
    return minor
