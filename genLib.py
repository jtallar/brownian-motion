import numpy as np
import random
import math
import objects as obj

# TODO: Check uniform distribution OK
def generate_speed(max_v_mod):
    v_mod = random.uniform(0, max_v_mod)
    vx = random.uniform(-v_mod, v_mod)
    vy_mod = math.sqrt(v_mod ** 2 - vx ** 2)
    vy = vy_mod * (1 if random.random() > 0.5 else -1)
    return (vx, vy)

def check_superposition(part, row, col, matrix):
    for r in range(row - 1, row + 2):
        for c in range(col - 1, col + 2):
            cell_cur = matrix[r][c]
            while cell_cur:
                if part.border_distance(cell_cur.particle) <= 0:
                    return True
                cell_cur = cell_cur.next
    
    return False

def get_row_col(x, y, cell_width, M):
    cell_index = int(x / cell_width) + int(y / cell_width) * M
    return (int(cell_index / M + 1), int(cell_index % M + 1))

# Generate random particles
def particles(n, side, max_v_mod, small_r, small_m, big_r, big_m):
    part_list = []
    
    # Matrix with list of particles for each cell to check collision
    M = int(side / (big_r + small_r * 1.1))
    cell_width = side / M
    head_matrix = np.full((M + 2, M + 2), None)

    # Create big particle
    part = obj.Particle(0, side / 2.0, side / 2.0, 0, 0, big_r, big_m)
    (row, col) = get_row_col(part.x, part.y, cell_width, M)
    head_matrix[row][col] = obj.ParticleNode(part, head_matrix[row][col])
    part_list.append(part)

    # Create n smaller particles
    count = 0
    while count < n:
        # TODO: Check x, y limits (using r)
        (x, y) = (random.uniform(small_r, side - small_r), random.uniform(small_r, side - small_r))
        # Row, Col go from 1 to M
        (row, col) = get_row_col(x, y, cell_width, M)
        part = obj.Particle(count + 1, x, y, 0.0, 0.0, small_r, small_m)

        # If superposition exists, skip and regenerate new particle
        if check_superposition(part, row, col, head_matrix):
            continue

        (part.vx, part.vy) = generate_speed(max_v_mod)

        head_matrix[row][col] = obj.ParticleNode(part, head_matrix[row][col])
        part_list.append(part)
        
        count += 1

    return part_list

#Generate dynamic and static files, reading N and L from arg
def data_files(side, particles):
    static_file = open("static.txt", "w")
    static_file.write(str(len(particles)))
    static_file.write('\n')
    static_file.write(str(side))

    dynamic_file = open("dynamic.txt", "w")
    dynamic_file.write('0')       # dynamic time

    for p in particles:
        # Write static file
        static_file.write('\n%.4F %.4F' % (p.r, p.m))

        # Write dynamic file
        dynamic_file.write('\n%.7E %.7E %.7E %.7E' % (p.x, p.y, p.vx, p.vy))

    static_file.close()
    dynamic_file.close()
