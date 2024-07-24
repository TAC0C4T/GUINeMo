# BeNeMo
Ben's addition to NeMoTMS software for automation


TUTORIAL
___________________________________________________________________
## The short version

to begin you must allow powershell script execution. i could not get one of the scripts working as a batch script so i had to use powershell. open powershell as admin and run this command: ```Set-ExecutionPolicy -ExecutionPolicy Unrestricted```

files you need to know the location of: \
cell folder- in your nemotms models folder \
simnibs matlab- Users\(username)\SimNIBS-4.1\matlab_tools     this is the shortcut, double click on it to go to the folder \
m2m_ernie- simnibs4_examples\m2m_ernie    on my machine located in NeMo_research on the c drive \

first follow the nemo full tutorial pdf through set 3.2 \
Unzip the file you get when you download this repository \
run the run_this_first.py file. \  
The first folder select is for your cell folder, the second is for your simNIBS MATLAB folder, the third is the m2m_ernie folder. \
run the tms waveform generation step (3.6 in the full tutorial pdf) as per the full tutorial for nemo in Code\Neuron \
navigate to the cell folder and there will be a new folder created called output_folder. \
run runAuto.bat \
\
EACH RUN WILL OVERWRITE THE OUTPUT FILE SO EITHER CHANGE THE NAME OR MOVE IT AFTER EACH RUN.
At the default of 0degrees - 360degrees at 15degree steps the program takes somewhere in between 6 and 12 hours (not sure of the exact time) to run. \
\
to change orientation and parameters for coupling, along with parameters in the efield calculations you must make those changes in hocscript.ps1. \
to change basic simulation parameters you go in to automate_SimNIBS.py and change variables \
 \
to skip running benemo just comment out line 97 of automate_simnibs.py



### Important Notes

THE LOW VALUE IN checkfired.py MUST BE BELOW THE FIRING THRESHOLD AND THE HIGH VALUE MUST BE ABOVE THE FIRING THRESHOLD. Error checking is a future task for this project and is currently not implemented. If, for instance, you set low to 500, but the threshold is actually 450, the file will run indefinitely until force quit.

The parameters.txt file that the script copies to your Code/E-Field_Coupling folder is based off your previous simNIBS simulation output. If you rerun the simNIBS simulation using a different coil, location, or change parameters, you will need to navigate to Results/E-Field_Coupling and copy the parameters.txt located there and move it to Code/E-Field_Coupling.

If you are planning to use a TMS waveform that is longer than 500us, you will need to modify the timeout amount that is hardcoded into automate_NeMo.bat, on line 24. The default value is 100 which works for waveforms of 500us or less.
