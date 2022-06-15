# BeNeMo
Ben's addition to NeMoTMS software for automation


TUTORIAL
___________________________________________________________________
There are 3 critical files in this repository: checkfired.py, run_this_first.py, and automate_NeMo.bat

The intention is to use the run_this_first.py file to create the necesary changes to the NeMo file structure to allow it to be automated. This includes adding some preset values in files and changing what they call.

The first step is to edit the filevar string in the run_this_first.py and point it to your desired cell model, and you will have to edit one line in the automate_NeMo.bat file. At the moment I have not figured out how to insert a properly formatted string into a batch file.

Once you have done run_this_first.py, you will simply run checkfired.py everytime you want to get the firing threshold of the cell. You can edit the variables in the beginning of checkfired to modify the tolerance and range of scaling factor.



THIS README IS STILL A WORK IN PROGRESS.
