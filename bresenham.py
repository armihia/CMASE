import numpy as np

def bresenham_line(start, end):
    x0, y0 = start
    x1, y1 = end
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while(True):
        points.append((x0, y0))
        if(x0 == x1 and y0 == y1):
            break
        e2 = 2 * err
        if(e2 > -dy):
            err -= dy
            x0 += sx
        if(e2 < dx):
            err += dx
            y0 += sy
    return points


def find_points(matrix,center,wall_n=0):
    result = set()
    passed=set()
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if((i,j) in passed or (i,j) in result):
                continue
            if (i, j) == center:
                result.add((i, j))
                continue

            path = bresenham_line((i, j), center)

            xs, ys = zip(*path)
            try:
                jdg=np.where(matrix[xs, ys] != wall_n)[0]
            except:
                continue

            if(len(jdg)==0):
                for k in path:
                    result.add(k)
            else:
                for k in path[:jdg[-1]]:
                    passed.add(k)
                for k in path[jdg[-1]:]:
                    result.add(k)

    return result

# matrix = np.array([
#     [0, 5, 3, 4, 5],
#     [5, 0, 5, 0, 1],
#     [7, 5, 0, 5, 8],
#     [4, 5, 0, 5, 2],
#     [5, 1, 0, 2, 5]
# ])
#
# center = (2, 2)
#
# print(find_points(matrix,center,0))