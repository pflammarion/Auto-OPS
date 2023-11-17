################################################################################
#
# Innovus setup file
# Created by Genus(TM) Synthesis Solution 19.14-s108_1
#   on 11/16/2023 18:10:25
#
################################################################################
#
# Genus(TM) Synthesis Solution setup file
#
################################################################################

      regexp {\d\d} [get_db program_version] major_version
      if { $major_version < 18 } {
        error "Innovus version must be 18 or higher."
      }
    

      set _t0 [clock seconds]
      Puts [format  {%%%s Begin Genus to Innovus Setup (%s)} \# [clock format $_t0 -format {%m/%d %H:%M:%S}]]
    
set allowMultiplePortPinWithoutMustjoin 1


# Design Import
################################################################################
setLibraryUnit -cap 1ff -time 1ns
## Reading FlowKit settings file
source encounter/top.v.flowkit_settings.tcl

source encounter/top.v.globals
init_design

# Reading metrics file
################################################################################
um::read_metric -id current encounter/top.v.metrics.json 



# Mode Setup
################################################################################
source encounter/top.v.mode


# MSV Setup
################################################################################

# Reading write_name_mapping file
################################################################################

      if { [is_attribute -obj_type port original_name] &&
           [is_attribute -obj_type pin original_name] &&
           [is_attribute -obj_type pin is_phase_inverted]} {
        source encounter/top.v.wnm_attrs.tcl
      }
    
eval {set edi_pe::pegConsiderMacroLayersUnblocked 1}
eval {set edi_pe::pegPreRouteWireWidthBasedDensityCalModel 1}

      set _t1 [clock seconds]
      Puts [format  {%%%s End Genus to Innovus Setup (%s, real=%s)} \# [clock format $_t1 -format {%m/%d %H:%M:%S}] [clock format [expr {28800 + $_t1 - $_t0}] -format {%H:%M:%S}]]
    


# The following is partial list of suggested prototyping commands.
# These commands are provided for reference only.
# Please consult the Innovus documentation for more information.
#   Placement...
#     ecoPlace                     ;# legalizes placement including placing any cells that may not be placed
#     - or -
#     placeDesign -incremental     ;# adjusts existing placement
#     - or -
#     placeDesign                  ;# performs detailed placement discarding any existing placement
#   Optimization & Timing...
#     optDesign -preCTS            ;# performs trial route and optimization
#     timeDesign -preCTS           ;# performs timing analysis

