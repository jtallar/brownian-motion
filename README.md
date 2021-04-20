# Brownian Motion

## What to Install
- `python3 -m pip install numpy`
- Download and install OVITO from: https://www.ovito.org/
### Versions
`python 3.8`

## Configuration
Everything is configured by modifying `config.json`. Available configuration keys are:
   - `static_file`: static file filepath
   - `dynamic_file`: dynamic file filepath
   - `N`: number of small particles, 100 < N < 150
   - `L`: simulation area side, L > 0
   - `small_radius`: small particle radius, rp >= 0
   - `small_mass`: small particle mass, mp > 0
   - `big_radius`: big particle radius, RP > rp
   - `big_mass`: big particle mass, MP > mp
   - `max_v_mod`: initial max particle speed module, vm > 0
   - `max_events`: maximum amount of events to analyze, maxEvents > 0
   - `delta_time_animation`: minimum timestep between events for animation, dt > 0
   - `delta_time_analysis`: minimum timestep between events for analysis, dt > 0
   - `delta_time_intercollition`: bin width for intercollision plot, dti > 0
   - `delta_v_mod`: timestep between speeds in histogram, dv > 0
   - `small_dcm_count`: number of particles to select for small particle DCM calculation, small_dcm_count > 0
   - `plot`: determines whether to plot or not single analysis, must be true or false

## Particle generator
To generate initial particle positions by creating `static_file` and `dynamic_file`. 
Generates N small particles with random positions and speeds, and 1 stopped big particle at the center. If N cannot be reached in a number of iterations, resets and tries again.
Run `python3 generator.py`, using the following parameters from `config.json`:

   `static_file`, `dynamic_file`, `N`, `L`, `small_radius`, `small_mass`, `big_radius`, `big_mass`, `max_v_mod`

## Simulation
To generate executable and run the life simulation
1. Run `./prepare.sh` in root to generate executable (only required once).
2. Run `./target/tp3-simu-1.0/brownian-motion.sh`, using the following parameters from `config.json`:
   
   `static_file`, `dynamic_file`, `max_events`

Output will be appended to `dynamic_file`, adding time and particle position and velocity for each event.

## Animation Tool
Generates `simu.xyz` using information from `static_file` and `dynamic_file`.
Run `python3 animator.py`, using the following parameters from `config.json`:

   `static_file`, `dynamic_file`, `delta_time_animation`, `max_v_mod`

To view the animation, you must open `simu.xyz` with Ovito:
`./bin/ovito simu.xyz`. 

Particles will be colored in a scale of colors from cian (static particles) to red (high velocity module), showing how fast each particle is going.

### Column Mapping 
Configure the file column mapping as follows:
   - Column 1 - Radius
   - Column 2 - Position - X
   - Column 3 - Position - Y
   - Column 4 - Particle Identifier
   - Column 5 - Color - R
   - Column 6 - Color - G
   - Column 7 - Color - B

# Analysis Tools
Analysis can be performed in multiple ways.

## analysis.py
Generate plots and metrics given a single simulation file as input.
Run `python3 analysis.py [out_filename]`, using the following parameters from `config.json`:

   `static_file`, `dynamic_file`, `delta_time_analysis`, `delta_time_intercollition`, `delta_v_mod`, `max_v_mod`, `small_dcm_count`, `plot`

If a filename is provided, some metrics will be written to filename. If plot is false, then no graphs are plotted.

Metrics calculated are:
- Small DCM D (single simulation)
- Collision count
- Collision frequency
- Average time between collisions
- Kinetic energy

Plots shown are:
- Small particles DCM dependant on time for last half
- Probability distribution of times between collisions
- Initial probability distribution of |v|
- Probability distribution of |v| in last third of simulation
- Big particle trajectory (with and without zooming in)

## multipleAnalysis.py
Run analysis on multiple simulation files to plot metrics according to the different iterations or values. It receives a root directory, where each folder should correspond to a parameter value (eg: `101`) with multiple data simulations of that value.
`python3 multipleAnalysis.py root_directory (N|T) [save_dir]`

The second parameter indicates mode, whether simulations have a varying number of small particles (N) or temperature (T, by changing initial `max_v_mod`). If save_dir is provided, the plots are saved as `.png` in that directory.

If mode is N, plots shown are:
- Big particle trajectory, taking one repetition for each N
- Collision count dependant on N
- Collision frequency dependant on N
- Average time between collisions dependant on N

If mode is T, plots shown are:
- Big particle trajectory, taking one repetition for each T
- Small particles DCM D value dependant on initial max_v_mod
- Big particle DCM dependant on time for `max_v_mod` = 2.0, for last half of simulation
- Big particle DCM D value dependant on initial max_v_mod
- Small particles DCM dependant on time for `max_v_mod` = 2.0, for last half of simulation
- Small particles DCM D value dependant on initial max_v_mod

### multipleN.sh
This script can be used to run generation and simulation multiple times, given a starting N value, a step to increase N each iteration and the number of repetitions (>= 2) to run for each N in range.
`./multipleN.sh N_start N_step repetitions`

The script runs the simulation for each available N from `N_start` to the highest `N_start + K * N_step` that is lower or equal than 136. Then, it runs `multipleAnalysis.py` with the output data directory. The plots can be found at directory `pics_N`. Values corresponding to each plot can also be found at file `pics_N/outN.txt`.

### multipleT.sh
This script can be used to run generation and simulation multiple times, given a starting max velocity module value, a step to increase module each iteration, a maximum module and the number of repetitions (>= 2) to run for each module in range.
`./multipleT.sh max_v_mod_start max_v_mod_step max_v_mod_stop repetitions`

The script runs the simulation for each available velocity module from `max_v_mod_start` to the highest `max_v_mod_start + K * max_v_mod_step` that is lower or equal than `max_v_mod_stop`. Then, it runs `multipleAnalysis.py` with the output data directory. The plots can be found at directory `pics_T`. Values corresponding to each plot can also be found at file `pics_T/outN.txt`.