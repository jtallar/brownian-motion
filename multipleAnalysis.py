import sys
import json
import os
import objects as obj
import utils
import analyzerFun as anl

if len(sys.argv) < 3:
    print("Must run with python multipleAnalysis.py root_directory (N|T) [save_dir]")
    sys.exit(1)

save_dir = None
if len(sys.argv) == 4:
    if sys.argv[3][-1] == '/':
        save_dir = sys.argv[3][:-1:]
    else:
        save_dir = sys.argv[3]
    # Create directory if not exists
    try:
        os.mkdir(save_dir)
    except FileExistsError as exc:
        print("save_dir already exists. continuing...")

if sys.argv[1][-1] == '/':
    root_directory = sys.argv[1][:-1:]
else:
    root_directory = sys.argv[1]

mode = sys.argv[2]
if mode != 'N' and mode != 'T':
    print("Invalid mode! Must use N or T to indicate which parameter is variable.")
    sys.exit()

# Read params from config.json
with open("config.json") as file:
    config = json.load(file)

delta_t = utils.read_config_param(
    config, "delta_time_analysis", lambda el : float(el), lambda el : el <= 0)
delta_t_intercol = utils.read_config_param(
    config, "delta_time_intercollition", lambda el : float(el), lambda el : el <= 0)
delta_v_mod = utils.read_config_param(
    config, "delta_v_mod", lambda el : float(el), lambda el : el <= 0)
small_dcm_rad = utils.read_config_param(
    config, "small_dcm_radius", lambda el : float(el), lambda el : el < 0)
small_dcm_count = utils.read_config_param(
    config, "small_dcm_count", lambda el : int(el), lambda el : el <= 0)

obs_dict = {}
root_entries = os.listdir(root_directory)
for directory in root_entries:
    directory = root_directory + '/' + directory
    entries = os.listdir(directory)
    init_param = int(directory.split('/')[-1])
    static_filename = directory + '/static.txt'
    obs_dict[init_param] = []
    for filename in entries:
        if filename == 'static.txt': continue
        dynamic_filename = directory + '/' + filename
        obs_dict[init_param].append(anl.analyze(static_filename, dynamic_filename, delta_t, delta_t_intercol, delta_v_mod, small_dcm_rad, small_dcm_count, False))

# Get summarized values list
keys = list(obs_dict.keys())
keys.sort()
sum_values = [obj.Summary(obs_list, param) for param, obs_list in obs_dict.items()]
sum_values.sort(key=lambda x: x.param)
L = sum_values[0].L

utils.init_plotter()

if mode == 'N':
    N_values = [x.N for x in sum_values]
    # Plot multiple trayectories for different N
    trayectories_x = [x.big_position_x_list for x in sum_values]
    trayectories_y = [x.big_position_y_list for x in sum_values]
    save_name = save_dir + '/trayectories.png' if save_dir else None
    colors = utils.plot_multiple_values(trayectories_x, 'Big particle X (m)', trayectories_y, 'Big particle Y (m)', 1, False, min_val=0, max_val=L, save_name=save_name)
    for i, col in enumerate(colors):
        utils.print_with_color("N = " + str(N_values[i]) + ", color = " + col, col)
    # Plot collision_count = f(N)
    save_name = save_dir + '/collision_count.png' if save_dir else None
    utils.plot_error_bars_summary(keys, 'N', sum_values, 'collision_count', 'Collision count', 1, sci=False, save_name=save_name)
    # Plot avg_collision_freq = f(N)

    # Plot avg_intercollision_time = f(N)

else:
    print("Not done yet")
    # Plot multiple trayectories for different K

    # Plot small_dcm_d = f(T)

    # Plot big_dcm

    # Calculate big_dcm_d

if save_dir:
    print(f'Saved plots in {save_dir}/')
else:
    # Hold execution until all plots are closed
    utils.hold_execution()