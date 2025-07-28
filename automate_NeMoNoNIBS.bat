::To begin using file, change all folders and directories to your own
::ex. find your own cell model folder
::In addition since we are running couple_script instead of couple_gui, you will need to find the parameters file
::to do this, navigate to ...\Models\Cell\Results\E-Field_Coupling and copy the parameters.txt file to ...\Models\Cell\Code\E-Field_Coupling
::This parameters.txt file is what you will edit to have your mesh file, coordinates, and scaling factor
::in line 15 of this file where you call couple_script, use the path to the parameters file IN YOUR CODE folder, NOT results folder
@ECHO OFF
ECHO Compiling MATLAB
cd C:\NeMo-TMS-master\Models\71717118\Code\E-Field_Coupling



::only do addpath to matlab folder if upon running couple_gui you get the error cannot find msh_load_gmsh4
::if you do not get that error, remove the addpath command but keep couple script
::matlab -batch "addpath('C:\NemoTMS\NeMo-TMS-master\matlab'); couple_script('C:\NemoTMS\NeMo-TMS-master\Models\cell_6\Code\E-Field_Coupling\parameters.txt')"

cd ..
cd NEURON
::GUI_params.hoc
timeout 30 > nul
::The pause command will prompt "press any key to continue..." DO NOT PRESS A KEY
::PAUSE is intended to make TMS_script run after GUI_params, otherwise they run at the same time
TMS_script.hoc
ECHO script ran
timeout 100 > nul
EXIT /b 0
::the above line of code exits the batch file, while still running the python file, with exit code 0 (no issues)
