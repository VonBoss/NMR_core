# Inversion recovery analysis notebook

## Objective
In this notebook, we will learn the basics of working with scientific data in Python, focusing on an NMR inversion recovery experiment. We will import experimental data into a Pandas DataFrame, calculate the T<sub>1</sub> relaxation times and ideal an ideal d<sub>1</sub> delay time, and visualize the fitted data.
 

## Clone NMR_core repository

1. Open your terminal and navigate to the directory where you would like to download the NMR_core repository from Github.

        cd <path-to-t1_GitHub-repositories>

    * **Tip for new Windows WSL users:** You can navigate to your Windows file system in the WSL command line by using the following command:

          cd /mnt/c/Users/<your-user-name>


2. Clone the RNAvigate and fpocketR GitHub repositories.

        git clone https://github.com/Weeks-UNC/fpocketR.git

5. Create fpocketR conda environment and install fpocketR and RNAvigate.

        cd fpocketR
        conda env create --file enviroment.yml
        conda activate fpocketR
        conda develop .