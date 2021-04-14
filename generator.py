import sys
import json
import genLib as gen
import utils

# Read params from config.json
with open("config.json") as file:
    config = json.load(file)

static_filename = utils.read_config_param(
    config, "static_file", lambda el : el, lambda el : False)
dynamic_filename = utils.read_config_param(
    config, "dynamic_file", lambda el : el, lambda el : False)

N = utils.read_config_param(
    config, "N", lambda el : int(el), lambda el : el <= 100 or el >= 150)
L = utils.read_config_param(
    config, "L", lambda el : float(el), lambda el : el <= 0)
small_rad = utils.read_config_param(
    config, "small_radius", lambda el : float(el), lambda el : el < 0)
small_mass = utils.read_config_param(
    config, "small_mass", lambda el : float(el), lambda el : el <= 0)
big_rad = utils.read_config_param(
    config, "big_radius", lambda el : float(el), lambda el : el <= small_rad)
big_mass = utils.read_config_param(
    config, "big_mass", lambda el : float(el), lambda el : el <= small_mass)
max_v_mod = utils.read_config_param(
    config, "max_v_mod", lambda el : float(el), lambda el : el <= 0)

particles = gen.particles(N, L, max_v_mod, small_rad, small_mass, big_rad, big_mass)

gen.data_files(L, particles, static_filename, dynamic_filename)
print(f'Generated files {static_filename} and {dynamic_filename}')