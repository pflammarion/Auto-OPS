# ####################################################################

#  Created by Genus(TM) Synthesis Solution 19.14-s108_1 on Thu Nov 16 18:10:24 MET 2023

# ####################################################################

set sdc_version 2.0

set_units -capacitance 1fF
set_units -time 1000ps

# Set the current design
current_design top

set_clock_gating_check -setup 0.0 
set_wire_load_mode "enclosed"
