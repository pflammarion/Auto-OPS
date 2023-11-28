#!/bin/zsh

source venv/bin/activate

benchmarks=1

if [[ benchmarks -eq 1 ]]; then
    benchmark_list=('c17' 'c432' 'c499' 'c1355' 'c1908' 'c2670' 'c3540' 'c7552')
    def_path_prefix="benchmarks/Benchmarks_ISCAS85/GDS-II/Benchmarks"
elif [[ benchmarks -eq 2 ]]; then
    benchmark_list=('test01' 'test02' 'test03' 'test04' 'test05' 'test06' 'test07' 'test08' 'test09' 'test10' 'test11' 'test12' 'test13' 'test14' 'test15' 'test16' 'test17' 'test18' 'test19' 'test20')
    def_path_prefix="benchmarks/ICCAD_Contest2021"
elif [[ benchmarks -eq 3 ]]; then
    benchmark_list=('adder' 'bar' 'div' 'Hyp' 'log2' 'max' 'multiplier' 'sin' 'sqrt' 'square')
    def_path_prefix="benchmarks/EPFL"
else
    echo "Invalid value for 'benchmarks'. Exiting."
    exit 1
fi

for def_name in "${benchmark_list[@]}"
do
    if [[ benchmarks -eq 1 ]]; then
        def_path="${def_path_prefix}/${def_name}/${def_name}.def"
    else
        def_path="${def_path_prefix}/${def_name}/Par/top.def"
    fi

    python3 ./main.py \
        --std_file input/stdcells.gds \
        --lib_file input/stdcells.lib \
        --def_file "$def_path" \
        --layer_list 1 5 9 10 11
done

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