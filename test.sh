#!/bin/zsh
source venv/bin/activate

python3 ./main.py\
                --std_file input/stdcells.gds \
                --lib_file input/stdcells.lib \
                --layer_list "[[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]]" \
                --output unit_test