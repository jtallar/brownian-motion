# Life Simulation
To generate executable and run the life simulation
1. Run `./prepare.sh` in root.
2. Run `./target/tp2-simu-1.0/life.sh -Dsize=100 -Dinit=40 -Dfill=60 -Dseed=System.nanoTime() -Dsteps=Long.MAX_VALUE -Dout=data -Dpel=false -Drule="=.2.|.=.3/=.3" -Ddim=2 -Dmoore=1 -Dcenter=false`, where:
    - `size` square matrix side size
    - `init`: initial square matrix side size 
    - `fill`: initial square matrix occupation percentage
    - `steps`: maximum amount of steps performed
    - `out`: output file filepath
    - `pel`: sets parallel processing
    - `rule`: Survival/Birth rule
    - `dim`: matrix amount of dimensions
    - `moore`: moore neighbour cells depth
    - `center`: true for centered to origin (0, 0, 0) output and input
    - the example above equals to run `./life.sh`
3. [OPTIONAL] Run  `./target/tp2-simu-1.0/life.sh -Din=dataIn`, where
    - `in`: initializer file and also output file (must finish in new line)
    - `steps`, `moore`, `pal` and `rule` can be added
    - this method replaces `size`, `init`, `fill`, `seed`, `dim` and `out`

## 2D Systems Used
All 2D systems used will have a 101x101 grid, with particles starting at a 41x41 smaller grid. 
Seed value will be randomized, steps will not be limited and output will be generated at corresponding directory.
Center option will be set to true, as well as parallel processing, and dimensions will be set to 2.
Fill will take different values in the interval (0,100].

### Rule 1 - 2D System 1
Standard Conway's Game of Life ruleset. 
- Moore neighbourhood of range 1.
- A cell survives if it has either 2 or 3 living neighbours. 
- A cell is born if it has exactly 3 living neighbours.

`./target/tp2-simu-1.0/life.sh -Drule="=.2.|.=.3/=.3" -Dsize=101 -Dinit=41 -Ddim=2 -Dpel=true -Dcenter=true -Dfill=60`

### Rule 2 - 2D System 2
Custom ruleset with different Moore neighbourhood range.
- Moore neighbourhood of range 2.
- A cell survives if it has either 9 or 10 living neighbours. 
- A cell is born if it has between 1 and 4 living neighbours.

`./target/tp2-simu-1.0/life.sh -Drule=">.8.&.<.11/>.0.&.<.5" -Dmoore=2 -Dsize=101 -Dinit=41 -Ddim=2 -Dpel=true -Dcenter=true -Dfill=60`

### Rule 3 - 2D System 3
Custom ruleset with possibility of surviving without neighbours.
- Moore neighbourhood of range 1.
- A cell survives if it has at most 2 living neighbours. 
- A cell is born if it has exactly 3 living neighbours.

`./target/tp2-simu-1.0/life.sh -Drule="<.3/=.3" -Dsize=101 -Dinit=41 -Ddim=2 -Dpel=true -Dcenter=true -Dfill=60`

## 3D Systems Used
All 3D systems used will have a 101x101x101 grid, with particles starting at a 41x41x41 smaller grid. 
Seed value will be randomized, steps will not be limited and output will be generated at corresponding directory.
Center option will be set to true, as well as parallel processing, and dimensions will be set to 2.
Fill will take different values in the interval (0,100].

### Rule 4 - 3D System 1
Standard Conway's Game of Life ruleset applied to 3D. 
- Moore neighbourhood of range 1.
- A cell survives if it has either 2 or 3 living neighbours. 
- A cell is born if it has exactly 3 living neighbours.

`./target/tp2-simu-1.0/life.sh -Drule="=.2.|.=.3/=.3" -Dsize=101 -Dinit=41 -Ddim=3 -Dpel=true -Dcenter=true -Dfill=60`

### Rule 5 - 3D System 2
Known 3D ruleset named 5766.
- Moore neighbourhood of range 1.
- A cell survives if it has between 5 and 7 living neighbours. 
- A cell is born if it has exactly 6 living neighbours.

`./target/tp2-simu-1.0/life.sh -Drule=">.4.&.<.8/=.6" -Dsize=101 -Dinit=41 -Ddim=3 -Dpel=true -Dcenter=true -Dfill=60`

### Rule 6 - 3D System 3
Custom ruleset with more possibilities of surviving.
- Moore neighbourhood of range 1.
- A cell survives if it has between 6 and 10 living neighbours. 
- A cell is born if it has either 7 or 8 living neighbours.

`./target/tp2-simu-1.0/life.sh -Drule=">.5.&.<.11/=.7.|.=.8" -Dsize=101 -Dinit=41 -Ddim=3 -Dpel=true -Dcenter=true -Dfill=60`

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

# Animation Tool
Generates `simu.xyz` given a simulation file as input. If simulation file is named `data`, then:
`python3 preprocessing.py < data`

To view the animation, you must open `simu.xyz` with Ovito:
`./bin/ovito simu.xyz`

After configuring column mapping, to render particles as cubes, go to Visual elements -> Particles 
and in Particle display, select `Cube/Box` as Standard shape.

## 2D Column Mapping 
If your simulation is a 2D file, configure the file column mapping as follows:
   - Column 1 - Position - X
   - Column 2 - Position - Y
   - Column 3 - Radius
   - Column 4 - Color - R
   - Column 5 - Color - G
   - Column 6 - Color - B

## 3D Column Mapping
If your simulation is a 3D file, configure the file column mapping as follows:
   - Column 1 - Position - X
   - Column 2 - Position - Y
   - Column 3 - Position - Z
   - Column 4 - Radius
   - Column 5 - Color - R
   - Column 6 - Color - G
   - Column 7 - Color - B