import sys
import json
import utils

# 3.0
# Estudiar distintos comportamientos variando el N

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


# Read params from config.json
with open("config.json") as file:
    config = json.load(file)

static_filename = utils.read_config_param(
    config, "static_file", lambda el : el, lambda el : False)
dynamic_filename = utils.read_config_param(
    config, "dynamic_file", lambda el : el, lambda el : False)

# For analysis, delta_time MUST NOT be 0
delta_t = utils.read_config_param(
    config, "delta_time", lambda el : float(el), lambda el : el <= 0)
max_v_mod = utils.read_config_param(
    config, "max_v_mod", lambda el : float(el), lambda el : el <= 0)

dynamic_file = open(dynamic_filename, "r")

static_file = open(static_filename, "r")
N = int(static_file.readline())
L = float(static_file.readline())
particle_radius = []
for line in static_file:
    particle_radius.append(line.split()[0])


restart = True
target_time = 0.0
p_id = 0
# Start collision count in -1 as we have t0, no collision yet
collision_count = -1
collision_bin_dic = {}
time_list = []
for linenum, line in enumerate(dynamic_file):
    if restart:
        time = float(line.rstrip())
        # if time >= target_time:
        #     write_corners(ovito_file, N, L)
        restart = False
        p_id = 0
        collision_count += 1
        time_list.append(time)
        bin_number = int(time / delta_t)
        if bin_number not in collision_bin_dic:
            collision_bin_dic[bin_number] = 0
        collision_bin_dic[bin_number] += 1
        continue
    if "*" == line.rstrip():
        restart = True
        # Take 1 event AFTER delta t
        if time >= target_time:
            target_time += delta_t
        continue

    if time >= target_time:
        line_vec = line.rstrip().split(' ')
        (x,y,r) = (float(line_vec[0]), float(line_vec[1]), float(particle_radius[p_id]))
        (vx,vy) = (float(line_vec[2]), float(line_vec[3]))
        v_mod = (vx * vx + vy * vy) ** 0.5
        p_id += 1

# Close files
dynamic_file.close()
static_file.close()

# time is last time recorded
collision_freq = collision_count / time
bin_count = int(time / delta_t) + 1

print(collision_bin_dic)
print(f'Collision count = {collision_count}\n'
      f'Collision frequency = {collision_freq}')

utils.init_plotter()
utils.plot_histogram(time_list, bin_count, 'Event time', 'Probability of events', 0, False)
utils.hold_execution()