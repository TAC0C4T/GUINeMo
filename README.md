# BeNeMo
Ben's addition to NeMoTMS software for automation

---

## TUTORIAL

### Necessary

To begin, you must allow PowerShell script execution. One of the scripts could not be implemented as a batch script and had to be written in PowerShell. Open PowerShell as Administrator and run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Unrestricted
```

### Files You Need to Know the Location Of

- **Cell Folder** – located in your NeMoTMS models folder  
- **simNIBS MATLAB Folder** – `Users\(username)\SimNIBS-4.1\matlab_tools` (use the shortcut, double-click to open folder)  
- **m2m_ernie Folder** – `simnibs4_examples\m2m_ernie` (on this machine, it's located in `C:\NeMo_research`)  

### Steps

1. Follow the NeMo full tutorial PDF through section 3.2.
2. Unzip the file you get from this repository.
3. Run `run_this_first.py`.  
   - First folder: your **cell** folder  
   - Second folder: your **simNIBS MATLAB** folder  
   - Third folder: the **m2m_ernie** folder  
4. Run the TMS waveform generation step (section 3.6 in the full tutorial) from `Code/TMS_waveform`.
5. Navigate to the **cell** folder. A new folder called `output_folder` will be created.
6. Run `runAuto.bat`.
7. Input all necessary options
   - Can also copy/paste from excel spreadsheet
8. Click add sim to run for each parameter set
9. Click run button
10. Output will appear in output.csv

**Each run will overwrite the output file.** Rename or move it after each run.

- At the default of 0°–360° in 15° steps, the program takes 6–12 hours to run.

To run again:
- Delete or rename `output.csv`
- Change parameters
- Run `runAuto.bat` again  
(`run_this_first.py` only needs to be run once per cell folder)

---

## Important Notes
- If using a TMS waveform longer than 500us, update the timeout in `automate_NeMo.bat` (line 24). Default is 100, suitable for ≤500us waveforms.
