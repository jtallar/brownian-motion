import sys
import json
import utils
import math
import objects as obj

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
small_dcm_rad = utils.read_config_param(
    config, "small_dcm_radius", lambda el : float(el), lambda el : el < 0)
small_dcm_count = utils.read_config_param(
    config, "small_dcm_count", lambda el : int(el), lambda el : el <= 0)
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
particle_origin_list = []
big_z_dist_list = []
big_z_dist_time_list = []

small_dcm_ids_set = set()
small_z_dist_sq_sum = 0
small_dcm_list = []
small_dcm_time_list = []
small_dcm_stop = False

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
            if not small_dcm_stop:
                # Calculate small particle DCM
                small_dcm_list.append(small_z_dist_sq_sum / len(small_dcm_ids_set))
                small_dcm_time_list.append(time)
                small_z_dist_sq_sum = 0

            # Update target_time
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
            
    # Perform only for initial positions
    if time == 0:
        # Accumulate kinetic energy only once, is always constant
        kinetic_energy += 0.5 * particle_mass[p_id] * v_mod * v_mod
        # Save particle positions
        particle_origin_list.append(part)
        # Save small particle ids for dcm if particle near center
        if p_id != big_particle_index and origin_part.center_distance(part) < small_dcm_rad and len(small_dcm_ids_set) < small_dcm_count:
            small_dcm_ids_set.add(p_id)

    # Check if particle in DCM and wall collision
    if p_id in small_dcm_ids_set and not small_dcm_stop and part.collides_with_wall(L):
        small_dcm_stop = True

    # Every dt, calculate DCM
    if time >= target_time:
        if p_id == big_particle_index:
            # Save z dist for big particle
            big_z_dist_list.append(particle_origin_list[p_id].center_distance(part))
            big_z_dist_time_list.append(time)
        elif not small_dcm_stop and p_id in small_dcm_ids_set:
            # Accum (z dist) ^ 2 for smaller particles
            small_z_dist_sq_sum += particle_origin_list[p_id].center_distance(part) ** 2

    p_id += 1

# Close files
dynamic_file.close()
static_file.close()

# Initialize plotting
utils.init_plotter()

# Calculate collision frequency. time is last time recorded
collision_freq = collision_count / time
# Get time bins. Eg: [0.0, dit, 2*dit, ...]
intercollision_time_bins = get_delta_bins(delta_t_intercol, 0, math.ceil(max_intercollision_time / delta_t_intercol))
# Get velocity bins. Eg: [0.0, dv, 2*dv, ...]
v_mod_bins = get_delta_bins(delta_v_mod, 0, math.ceil(max_small_v_mod / delta_v_mod))
# Calculate average intercollision time
avg_intercollision_time = sum_intercollision_time / collision_count
# Calculate small particles DCM
if len(small_dcm_ids_set) == small_dcm_count:
    # Plot small DCM to get m from linear regression
    coef = utils.plot_values_with_adjust(small_dcm_time_list[len(small_dcm_time_list)//2:], 'Time (s)', small_dcm_list[len(small_dcm_list)//2:], 'Small DCM (m^2)', 2, False)
    small_dcm_D = coef[0] / 2
    print(f'Small DCM D = {small_dcm_D}')    
else:
    print('Did not reach desired small_dcm_count, skipping DCM calculation...')

print(f'Collision count = {collision_count}\n'
      f'Collision frequency = {collision_freq}\n'
      f'Intercollision avg time = {avg_intercollision_time:.7E}\n'
      f'Constant kinetic energy = {kinetic_energy:.7E}\n')

# Plotings
if plot_boolean:
    # Small particles DCM was plotted before, will be showed when holding execution
    # utils.plot_values_with_adjust(small_dcm_time_list[len(small_dcm_time_list)//2:], 'Time (s)', small_dcm_list[len(small_dcm_list)//2:], 'Small DCM (m^2)', 2, False)
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



## Trayectorias = f(N) --> N, L, big_position_x_list, big_position_y_list
# Eventos = f(N) --> N, L, collision_count
# Prom Frec Col = f(N) --> N, L, collision_freq
# Prom t Intercol = f(N) --> N, L, avg_intercollision_time
#### Distribucion tiempos de colision con NMax
#### Distribucion |v| pequeñas inicial + ultimo tercio con NMax
## Trayectorias = f(T) --> K, L, init_max_v_mod, big_position_x_list, big_position_y_list
# DCM p chicas = f(T) --> K, L, init_max_v_mod, small_dcm_D
#### Grafico DCM p chicas con NMax y |v| <= 2.0
# DCM p grande = f(T) --> K, L, init_max_v_mod, big_z_dist_list, big_z_dist_time_list
# Grafico DCM p grande con NMax y |v| <= 2.0 --> K, L, big_z_dist_list, big_z_dist_time_list