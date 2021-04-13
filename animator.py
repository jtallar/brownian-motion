import sys

WHITE = ' 255 255 255'
GREEN = ' 0 255 0'
RED = ' 255 0 0'
C = '1e-10 '

def write_corners(ovito_file, N, L):
    ovito_file.write(str(N+4))
    corners = '\n\n'+C+'0 0 0'+WHITE+'\n'+C+'0 '+str(L)+' 0'+WHITE+'\n'+C+str(L)+' 0 0'+WHITE+'\n'+C+str(L)+' '+str(L)+' 0'+WHITE+'\n'
    ovito_file.write(corners)

# Read params
if len(sys.argv) != 2:
    print(f'Wrong number of args!\n'
          f'You need to specify delta t (dt).\n'
          f'Must run with\n'
          f'\tpython3 animator.py dt')
    sys.exit(1)

delta_t = float(sys.argv[1])
if delta_t < 0:
    print('Delta t must be positive or zero (print all events)!')
    sys.exit(1)

dynamic_file = open("dynamic.txt", "r")

static_file = open("static.txt", "r")
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
        color = WHITE
        ovi_line = r+x+y+str(p_id)+' '+color+'\n'
        ovito_file.write(ovi_line)
        p_id += 1

print(f'Generated simu.xyz')

dynamic_file.close()
static_file.close()
ovito_file.close()