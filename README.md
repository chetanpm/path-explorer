# Project Overview

The Path Explorer is a modern PyQt6-based application designed for visualizing additive manufacturing toolpaths from CLI files. It offers thermal simulation and 3D preview inspection capabilities, enabling detailed analysis of manufacturing processes.

## Screenshots and Demonstration Video

Here are some screenshots and a demonstration video of the application:

- [Dark Mode](Demonstration/Dark_mode.png)
- [Light Mode](Demonstration/Light_mode.png)
- [File Rendered](Demonstration/Animation.png)
- [Demonstration](Demonstration/Video.mov)

## Installation

To simplify the Python environment setup, I recommend using [UV](https://docs.astral.sh/uv/), a virtual environment manager and extremely fast package manager written in Rust. UV consolidates multiple setup steps into one, making it easier to set up the environment. Alternatively, I’ve provided the requirements.txt file for those who prefer using their preferred package manager and setting up a virtual environment as they are accustomed to.

I’ve primarily tested the application on three operating systems:

## macOS 15.5 (ARM V9.2A: Apple Silicone)

Installing a package manager like [Homebrew](https://brew.sh) is highly beneficial on macOS, as it allows you to install many Linux-style programs. After installing Homebrew, follow the next set of commands from the terminal shell, which defaults to zsh:

```zsh
brew install uv
```

MacOS typically comes with Git shipped by default with all its operating system versions. However, if you need to install Git from Homebrew, append “git” to the above command: brew install uv git.

## Windows 11 (Intel)

In the latest versions of Windows, there’s an inbuilt package manager that allows you to download packages like UV and Git.

You can either follow the installation instructions provided on [UV's](https://docs.astral.sh/uv/) website or use the following command:

```bash
winget install —id=astral-sh.uv -e
```

Additionally, you need to install Git.

```bash
winget install git.git
```

## Arch Linux (Intel)

```bash
sudo pacman -S uv git
```

## Building path-explorer

Once the system’s global dependencies are met, proceed with the path-explorer project. These steps are consistent across all platforms.

```zsh
git clone https://gitlab.com/chetanpm/path-explorer && cd path-explorer
```

```zsh
uv sync
```

The repository contains a lockfile named uv.lock that lists the required package dependencies and their versions. I tested these versions in the project, and UV installs all the dependencies swiftly.

```zsh
uv run .
```

This will launch the GUI. Since UV automatically manages the virtual environment, it creates one, activates it, and runs the scripts. Once the application is terminated, the virtual environment is automatically deactivated.

## Troubleshooting

Running uv run . for the first time may take a few minutes to launch. However, subsequent launches are fast once cached.

If the program doesn’t start or throws errors, try capturing the log using the following command:

```zsh
uv run . 2>&1 | tee parser_debug.log
```

General search results with the log’s errors will help you identify the issue. If you still can’t find a solution, create an issue with the log file, and I’ll search the internet and try to assist you.

If you’re not a fan of using UV, you can create a virtual environment using Python’s venv or conda. Activate the environment by sourcing the activate binary from your VirtualEnvironment/bin/activate directory. Then, run pip install -r requirements.txt to install all the dependencies. Finally, run python __main__.py to launch the GUI.

## Development

The architecture is designed to be modular. The core package comprises three modules: cli_parser, heat_model, and theme_manager. Each module enables specific features within the application. Additional modules can be added to the core to expand its functionality.

The graphical user interface (GUI) package includes main_window, visualization, and styles modules. These modules are decoupled from the core packages.

The cli_parser script executes the parsing logic on the CPU. Rendering is offloaded using pyvista, which utilizes vtk for abstraction and handles GPU acceleration. It leverages corresponding acceleration frameworks such as Metal on Apple silicon, DirectX on Windows, and OpenGL/Vulkan on Linux.

## Key Features

### Parsing Algorithm

1. The script reads the entire file content.
2. It locates the header end marker ($$HEADEREND).
3. The script parses the header parameters:
   - $$UNITS/ (unit conversion factor)
   - $$DIMENSION/ (minimum and maximum coordinates)
   - $$LAYERS/ (total layer count)
4. The script processes the geometry section:
   - For each $$LAYER/ entry:
     a. It calculates the Z-height based on the layer index.
     b. It initializes the layer data structure.
   - For each $$HATCHES/ entry:
     a. It extracts the point count.
     b. It processes the coordinate pairs.
     c. It stores the result as polyline segments.
5. The script validates the consistency of the layer count.
6. The script returns structured data with:
   - Header information.
   - A layer array containing Z-heights and geometries.
   - The actual and declared layer counts.

- The script parses critical header information, including units, dimensions, and layer count.
- It handles both metric and imperial units based on the header specification and converts them to millimeters for visualization.
- The script processes each layer sequentially, preserving the original layer numbering.
- It calculates precise Z-heights based on the header dimensions and layer count.
- Shows a 3d preview by showing all the layers at the same time giving you a rough idea of the final 3d model.
- The script gracefully handles malformed lines and missing sections.

### Heat Source Modeling

The heat source modeling module enables the simulation of heat sources in the application.

Our thermal simulation employs a physics-based heat source model that accurately represents the energy input during additive manufacturing processes. It utilizes the Gaussian heat distribution:

- I’ve incorporated a moving heat source to simulate the line-by-line scanning process for each layer.
- The spot size adapts based on the hatch spacing.

### Visualization

- Real-time rendering with GPU acceleration.

### Limitations

- Currently supports hatches only (no contours).
- Assumes constant layer height.
- Simplified Gaussian model (not the full Rosenthal solution).
- No material-specific calibration.
- No experimental validation.

Thermal accumulation with history and a full simulation of thermal application with a moving heat source automatically layer after layer was working but these features have been commented out of the code due to issues that need to be addressed. Time is required to fix these features.

If you decide to make changes to the code, run ‘uv tool install ruff’ and ‘uv tool run ruff check’ from within the repository. The —fix option can sometimes be used to fix simple syntax errors.
