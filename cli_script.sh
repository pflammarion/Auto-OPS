# Example of script where echo are interpreted

echo "update cell_name INV_X1"

for x in {0..1}; do
  echo "update state_list $x"
  for i in {0..30}; do
    position_x=$((100*i))
    echo "update x_position $position_x"
    for j in {0..30}; do
      position_y=$((100*j))
      echo "update y_position $position_y"
      echo "rcv save"
    done
  done
done

