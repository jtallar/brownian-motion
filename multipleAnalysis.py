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

