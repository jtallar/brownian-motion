# Brownian Motion

## What to Install
- `python3 -m pip install numpy`
- Download and install OVITO from: https://www.ovito.org/
### Versions
`python 3.8`

## Particle generator
To generate initial particle positions by creating `static.txt` and `dynamic.txt`. 
Generates N small particles with random positions and speeds, and 1 stopped big particle at the center. 
Run `python3 generator.py N L rp mp RP MP vm`, where:
   - `N`: number of small particles, 100 < N < 150
   - `L`: simulation area side, L > 0
   - `rp`: small particle radius, rp >= 0
   - `mp`: small particle mass, mp > 0
   - `RP`: big particle radius, RP > rp
   - `MP`: big particle mass, MP > mp
   - `vm`: max particle speed module, vm > 0

## Simulation
To generate executable and run the life simulation
1. Run `./prepare.sh` in root.
2. Run `./target/tp3-simu-1.0/brownian-motion.sh -Dstatic=static.txt -Ddynamic=dynamic.txt -DmaxEvents=10000`, where:
   - `static`: static file filepath
   - `dynamic`: dynamic file filepath
   - `maxEvents`: maximum amount of events to analyze, maxEvents > 0

   The example above equals to run `./target/tp3-simu-1.0/brownian-motion.sh`, as those are the default values

## Animation Tool
Generates `simu.xyz` using information from `static.txt` and `dynamic.txt`.
Run `python3 animator.py dt vm`, where:
   - `dt`: minimum timestep between events, dt >= 0
   - `vm`: max particle speed module (coloured red), vm > 0

To view the animation, you must open `simu.xyz` with Ovito:
`./bin/ovito simu.xyz`. Particles will be colored in a scale of colors from cian (static particles) to red (high velocity module), showing how fast each particle is going.

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
Generate plots and observables given a single simulation file as input. If simulation file is named `data`, then:
`python3 analysis.py [plot] < data`

If plot is not provided, then no graphs are plotted.

All plots have time as independant variable. Plots shown are:
- Live cells count
- Pattern outer radius
- Pattern inner radius
- Number of changes between t and t-1

### rule-analysis.sh
This script can be used to run any of the rules specified before given a rule number (1-6) and a fill value.
`./rule-analysis.sh rule_number fill`

The script runs the simulation and then runs `analysis.py` with the output data file.

## multipleAnalysis.py
Run analysis on multiple simulation files to plot observables according to the different fill percentages. It receives a root directory, where each folder should correspond to a fill percentage (eg: `10`) with multiple data simulations of that percentage.
`python3 multipleAnalysis.py root_directory [save_dir]`

If save_dir is provided, the plots as `.png` in that directory.

All plots have fill percentage as independant variable. Plots shown are:
- Step count
- Rate of change of live cells count
- Rate of change of pattern outer radius
- Rate of change of pattern inner radius
- Rate of change of the number of changes between t and t-1

### rule-multianalysis.sh
This script can be used to run any of the rules specified before multiple times, given a rule number (1-6), a starting fill value, a step to increase fill value each iteration and the number of repetitions to run for each fill percentage in range.
`./rule-multianalysis.sh rule_num fill_start fill_step repetitions`

The script runs the simulation for each available fill percentage from `fill_start` to the highest `fill_start + K * fill_step` that is lower or equal than 100. Then, it runs `multipleAnalysis.py` with the output data directory. The plots can be found at directory `pics_ruleN`, where N is the rule number provided. Values corresponding to each plot can also be found at file `pics_ruleN/outN.txt`, being N the rule number both times.
