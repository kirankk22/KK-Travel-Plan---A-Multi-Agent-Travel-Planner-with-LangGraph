# KK-Travel-Plan---A-Multi-Agent-Travel-Planner-with-LangGraph

## How to run ?

1. Create the virtual environment using conda:

```bash
conda create -n kk-travel-plan python=3.13 -y
```

2. Activate the virtual environment:

```bash
conda activate kk-travel-plan
```

3. Install the required dependencies:

```bash
conda activate kk-travel-plan
python -m pip install --upgrade pip
python -m pip install --dry-run -r requirements.txt
```


```bash
python -m pip install -r requirements.txt
python -m pip check
```

## Environment Setup — macOS (Apple Silicon)

### Issue: `zsh: command not found: conda`

This error indicates that Conda is either not installed or its executable is not available in the terminal's `PATH`.

The following steps describe how to install Miniforge and configure the Python environment on macOS.

### Step 1: Verify the Existing Setup

Run the following commands in the terminal:

```bash
python3 --version
which python3
which brew
which conda
uname -m
```

**Expected environment:**
- Operating system: macOS
- Architecture: `arm64` (Apple Silicon)
- Python: 3.13.7
- Package manager: Homebrew
- Conda: Installed in the following steps if not already available

### Step 2: Download Miniforge

Miniforge is a lightweight Conda distribution that provides Python environment and package management.

Official download page: https://conda-forge.org/download/

Select the appropriate installer for your Mac.

For Apple Silicon Macs, the installer filename is:

```text
Miniforge3-Darwin-arm64.sh
```

### Step 3: Install Miniforge

If the installer has already been downloaded, execute:

```bash
bash ~/Downloads/Miniforge3-Darwin-arm64.sh
```

Follow the installation prompts:

1. Press `Enter` to review the license.
2. Press `q` to exit the license screen if prompted.
3. Type `yes` to accept the license agreement.
4. Press `Enter` to accept the default installation directory:

   ```text
   /Users/kirankumar/miniforge3
   ```

5. When prompted to initialize Miniforge, type `yes`.

Wait for the installation to complete.

> **Note:** The installation directory shown above is the default. If you selected a different directory, use that location in the subsequent commands.

### Step 4: Initialize Conda in Zsh

Initialize Conda for the Zsh shell:

```bash
~/miniforge3/bin/conda init zsh
```

Reload the shell configuration:

```bash
source ~/.zshrc
```

Alternatively, close and reopen the terminal.

Verify the installation:

```bash
conda --version
```

The command should display the installed Conda version.

### Step 5: Create the Project Environment

Create a dedicated Conda environment for the travel planner:

```bash
conda create -n kk-travel-plan python=3.13 -y
```

Activate the environment:

```bash
conda activate kk-travel-plan
```

Verify the Python version and executable path:

```bash
python --version
which python
```

The Python executable should point to the `kk-travel-plan` environment.

### Step 6: Verify the Active Environment

List all Conda environments:

```bash
conda env list
```

Example output:

```text
# conda environments:
#
base                     /Users/kirankumar/miniforge3
kk-travel-plan         *  /Users/kirankumar/miniforge3/envs/kk-travel-plan
```

The asterisk (`*`) indicates the currently active environment.

Your terminal prompt should also show the environment name:

```text
(kk-travel-plan) kirankumar@Kirans-MacBook-Air KK-Travel-Plan---A-Multi-Agent-Travel-Planner-with-LangGraph %
```

### Troubleshooting

**Problem:** `conda: command not found`

Try initializing Conda again:

```bash
~/miniforge3/bin/conda init zsh
source ~/.zshrc
conda --version
```

If the installation directory differs from the default, replace `~/miniforge3` with your actual installation path.

**Problem:** The environment is not activated.

Run:

```bash
conda activate kk-travel-plan
```

**Problem:** The Python executable points outside the environment.

Check the active environment:

```bash
conda info --envs
which python
```

If necessary, activate `kk-travel-plan` again before installing project dependencies.

### Environment Setup Complete

The project now has a dedicated Python 3.13 Conda environment.

**Next steps:**
1. Install the dependencies listed in `requirements.txt`.
2. Configure the required environment variables in `.env`.
3. Run the application and validate the LangGraph multi-agent workflow.

Keep project dependencies isolated within `kk-travel-plan` to avoid conflicts with system-wide Python packages.


