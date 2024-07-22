param (
    [string]$meshpath
)

# Define content for parameters.txt
$content = @"
% FEM mesh file name
meshfile = 'ernie_TMS_1-0001_Magstim_70mm_Fig8_scalar.msh';
% FEM mesh pathway
meshpath = '$meshpath';
% neuron location
nrnloc = [-46  45  38];
% neuron depth
nrndpth = 1;
% neuron segment coordinates file name
nrnfile = 'locs_all_seg.txt';
% neuron segment coordinates pathway
nrnpath = '..\..\Results\NEURON\locs\';
% neuron axis
nrnaxs = [0  1  0];
% neuron desired oriention
nrnori = [1  0  0];
% E-field scaling factor
scale_E = 1;
% results directory
respath = '..\..\Results\E-field_Coupling';
"@

# Write content to parameters.txt
Set-Content -Path "..\Code\E-Field_Coupling\parameters.txt" -Value $content

# Change drive to C:
#Set-Location -Path "C:\"

# Change directory to NEURON folder
Set-Location -Path "..\Code\NEURON"

# Run nrniv with save_locations.hoc
Start-Process -FilePath "nrniv" -ArgumentList "save_locations.hoc" -NoNewWindow -Wait

# Change directory to E-Field_Coupling folder
Set-Location -Path "..\E-Field_Coupling\"

# Run MATLAB with batch script
Start-Process -FilePath "matlab" -ArgumentList "-batch", "couple_script('parameters.txt')" -NoNewWindow -Wait

# Change directory to output_folder
Set-Location -Path "..\..\output_folder"

# Run MATLAB with Efield_SimNIBS function
Start-Process -FilePath "matlab" -ArgumentList "-batch", "Efield_SimNIBS()" -NoNewWindow -Wait

Exit