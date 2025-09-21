import numpy as np
import heapq


def astar(grid,start,goal,heuristic = 'manhattan'):
    start=tuple(start)
    goal=tuple(goal)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    h_func = {
        'manhattan': lambda r, c: abs(r - goal[0]) + abs(c - goal[1]),
        'euclidean': lambda r, c: np.sqrt((r - goal[0]) ** 2 + (c - goal[1]) ** 2),
        'chebyshev': lambda r, c: max(abs(r - goal[0]), abs(c - goal[1]))
    }[heuristic]

    open_heap = []
    heapq.heappush(open_heap, (0, start))

    came_from = {}
    cost_so_far = np.full(grid.shape, np.inf)
    cost_so_far[start] = 0

    while open_heap:
        current_cost, current = heapq.heappop(open_heap)

        if current == goal:
            break

        for dr, dc in directions:
            nr, nc = current[0] + dr, current[1] + dc

            if nr < 0 or nr >= grid.shape[0] or nc < 0 or nc >= grid.shape[1]:
                continue

            if grid[nr, nc] > 0:
                continue



            move_cost = 1.0
            new_cost = cost_so_far[current] + move_cost

            try:
                if new_cost < cost_so_far[nr, nc]:
                    cost_so_far[nr, nc] = new_cost
                    priority = new_cost + h_func(nr, nc)
                    heapq.heappush(open_heap, (priority, (nr, nc)))
                    came_from[(nr, nc)] = current
            except:
                pass

    else:
        return None

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return None
    path.append(start)
    path.reverse()

    return path


# grid = np.array(
#     [
#         [0,0,0,0,0,0,0],
#         [1,1,2,1,1,1,0],
#         [0,0,0,1,1,1,0],
#         [0,0,0,0,0,0,0],
#     ]
# )
# start = (0, 0)
# goal = (2, 2)
#
# path = astar(grid, start, goal)
# print(path)