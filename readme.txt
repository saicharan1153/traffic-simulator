Python 3.7.3

libraries
pygame 2.1.2

read_gen_data() -> function used to generate vehicles according to mentioned csv file for fixed signaling, In case of optimized signaling it uses predited data csv file to calculate green time and scheduling.


when running the simulator make sure the generated traffic data and predicted file path to be changed in read_gen_data() accordingly.

when running fixed signaling make sure fixed_signaling function is called in thread2. Similarly, for optimized signaling call optimizationAlgoSignalling function in thread2

for exporting the avg delay data to csv make sure to chane file_name variable accordingly

for running the simulator in multiple speeds change sim_rate variable, but make sure that if higher sim_rate is chosen the functionality of simulator will not be proper functions may not be called properly for chosen speed

