import sys
import json
import utils
import math
import objects as obj

# 3.0
# Estudiar distintos comportamientos variando el N
# TODO: Tomamos #Eventos = f(N)? Trayectorias?

# 3.1
# Frecuencia de colisiones --> Nro de colisiones por unidad de tiempo
# Promedio de tiempos de colision (intercolision?)
# Distribucion de probabilidades de los tiempos de colision (o PDF)

# 3.2
# PDF del |v| de las particulas pequeñas en el ultimo tercio de la sim
# PDF del |v| de las particulas pequeñas inicialmente (t=0)

# 3.3
# Trayectoria de particula grande para distintas temperaturas (K)
# Como se cambia la temperatura en este sistema?

# 3.4
# Estimar el coeficiente de difusion D de la particula grande (DCM=f(t))
# Estimar el coeficiente de difusion D de las particulas pequeñas (DCM=f(t))
# Realizar el ajuste del D con el metodo generico de la teorica 0
# Describir como se eligen los tiempos en los que se calcula el DCM (dt)
# Para estas cosas, solo tomar hasta que la particula colisiona con la pared, 
# tanto para grandes como para chicas. Tomar solo la segunda mitad de sus trayectorias

def get_delta_bins(delta, start, max_mult_inclusive):
    return [x * delta for x in range(start, max_mult_inclusive + 1)]

# Read out filename param if provided
out_filename = None
if len(sys.argv) >= 2:
    out_filename = sys.argv[1]

# Read params from config.json
with open("config.json") as file:
    config = json.load(file)

static_filename = utils.read_config_param(
    config, "static_file", lambda el : el, lambda el : False)
dynamic_filename = utils.read_config_param(
    config, "dynamic_file", lambda el : el, lambda el : False)

delta_t = utils.read_config_param(
    config, "delta_time_analysis", lambda el : float(el), lambda el : el <= 0)
delta_t_intercol = utils.read_config_param(
    config, "delta_time_intercollition", lambda el : float(el), lambda el : el <= 0)
delta_v_mod = utils.read_config_param(
    config, "delta_v_mod", lambda el : float(el), lambda el : el <= 0)
init_max_v_mod = utils.read_config_param(
    config, "max_v_mod", lambda el : float(el), lambda el : el <= 0)
plot_boolean = utils.read_config_param(
    config, "plot", lambda el : bool(el), lambda el : False)

dynamic_file = open(dynamic_filename, "r")

static_file = open(static_filename, "r")
N = int(static_file.readline())
L = float(static_file.readline())
(max_radius, big_particle_index) = (-1.0, -1)
particle_radius = []
particle_mass = []
for index, line in enumerate(static_file):
    line_vec = line.rstrip().split()
    particle_radius.append(float(line_vec[0]))
    particle_mass.append(float(line_vec[1]))
    if particle_radius[index] > max_radius:
        max_radius = particle_radius[index]
        big_particle_index = index

restart = True
target_time = 0.0
p_id = 0
# Start collision count in -1 as we have t0, no collision yet
collision_count = -1
(time, prev_time) = (0, 0)
sum_intercollision_time = 0
intercollision_time_list = []
max_intercollision_time = 0

max_small_v_mod = 0
init_small_v_mod_list = []
all_small_v_mod_list = []

big_position_x_list = []
big_position_y_list = []

origin_part = obj.Particle(-1, L / 2, L / 2, 0, 0, 0, 0)
big_z_dist_list = []
big_z_dist_time_list = []

