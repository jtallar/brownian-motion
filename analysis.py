import sys
import json
import utils
import math

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

def get_delta_bins(delta, max_inclusive):
    return [x * delta for x in range(max_inclusive + 1)]

# Read params from config.json
with open("config.json") as file:
    config = json.load(file)

static_filename = utils.read_config_param(
    config, "static_file", lambda el : el, lambda el : False)
dynamic_filename = utils.read_config_param(
    config, "dynamic_file", lambda el : el, lambda el : False)

delta_t = utils.read_config_param(
    config, "delta_time", lambda el : float(el), lambda el : el <= 0)
delta_v_mod = utils.read_config_param(
    config, "delta_v_mod", lambda el : float(el), lambda el : el <= 0)
init_max_v_mod = utils.read_config_param(
    config, "max_v_mod", lambda el : float(el), lambda el : el <= 0)

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
time_list = []
(time, prev_time) = (0, 0)
sum_intercollision_time = 0

max_small_v_mod = 0
init_small_v_mod_list = []
all_small_v_mod_list = []

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
            sum_intercollision_time += time - prev_time
        # Add time to list
        time_list.append(time)
        continue
    if "*" == line.rstrip():
        restart = True
        # Take 1 event AFTER delta t
        if time >= target_time:
            target_time += delta_t
        continue

    line_vec = line.rstrip().split(' ')
    (x,y,r) = (float(line_vec[0]), float(line_vec[1]), particle_radius[p_id])
    (vx,vy) = (float(line_vec[2]), float(line_vec[3]))
    v_mod = (vx * vx + vy * vy) ** 0.5
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
    # Accumulate kinetic energy only once, is always constant
    if time == 0:
        kinetic_energy += 0.5 * particle_mass[p_id] * v_mod * v_mod
    p_id += 1

    # if time >= target_time:
    #     ovito_file.write()

# Close files
dynamic_file.close()
static_file.close()

# Calculate collision frequency. time is last time recorded
collision_freq = collision_count / time
# Get time bins. Eg: [0.0, dt, 2*dt, ...]
time_bins = get_delta_bins(delta_t, math.ceil(time / delta_t))
# Get velocity bins. Eg: [0.0, dv, 2*dv, ...]
v_mod_bins = get_delta_bins(delta_v_mod, math.ceil(max_small_v_mod / delta_v_mod))
# TODO: Check que se refieran a esto con promedio de tiempos de colision
# Calculate average intercollision time
avg_intercollision_time = sum_intercollision_time / collision_count

print(f'Collision count = {collision_count}\n'
      f'Collision frequency = {collision_freq}\n'
      f'Intercollision avg time = {avg_intercollision_time:.7E}\n'
      f'Constant kinetic energy = {kinetic_energy:.7E}\n')

# Plot histogram density
utils.init_plotter()
utils.plot_histogram_density(time_list, time_bins, 'Event time', 'Probability of events', 0, False)
utils.plot_histogram_density(init_small_v_mod_list, v_mod_bins, '|v| (m/s)', 'Probability of |v|', 1, False)
utils.plot_histogram_density(all_small_v_mod_list[:len(all_small_v_mod_list)//3], v_mod_bins, '|v| (m/s)', 'Probability of |v|', 1, False)
utils.hold_execution()