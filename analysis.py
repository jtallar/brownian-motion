import sys
import json
import utils
import math
import objects as obj
import analyzerFun as anl

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

metrics = anl.analyze(static_filename, dynamic_filename, delta_t, delta_t_intercol, delta_v_mod, small_dcm_rad, small_dcm_count, plot_boolean)

# If out filename provided, print to file
if out_filename:
    with open(out_filename, "w") as file:
        file.write(
            f'{metrics.N}\n'
            f'{init_max_v_mod}\n'
            f'{metrics.collision_count}\n'
            f'{metrics.collision_freq}\n'
            f'{metrics.avg_intercollision_time:.7E}\n'
            f'{metrics.kinetic_energy:.7E}\n'
        )



## Trayectorias = f(N) --> N, L, big_position_x_list, big_position_y_list
# Eventos = f(N) --> N, L, collision_count
# Prom Frec Col = f(N) --> N, L, collision_freq
# Prom t Intercol = f(N) --> N, L, avg_intercollision_time
#### Distribucion tiempos de colision con NMax
#### Distribucion |v| pequeñas inicial + ultimo tercio con NMax
## Trayectorias = f(T) --> K, L, big_position_x_list, big_position_y_list
# DCM p chicas = f(T) --> K, L, small_dcm_D
#### Grafico DCM p chicas con NMax y |v| <= 2.0
# DCM p grande = f(T) --> K, L, big_z_dist_list, big_z_dist_time_list
# Grafico DCM p grande con NMax y |v| <= 2.0 --> K, L, big_z_dist_list, big_z_dist_time_list