#!/bin/sh
source venv/bin/activate

python3 ./main.py\
                --std_file input/stdcells.gds \
                --lib_file input/stdcells.lib \
                --layer_list "[[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]]" \
                --def_file benchmarks/EPFL/div/Par/top.def \
                --plot_realtime 50 \
                --benchmark_plot \
                --benchmark_area 100 150 100 150 \
                --verbose
: <<'END_COMMENT'
python3 ./main.py\
                --std_file input/stdcells.gds \
                --lib_file input/stdcells.lib \
                --gds_file \
                --def_file \
                --input \
                --layer_list \
                --cell_list \
                --output \
                --verbose
END_COMMENT