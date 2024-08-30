# NMR core repo installation
 
 This guide will help you set up the necessary Python environment to run the NMR project. The environment includes various scientific libraries essential for working with NMR data.

Installation steps:

1. [Clone NMR_core repository](#clone-nmr_core-repository)
2. [Install dependencies](#install-dependencies)

## Clone NMR_core repository

1. Open your terminal and navigate to the directory where you would like to download the NMR_core repository from Github.

        cd <path-to-t1_GitHub-repositories>

    * **Tip for new Windows WSL users:** You can navigate to your Windows file system in the WSL command line by using the following command:

          cd /mnt/c/Users/<your-user-name>


2. Clone the nmr_core GitHub repositories.

        git clone https://github.com/VonBoss/NMR_core.git

## Install dependencies

Options:

1. [Install using a conda environment (**recommended**)](#install-using-a-conda-environment-recommended)
2. [Install dependencies with pip](#install-using-pip)

### Install using a conda environment (**recommended**)

1. Create `nmr` conda environment.

        cd NMR_core
        conda env create --file enviroment.yml

2. Activate the `nmr` environment to use it.

        conda activate nmr

3. Run the Jupyter notebooks
    
    You can now run your Jupyter notebooks within this environment. Start with:

        jupyter notebook  

### Install using pip

1. Prerequisites

    Before starting, make sure you have the following installed on your system:

    - **Python 3.8+**
    - **pip**
    - **virtualenv** (optional but recommended)

2. Create a Virtual Environment (recommended).

        python -m venv nmr

3. Activate the virtual environment.

    On windows: 

        nmr\Scripts\activate

    On macOS/Linux:
    
        source nmr/bin/activate

4. Install dependencies

        pip install numpy scipy ipykernel matplotlib nmrpy rdkit-pypi xlsxwriter pandas==2.1 pyarrow ipykernel
        python -m ipykernel install --user --name=nmr --display-name "Python (nmr)"

5. Run the Jupyter notebooks
    
    You can now run your Jupyter notebooks within this environment. Start with:

        jupyter notebook  


