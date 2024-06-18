import os
from tkinter import Tk
from tkinter.filedialog import askdirectory
import shutil

#below is the popup prompt
filevar = askdirectory(title='Select the Cell Folder') #this variable MUST be the general cell folder, ie \Models\cell_2\
#cannot be anything specific
matlabvar = askdirectory(title='Select the MATLAB Folder(belonging to SimNIBS)')

ernievar = askdirectory(title='Select Ernie Folder')
#filevar = r"C:\NemoTMS\NeMo-TMS-master\Models\cell_2"
path = os.path.join(filevar, r'output_folder')
os.mkdir(path)


with open(filevar + r'\Code\NEURON\GUI_params.hoc','r') as file:
        filedata = file.readlines()
filedata[10] = 'E_field_params()'
with open(filevar + r'\Code\NEURON\GUI_params.hoc','w') as file:
        file.writelines(filedata)


with open(filevar + r'\Code\NEURON\GUI.hoc','r') as file:
        filedata1 = file.readlines()
filedata1[30] = 'save_params() \n'#These are the preset vales in GUI params for a  realistic E-Field
filedata1.insert(30, 'syn_freq = 3 \n')#if this file is run a second time, it will insert these again and it will likely be a problem
filedata1.insert(31, 'syn_noise = 0.5 \n')
filedata1.insert(32, 'syn_weight = 0.00 \n')
filedata1.insert(33, 'syn_weight_sync = 0.00 \n')
filedata1.insert(34, 'tms_offset = 2.00 \n')
with open(filevar + r'\Code\NEURON\GUI.hoc','w') as file:
       file.writelines(filedata1)

with open('parameters.txt','r') as file:
        filedata2 = file.readlines()
with open(filevar + r'\Code\E-Field_Coupling\parameters.txt','w') as file:
       file.writelines(filedata2)

with open('checkfired.py','r') as file:
        filedata3 = file.readlines()
filedata3[17] = '    filevar = r"' + filevar + '"\n'
with open(filevar + r'\output_folder\checkfired.py','w') as file:
        file.writelines(filedata3)




var1 = "matlab -batch \"addpath(\'"
var2= "\'); couple_script(\'"
var3= "\')\""


with open('automate_NeMo.bat','r') as file:
        filedata4 = file.readlines()
filedata4[8] = 'cd ' + filevar + r'\Code\E-Field_Coupling'
filedata4[14] = var1 + matlabvar + var2 + filevar + '/Code/E-Field_Coupling/parameters.txt' + var3#do NOT change the direction of these backslashes, trust me it is not wrong
with open(filevar + r'\output_folder\automate_NeMo.bat','w') as file:
        file.writelines(filedata4)

os.remove(filevar + r'\Code\TMS_Waveform\TMS_Waveform.m')#this line removes the original waveform

with open('TMS_Waveform.m', 'r') as file:#will be replaced here by the rudniki waveform
    filedata5 = file.readlines()
with open(filevar + r'\Code\TMS_Waveform\TMS_Waveform.m','w') as file:
    file.writelines(filedata5)

with open('automate_simNIBS.py','r') as file:
        filedata6 = file.readlines()
with open(filevar + r'\output_folder\automate_simNIBS.py','w') as file:
        file.writelines(filedata6)

with open('rmtree.py','r') as file:
        filedata7 = file.readlines()
with open(filevar + r'\output_folder\rmtree.py','w') as file:
        file.writelines(filedata7)

with open('Efield_SimNIBS.m','r') as file:
        filedata8 = file.readlines()
with open(filevar + r'\output_folder\Efield_SimNIBS.m','w') as file:
        file.writelines(filedata8)

with open('hocScript.bat','r') as file:
        filedata9 = file.readlines()
filedata9[5] = 'cd ' + filevar + r'\Code\Neuron'
filedata9[8] = 'cd ' + filevar + r'\Code\E-Field_Coupling'
filedata9[11] = 'cd ' + filevar + r'\output_folder'
with open(filevar + r'\output_folder\hocScript.bat','w') as file:
        file.writelines(filedata9)

with open('runAuto.bat','r') as file:
        filedata10 = file.readlines()
with open(filevar + r'\output_folder\runAuto.bat','w') as file:
        file.writelines(filedata10)

shutil.copy('Magstim_70mm_Fig8.ccd', filevar + r'\output_folder')

shutil.copytree(ernievar, filevar + r'\output_folder\m2m_ernie')

shutil.copy('parameters.txt', filevar + r'\Code\E-Field_Coupling')


subprocess.check_call(["attrib","+H","automate_NeMo.bat"])#These lines hide the files that are located next to run_this_first
subprocess.check_call(["attrib","+H","TMS_Waveform.m"])#This is so someone doesn't accidentally run checkfired from outside the output_folder
subprocess.check_call(["attrib","+H","checkfired.py"])
