#!/bin/bash
if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters." 
    echo "Run with ./multipleN.sh N_start N_step repetitions"
    exit 1
fi

ROOT_DIR="data_dir"
if [ -d "$ROOT_DIR" ]; then
    printf '%s\n' "Removing Directory recursively ($ROOT_DIR)"
    rm -rf "$ROOT_DIR"
fi
mkdir "$ROOT_DIR"

# Disable plotting if enabled
sed -i -e 's/\"plot\": true/\"plot\": false/g' config.json
N="$1"
while [ "$N" -lt 150 ]
do
    SIM_DIR="$ROOT_DIR/$N"
    if [ -d "$SIM_DIR" ]; then
        printf '%s\n' "Removing Directory recursively ($SIM_DIR)"
        rm -rf "$SIM_DIR"
    fi
    mkdir "$SIM_DIR"
    echo "Running $3 times with N=$N..."
    for i in $(seq 1 $3)
    do
        OUT_FILE="$SIM_DIR/data$i"
        # Replace N with current value
        SED_REP="s/\"N\": [0-9]\+,/\"N\": $N,/g"
        sed -i -e "$SED_REP" config.json
        python3.8 generator.py
        ./target/tp3-simu-1.0/brownian-motion.sh
        python3.8 analysis.py "$OUT_FILE"
    done
    echo "-----------------------------------"
    ((N = N + "$2"))
done