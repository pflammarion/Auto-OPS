if {![namespace exists ::IMEX]} { namespace eval ::IMEX {} }
set ::IMEX::dataVar [file dirname [file normalize [info script]]]
set ::IMEX::libVar ${::IMEX::dataVar}/libs

create_library_set -name default_library_set\
   -timing\
    [list ${::IMEX::libVar}/lib/typ/NangateOpenCellLibrary_typical.lib]
create_rc_corner -name _default_rc_corner_\
   -preRoute_res 1\
   -postRoute_res 1\
   -preRoute_cap 1\
   -postRoute_cap 1\
   -postRoute_xcap 1\
   -preRoute_clkres 0\
   -preRoute_clkcap 0\
   -T 25
create_delay_corner -name _default_delay_corner_\
   -library_set default_library_set\
   -opcond_library NangateOpenCellLibrary\
   -opcond typical\
   -rc_corner _default_rc_corner_
create_constraint_mode -name _default_constraint_mode_\
   -sdc_files\
    [list ${::IMEX::libVar}/mmmc/top.v._default_constraint_mode_.sdc]
create_analysis_view -name _default_view_ -constraint_mode _default_constraint_mode_ -delay_corner _default_delay_corner_
set_analysis_view -setup [list _default_view_] -hold [list _default_view_]
