import numpy as np
import random
import math
import objects as obj

MAX_ITERATIONS = 100000

def generate_speed(max_v_mod):
    v_mod = random.uniform(0, max_v_mod)
    angle = random.uniform(0, 2 * math.pi)
    return (math.cos(angle) * v_mod, math.sin(angle) * v_mod)

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
    total_k = 0
    (count, iterations) = (0, 0)
    while count < n and iterations < MAX_ITERATIONS:
        iterations += 1
        # Generate random x, y
        (x, y) = (random.uniform(small_r, side - small_r), random.uniform(small_r, side - small_r))
        # Row, Col go from 1 to M
        (row, col) = get_row_col(x, y, cell_width, M)
        part = obj.Particle(count + 1, x, y, 0.0, 0.0, small_r, small_m)

        # If superposition exists, skip and regenerate new particle
        if check_superposition(part, row, col, head_matrix):
            continue

        (part.vx, part.vy) = generate_speed(max_v_mod)
        total_k += 0.5 * small_m * (part.vx ** 2 + part.vy ** 2)

        head_matrix[row][col] = obj.ParticleNode(part, head_matrix[row][col])
        part_list.append(part)
        
        count += 1

    print(f'Generated {count + 1} particles totalling {total_k:.7E}J')

    return part_list

#Generate dynamic and static files, reading N and L from arg
def data_files(side, particles, static_filename, dynamic_filename):
    static_file = open(static_filename, "w")
    static_file.write(str(len(particles)))
    static_file.write('\n')
    static_file.write(str(side))

    dynamic_file = open(dynamic_filename, "w")
    dynamic_file.write('0')       # dynamic time

    for p in particles:
        # Write static file
        static_file.write('\n%.4F %.4F' % (p.r, p.m))

        # Write dynamic file
        dynamic_file.write('\n%.7E %.7E %.7E %.7E' % (p.x, p.y, p.vx, p.vy))

    static_file.close()
    dynamic_file.close()
