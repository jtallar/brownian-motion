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
small_dcm_count = utils.read_config_param(
    config, "small_dcm_count", lambda el : int(el), lambda el : el <= 0)

obs_dict = {}
root_entries = os.listdir(root_directory)
for directory in root_entries:
    directory = root_directory + '/' + directory
    entries = os.listdir(directory)
    init_param = float(directory.split('/')[-1])
    static_filename = directory + '/static.txt'
    obs_dict[init_param] = []
    for filename in entries:
        if filename == 'static.txt': continue
        dynamic_filename = directory + '/' + filename
        print(dynamic_filename)
        obs_dict[init_param].append(anl.analyze(static_filename, dynamic_filename, delta_t, delta_t_intercol, delta_v_mod, small_dcm_count, False))

# Get summarized values list
keys = list(obs_dict.keys())
keys.sort()
sum_values = [obj.Summary(obs_list, param, mode == 'T') for param, obs_list in obs_dict.items()]
sum_values.sort(key=lambda x: x.param)
L = sum_values[0].L

utils.init_plotter()

if mode == 'N':
    # Plot multiple trayectories for different N
    N_values = [x.N for x in sum_values]
    trayectories_x = [x.big_position_x_list for x in sum_values]
    trayectories_y = [x.big_position_y_list for x in sum_values]
    save_name = save_dir + '/trayectories_N.png' if save_dir else None
    colors = utils.plot_multiple_values(trayectories_x, 'Big particle X (m)', trayectories_y, 'Big particle Y (m)', 1, sci=False, min_val=0, max_val=L, save_name=save_name)
    for i, col in enumerate(colors):
        utils.print_with_color(f"N = {N_values[i]}, color = {col}", col)
    # Plot collision_count = f(N)
    save_name = save_dir + '/collision_count.png' if save_dir else None
    utils.plot_error_bars_summary(keys, 'N', sum_values, 'collision_count', 'Collision count', 1, sci_y=True, save_name=save_name)
    # Plot avg_collision_freq = f(N)
    save_name = save_dir + '/collision_freq.png' if save_dir else None
    utils.plot_error_bars_summary(keys, 'N', sum_values, 'collision_freq', 'Average collision frequency (1/s)', 1, sci_y=False, save_name=save_name)
    # Plot avg_intercollision_time = f(N)
    save_name = save_dir + '/avg_intercollision_time.png' if save_dir else None
    utils.plot_error_bars_summary(keys, 'N', sum_values, 'avg_intercollision_time', 'Average intercollision time (s)', 1, sci_y=True, save_name=save_name)

else:
    # Plot multiple trayectories for different K
    K_values = [x.last_kinetic_energy for x in sum_values]
    trayectories_x = [x.big_position_x_list for x in sum_values]
    trayectories_y = [x.big_position_y_list for x in sum_values]
    save_name = save_dir + '/trayectories_K.png' if save_dir else None
    colors = utils.plot_multiple_values(trayectories_x, 'Big particle X (m)', trayectories_y, 'Big particle Y (m)', 1, sci=False, min_val=0, max_val=L, save_name=save_name)
    for i, col in enumerate(colors):
        utils.print_with_color(f"K = {K_values[i]:.7E}, color = {col}", col)
    # Plot small_dcm_d = f(T)
    save_name = save_dir + '/small_dcm_D.png' if save_dir else None
    utils.plot_error_bars_summary(keys, 'Max initial |v|', sum_values, 'small_dcm_D', 'Small particles D (m^2/s)', 1, sci_y=True, save_name=save_name)
    # Plot big_dcm when Max initial |v| = 2.0 if found (if not, take last one)
    big_dcm_list = sum_values[-1].big_dcm_list
    big_dcm_time_list = sum_values[-1].big_dcm_time_list
    for x in sum_values:
        if x.param == 2.0:
            big_dcm_list = x.big_dcm_list
            big_dcm_time_list = x.big_dcm_time_list
            print("Plotting Big DCM for |v| = 2.0")
            break
    save_name = save_dir + '/big_dcm_2.0.png' if save_dir else None
    coef = utils.plot_values_with_adjust(big_dcm_time_list[len(big_dcm_time_list)//2:], 'Time (s)', big_dcm_list[len(big_dcm_list)//2:], 'Big DCM (m^2)', 2, sci=False, plot=True, save_name=save_name)
    big_dcm_D = coef / 2
    print(f'Big DCM D = {big_dcm_D}')
    # Calculate big_dcm_d
    big_DCM_Ds = [utils.plot_values_with_adjust(x.big_dcm_time_list[len(x.big_dcm_time_list)//2:], None, x.big_dcm_list[len(x.big_dcm_list)//2:], None, plot=False) / 2 for x in sum_values]
    save_name = save_dir + '/big_dcm_D.png' if save_dir else None
    utils.plot_values(keys, 'Max initial |v|', big_DCM_Ds, 'Big particle D', 2, sci_y=True, save_name=save_name)
    # Plot small_dcm when Max initial |v| = 2.0 if found (if not, take last one)
    small_dcm_list = sum_values[-1].small_dcm_list
    small_dcm_time_list = sum_values[-1].small_dcm_time_list
    for x in sum_values:
        if x.param == 2.0:
            small_dcm_list = x.small_dcm_list
            small_dcm_time_list = x.small_dcm_time_list
            print("Plotting Small DCM for |v| = 2.0")
            break
    save_name = save_dir + '/small_dcm_2.0.png' if save_dir else None
    coef = utils.plot_values_with_adjust(small_dcm_time_list[len(small_dcm_time_list)//2:], 'Time (s)', small_dcm_list[len(small_dcm_list)//2:], 'Small DCM (m^2)', 2, sci=False, plot=True, save_name=save_name)
    small_dcm_D = coef / 2
    print(f'Small DCM D = {small_dcm_D}')
    # Calculate small_dcm_d
    big_DCM_Ds = [utils.plot_values_with_adjust(x.small_dcm_time_list[len(x.small_dcm_time_list)//2:], None, x.small_dcm_list[len(x.small_dcm_list)//2:], None, plot=False) / 2 for x in sum_values]
    save_name = save_dir + '/small_dcm_D.png' if save_dir else None
    utils.plot_values(keys, 'Max initial |v|', big_DCM_Ds, 'Small particles D', 2, sci_y=True, save_name=save_name)

if save_dir:
    print(f'Saved plots in {save_dir}/')
else:
    # Hold execution until all plots are closed
    utils.hold_execution()