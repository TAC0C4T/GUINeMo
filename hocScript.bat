@ECHO OFF

C:

cd C:\NeMo-TMS-master\Models\15step2\Code\NEURON
nrniv save_locations.hoc

cd C:\NeMo-TMS-master\Models\15step2\Code\E-Field_Coupling\
matlab -batch "couple_script('parameters.txt')"

cd C:\NeMo-TMS-master\Models\15step2\output_folder
matlab -batch "Efield_SimNIBS()"

exit