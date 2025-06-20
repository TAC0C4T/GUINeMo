param (
    [string]$meshpath,
    [double[]]$nrnloc,
    [double[]]$nrnaxs,
    [double[]]$nrnori
)

# Define content for parameters.txt
$content = @"
% FEM mesh file name
meshfile = 'ernie_TMS_1-0001_Magstim_70mm_Fig8_scalar.msh';
% FEM mesh pathway
meshpath = '..\..\output_folder\$meshpath';
% neuron location
nrnloc = [$(($nrnloc -join ' '))];                                          %CHANGE NEURON LOCATION HERE
% neuron depth
nrndpth = 1;
% neuron segment coordinates file name
nrnfile = 'locs_all_seg.txt';
% neuron segment coordinates pathway
nrnpath = '..\..\Results\NEURON\locs\';
% neuron axis
nrnaxs = [$(($nrnaxs -join ' '))];
% neuron desired orientation
nrnori = [$(($nrnori -join ' '))];                                              %Change neuron orientation here
% E-field scaling factor
scale_E = 1;
% results directory
respath = '..\..\Results\E-field_Coupling';
"@

# efield calculation MATLAB script content with modified head_mesh path
$matlabcontent = @"
% Simple ROI analysis of the electric field from a simulation.
% We will calculate the mean electric field in a gray matter ROI
% The ROI is defined using an MNI coordinates

%% Load Simulation Result

% Read the simulation result
head_mesh = mesh_load_gmsh4(fullfile('$meshpath', 'ernie_TMS_1-0001_Magstim_70mm_Fig8_scalar.msh'));

% Crop the mesh so we only have gray matter volume elements (tag 2 in the mesh)
gray_matter = mesh_extract_regions(head_mesh, 'region_idx', 2);

%% Get Elements
% Electric fields are defined in the center of the elements
% get element centers
elm_centers = mesh_get_tetrahedron_centers(gray_matter);
% get element volumes, we will use those for averaging
elm_vols = mesh_get_tetrahedron_sizes(gray_matter);

%% Define the ROI

% Define M1 from MNI coordinates (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2034289/)
% the first argument is the MNI coordinates
% the second argument is the subject "m2m" folder
ernie_coords = mni2subject_coords([-46, 45, 38], 'm2m_ernie');
% we will use a sphere of radius 10 mm
r = 10;
% determine the elements in the ROI
roi = sqrt(sum(bsxfun(@minus, elm_centers, ernie_coords).^2, 2)) < r;

%% Get field and calculate the mean
% Get the field of interest
field_name = 'magnE';
field_idx = get_field_idx(gray_matter, field_name, 'elements');
field = gray_matter.element_data{field_idx}.tetdata;

% Calculate the mean
avg_field_roi = sum(field(roi) .* elm_vols(roi))/sum(elm_vols(roi));
fprintf('mean %s in ROI: %f\n', field_name, avg_field_roi)

%% Calculate field at coordinates
field_value = get_fields_at_coordinates(head_mesh, ernie_coords, 'nan');

file = fopen('output.txt', 'wt');
fprintf(file, '%f\n', avg_field_roi);
fprintf(file, '%f\n', field_value{1, 1}.data);
fprintf(file, '%f\n', field_value{1, 2}.data);
"@

Write-Host "writing content to Efield_SimNIBS.m"
Set-Content -Path "Efield_SimNIBS.m" -value $matlabcontent

# Write content to parameters.txt
Write-Host "Writing content to parameters.txt"
Set-Content -Path "..\Code\E-Field_Coupling\parameters.txt" -Value $content

# Write MATLAB script content to a temporary file
# $matlabscript = Join-Path $env:TEMP "matlab_script.m"
# Set-Content -Path $matlabscript -Value $matlabcontent

# Change directory to NEURON folder
Write-Host "Changing directory to NEURON folder"
Set-Location -Path "..\Code\NEURON"

# Run nrniv with save_locations.hoc
Write-Host "Running nrniv with save_locations.hoc"
Start-Process -FilePath "nrniv" -ArgumentList "save_locations.hoc" -NoNewWindow -Wait

# Change directory to E-Field_Coupling folder
# Write-Host "Changing directory to E-Field_Coupling folder"
# Set-Location -Path "..\E-Field_Coupling\"

# Change directory to output_folder
Set-Location -Path "..\..\output_folder\"

# Run MATLAB with batch script
Write-Host "Running MATLAB with batch script"
Start-Process -FilePath "matlab" -ArgumentList "-batch", "Efield_SimNIBS()" -NoNewWindow -Wait

# Change directory to output_folder
# Write-Host "Changing directory to output_folder"
# Set-Location -Path "..\..\output_folder"

# Run MATLAB with Efield_SimNIBS function
# Write-Host "Running MATLAB with Efield_SimNIBS function"
# Start-Process -FilePath "matlab" -ArgumentList "-batch", "Efield_SimNIBS()" -NoNewWindow -Wait

# Clean up temporary MATLAB script
# Remove-Item $matlabscript

Exit
