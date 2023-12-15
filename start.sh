#!/bin/sh
source venv/bin/activate

python3 ./main.py\
                --std_file input/stdcells.gds \
                --lib_file input/stdcells.lib \
                --cell_list INV_X1 \
                --layer_list "[[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]]" \
                --input 1 0 \
                --output reflection_over_cell\
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