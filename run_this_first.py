import os

filevar = r"C:\NemoTMS\NeMo-TMS-master\Models\cell_2"
path = os.path.join(filevar, r'output_folder')
os.mkdir(path)


with open(filevar + r'\Code\NEURON\GUI_params.hoc','r') as file:
        filedata = file.readlines()
filedata[10] = 'E_field_params()'
with open(filevar + r'\Code\NEURON\GUI_params.hoc','w') as file:
        file.writelines(filedata)    
        
        
with open(filevar + r'\Code\NEURON\GUI.hoc','r') as file:
        filedata1 = file.readlines()
filedata1[30] = 'save_params() \n'
filedata1.insert(30, 'syn_freq = 3 \n')
filedata1.insert(31, 'syn_noise = 0.5 \n')
filedata1.insert(32, 'syn_weight = 0.00 \n')
filedata1.insert(33, 'syn_weight_sync = 0.00 \n')
filedata1.insert(34, 'tms_offset = 2.00 \n')
with open(filevar + r'\Code\NEURON\GUI.hoc','w') as file:
       file.writelines(filedata1)    
        
with open(filevar + r'\Results\E-Field_Coupling\parameters.txt','r') as file:
        filedata2 = file.readlines()  
with open(filevar + r'\Code\E-Field_Coupling\parameters.txt','w') as file:
       file.writelines(filedata2)

with open('checkfired.py','r') as file:
        filedata3 = file.readlines()
filedata3[17] = 'filevar = r"' + filevar + '"'
with open(filevar + r'\output_folder\checkfired.py','w') as file:
        file.writelines(filedata3)

with open('automate_NeMo.bat','r') as file:
        filedata4 = file.readlines()
filedata4[8] = 'cd ' + filevar + r'\Code\E-Field_Coupling'
with open(filevar + r'\output_folder\automate_NeMo.bat','w') as file:
        file.writelines(filedata4)

os.remove(filevar + r'\Code\TMS_Waveform\TMS_Waveform.m')#this line removes the original waveform

with open('TMS_Waveform.m', 'r') as file:#will be replaced here by the rudniki waveform
    filedata5 = file.readlines()
with open(filevar + r'\Code\TMS_Waveform\TMS_Waveform.m','w') as file
    file.writelines(filedata5)
    
#Current as of 1315, 15 June
#last modified by Ben Joray