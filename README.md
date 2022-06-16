# BeNeMo
Ben's addition to NeMoTMS software for automation


TUTORIAL
___________________________________________________________________
There are 3 critical files in this repository: checkfired.py, run_this_first.py, and automate_NeMo.bat

The intention is to use the run_this_first.py file to create the necesary changes to the NeMo file structure to allow it to be automated.
Upon downloading the repository, run the run_this_first.py file, and it will prompt you for two directories. The first folder it asks for is the cell folder within Nemo, and the second folder it will ask for is your simNIBS MATLAB folder.

Once you select both of these, the script will automatically generate the folders and change the files as needed. The file checkfired.py will be wherever you extracted the zip file, and can simply be executed from that location as it will be pointing in the correct direction. The file will also replace the current TMS_Waveform.m file with the new one, with modifications from Ken Rudnicki to have an alterable waveform.

THESE CHANGES TO YOUR FILE STRUCTURE ARE PERMANENT, AND THERE IS NO WAY TO UNDO THEM. Once you execute run_this_first, it will alter preset values in your NEURON files and MATLAB files that will either need to be manually changed back, or you will need to regenerate the cell file from stage one.

Once you have done run_this_first.py, you will simply run checkfired.py everytime you want to get the firing threshold of the cell. You can edit the variables in the beginning of checkfired to modify the tolerance and range of scaling factor.

THE LOW VALUE MUST BE BELOW THE FIRING THRESHOLD AND THE HIGH VALUE MUST BE ABOVE THE FIRING THRESHOLD. Error checking is a future task for this project and is currently not implemented. If, for instance, you set low to 500, but the threshold is actually 450, the file will run indefinitely until force quit.


THIS README IS STILL A WORK IN PROGRESS.
