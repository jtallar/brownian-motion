import sys
import json
import utils

WHITE = ' 255 255 255'
GREEN = ' 0 255 0'
RED = ' 255 0 0'
C = '1e-10 '

def write_corners(ovito_file, N, L):
    ovito_file.write(str(N+4))
    corners = '\n\n'+C+'0 0 0'+WHITE+'\n'+C+'0 '+str(L)+' 0'+WHITE+'\n'+C+str(L)+' 0 0'+WHITE+'\n'+C+str(L)+' '+str(L)+' 0'+WHITE+'\n'
    ovito_file.write(corners)

# Read params from config.json
with open("config.json") as file:
    config = json.load(file)

static_filename = utils.read_config_param(
    config, "static_file", lambda el : el, lambda el : False)
dynamic_filename = utils.read_config_param(
    config, "dynamic_file", lambda el : el, lambda el : False)

delta_t = utils.read_config_param(
    config, "delta_time", lambda el : float(el), lambda el : el < 0)
max_v_mod = utils.read_config_param(
    config, "max_v_mod", lambda el : float(el), lambda el : el <= 0)

dynamic_file = open(dynamic_filename, "r")

static_file = open(static_filename, "r")
N = int(static_file.readline())
L = float(static_file.readline())
particle_radius = []
for line in static_file:
    particle_radius.append(line.split()[0])

ovito_file = open("simu.xyz", "w")

# TODO: Mostramos el vector velocidad en la animacion?
restart = True
target_time = 0
p_id = 0
for linenum, line in enumerate(dynamic_file):
    if restart:
        time = float(line.rstrip())
        if time >= target_time:
            write_corners(ovito_file, N, L)
        restart = False
        p_id = 0
        continue
    if "*" == line.rstrip():
        restart = True
        if time >= target_time:
            target_time += delta_t
        # TODO: Ver que hago si en un dt no hay eventos. Esto pasa si aca time >= target_time
        continue

    if time >= target_time:
        line_vec = line.rstrip().split(' ')
        (x,y,r) = (line_vec[0]+' ', line_vec[1]+' ', particle_radius[p_id]+' ')
        (vx,vy) = (float(line_vec[2]), float(line_vec[3]))
        v_mod = (vx * vx + vy * vy) ** 0.5
        color = ' ' + str(v_mod/max_v_mod) + ' ' + str(1.0-v_mod/max_v_mod) + ' ' + str(1.0-v_mod/max_v_mod)
        ovi_line = r+x+y+str(p_id)+color+'\n'
        ovito_file.write(ovi_line)
        p_id += 1

print(f'Generated simu.xyz')

dynamic_file.close()
static_file.close()
ovito_file.close()