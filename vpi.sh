#!/bin/zsh
source venv/bin/activate

python3 ./main.py\
                --std_file input/stdcells.gds \
                --lib_file input/stdcells.lib \
                --def_file benchmarks/Benchmarks_ISCAS85/GDS-II/Benchmarks/c17/c17.def \
                --layer_list "[[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]]" \
                --vpi input/new_vpi_output \
                --verbose