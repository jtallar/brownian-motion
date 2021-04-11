import sys
import genLib as gen

# Read params
if len(sys.argv) != 7:
    print(f'Wrong number of args!\n'
          f'You need to specify number of small particles (N), simulation area side (L), small particle radius (rp) and mass (mp), and big particle radius (RP) and mass (MP).\n'
          f'Must run with\n'
          f'\tpython3 generator.py N L rp mp RP MP')
    sys.exit(1)

N = int(sys.argv[1])
if N <= 100 or N >= 150:
    print('Number of small particles N must be between 101 and 149!')
    sys.exit(1)

L = int(sys.argv[2])
if L <= 0:
    print('Area side L must be positive!')
    sys.exit(1)

small_rad = float(sys.argv[3])
if small_rad < 0:
    print('Small particle radius must be positive or cero!')
    sys.exit(1)

small_mass = float(sys.argv[4])
if small_mass <= 0:
    print('Small particle mass must be positive!')
    sys.exit(1)

big_rad = float(sys.argv[5])
if big_rad <= small_rad:
    print('Big particle radius must be higher than small particle radius!')
    sys.exit(1)

big_mass = float(sys.argv[6])
if big_mass <= small_mass:
    print('Big particle mass must be higher than small particle mass!')
    sys.exit(1)

particles = gen.particles(N, L, small_rad, small_mass, big_rad, big_mass)

gen.data_files(L, particles)
print(f'Generated files static.txt and dynamic.txt')