kinetic_energy = 0
for linenum, line in enumerate(dynamic_file):
    if restart:
        prev_time = time
        time = float(line.rstrip())
        # if time >= target_time:
        #     write_corners(ovito_file, N, L)
        # Reset variables
        restart = False
        p_id = 0
        # Add a collision
        collision_count += 1
        # If there already were any collisions, acum intercollision time
        if collision_count > 0:
            intercollision_time = time - prev_time
            sum_intercollision_time += intercollision_time
            # Add intercollision time to list
            intercollision_time_list.append(intercollision_time)
            # Save max intercollision time
            if intercollision_time > max_intercollision_time:
                max_intercollision_time = intercollision_time
        continue
    if "*" == line.rstrip():
        restart = True
        # Take 1 event AFTER delta t
        if time >= target_time:
            target_time += delta_t
            if time >= target_time:
                print('Delta t is too small, there were no events in a gap! Exiting...')
                sys.exit(1)
        continue

    line_vec = line.rstrip().split(' ')
    # (id, x=0, y=0, vx=0, vy=0, r=0, m=0):
    part = obj.Particle(p_id, float(line_vec[0]), float(line_vec[1]), float(line_vec[2]), float(line_vec[3]), particle_radius[p_id], particle_mass[p_id])
    v_mod = part.get_v_mod()
    # Save small particle values
    if p_id != big_particle_index:
        # Save initial v_mod values
        if time == 0:
            init_small_v_mod_list.append(v_mod)
        # Save all v_mod values
        all_small_v_mod_list.append(v_mod)
        # Save max v_mod
        if v_mod > max_small_v_mod:
            max_small_v_mod = v_mod
    else:
        # Save big particle position
        big_position_x_list.append(part.x)
        big_position_y_list.append(part.y)
        # Every dt, calculate DCM for big particle
        if time >= target_time:
            big_z_dist_list.append(origin_part.center_distance(part))
            big_z_dist_time_list.append(time)
            
    # Accumulate kinetic energy only once, is always constant
    if time == 0:
        kinetic_energy += 0.5 * particle_mass[p_id] * v_mod * v_mod
    p_id += 1

# Close files
dynamic_file.close()
static_file.close()

# Calculate collision frequency. time is last time recorded
collision_freq = collision_count / time
# Get time bins. Eg: [0.0, dit, 2*dit, ...]
intercollision_time_bins = get_delta_bins(delta_t_intercol, 0, math.ceil(max_intercollision_time / delta_t_intercol))
# Get velocity bins. Eg: [0.0, dv, 2*dv, ...]
v_mod_bins = get_delta_bins(delta_v_mod, 0, math.ceil(max_small_v_mod / delta_v_mod))
# Calculate average intercollision time
avg_intercollision_time = sum_intercollision_time / collision_count

print(f'Collision count = {collision_count}\n'
      f'Collision frequency = {collision_freq}\n'
      f'Intercollision avg time = {avg_intercollision_time:.7E}\n'
      f'Constant kinetic energy = {kinetic_energy:.7E}\n')

# Plotings
if plot_boolean:
    utils.init_plotter()
    # Probability of intercollision time
    utils.plot_histogram_density(intercollision_time_list, intercollision_time_bins, 'Time between collision (s)', 'Probability of time', 1, True)
    # Initial probability of |v|
    utils.plot_histogram_density(init_small_v_mod_list, v_mod_bins, '|v| (m/s)', 'Probability of |v|', 1, False)
    # Probability of |v| in last third
    utils.plot_histogram_density(all_small_v_mod_list[2*len(all_small_v_mod_list)//3:], v_mod_bins, '|v| (m/s)', 'Probability of |v|', 1, False)
    # Big particle trayectory zoomed
    utils.plot_values(big_position_x_list, 'Big particle X (m)', big_position_y_list, 'Big particle Y (m)', 1, False)
    # Big particle trayectory full box size
    utils.plot_values(big_position_x_list, 'Big particle X (m)', big_position_y_list, 'Big particle Y (m)', 1, False, min_val=0, max_val=L)
    utils.hold_execution()

# If out filename provided, print to file
if out_filename:
    with open(out_filename, "w") as file:
        file.write(
            f'{N}\n'
            f'{init_max_v_mod}\n'
            f'{collision_count}\n'
            f'{collision_freq}\n'
            f'{avg_intercollision_time:.7E}\n'
            f'{kinetic_energy:.7E}\n'
        )