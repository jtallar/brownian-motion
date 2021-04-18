#!/bin/bash
if [ "$#" -ne 4 ]; then
    echo "Illegal number of parameters." 
    echo "Run with ./multipleT.sh max_v_mod_start max_v_mod_step max_v_mod_stop repetitions"
    exit 1
fi

if [ "$4" -le 1 ]; then
    echo "Illegal number of repetitions. Must be at least 2." 
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
# Set N to NMax = 136
sed -i -e 's/\"N\": [0-9]\+,/\"N\": 136,/g' config.json
MAX_V_MOD="$1"
while (( $(echo "$MAX_V_MOD <= $3" | bc -l) ))
do
    SIM_DIR="$ROOT_DIR/$MAX_V_MOD"
    if [ -d "$SIM_DIR" ]; then
        printf '%s\n' "Removing Directory recursively ($SIM_DIR)"
        rm -rf "$SIM_DIR"
    fi
    mkdir "$SIM_DIR"
    # Replace max_v_mod with current value
    SED_REP="s/\"max_v_mod\": [0-9]\+.[0-9]\+,/\"max_v_mod\": $MAX_V_MOD,/g"
    sed -i -e "$SED_REP" config.json
    # Replace static filename
    SED_DYN="s/\"static_file\": .*,/\"static_file\": \"$ROOT_DIR\/$MAX_V_MOD\/static.txt\",/g"
    sed -i -e "$SED_DYN" config.json
    echo "Running $4 times with max_v_mod=$MAX_V_MOD..."
    for i in $(seq 1 $4)
    do
        # Replace dynamic filename
        SED_DYN="s/\"dynamic_file\": .*,/\"dynamic_file\": \"$ROOT_DIR\/$MAX_V_MOD\/dynamic$i.txt\",/g"
        sed -i -e "$SED_DYN" config.json
        # OUT_FILE="$SIM_DIR/data$i"
        python3.8 generator.py
        ./target/tp3-simu-1.0/brownian-motion.sh
    done
    echo "-----------------------------------"
    MAX_V_MOD=$(echo "$MAX_V_MOD + $2" | bc -l)
done

# Reenable plotting
sed -i -e 's/\"plot\": false/\"plot\": true/g' config.json

PICS_DIR="pics_T"
OUT_FILE="out_T.txt"
python3.8 multipleAnalysis.py "$ROOT_DIR" 'T'
# python3.8 multipleAnalysis.py "$ROOT_DIR" 'T' "$PICS_DIR" > "$OUT_FILE"
# mv "$OUT_FILE" "$PICS_DIR"