WHITE = ' 255 255 255'
GREEN = ' 0 255 0'
RED = ' 255 0 0'
C = '1e-10 '

dynamic_file = open("dynamic.txt", "r")
dynamic_file.readline()

static_file = open("static.txt", "r")
N = int(static_file.readline())
L = float(static_file.readline())

ovito_file = open("simu.xyz", "w")
ovito_file.write(str(N+4))
corners = '\n\n'+C+'0 0 0'+WHITE+'\n'+C+'0 '+str(L)+' 0'+WHITE+'\n'+C+str(L)+' 0 0'+WHITE+'\n'+C+str(L)+' '+str(L)+' 0'+WHITE
ovito_file.write(corners)

for i in range(N):
    line = dynamic_file.readline().split(' ')
    (x,y,r) = (line[0]+' ', line[1]+' ', static_file.readline().split()[0]+' ')
    p_id = str(i)+' '
    color = WHITE
    ovi_line = '\n'+r+x+y+p_id+color
    ovito_file.write(ovi_line)

print(f'Generated simu.xyz')

dynamic_file.close()
static_file.close()
ovito_file.close()