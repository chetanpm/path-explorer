Project Overview

The Path Explorer is a modern PyQt6-based application designed for visualizing additive manufacturing toolpaths from CLI files. It features thermal simulation, 3D preview inspection capabilities for detailed analysis of manufacturing processes.

## Installation

To streamline the python environment setup, I've decided to go with [UV](https://docs.astral.sh/uv/). Its a virtual environment manager cum extremely fast package manager written in rust that streamlines multiple steps into one. You may use it for ease of setup or I've also the requirements.txt made available for someone who likes to do it with their choice of package manager and setup a virtual environment like they are used to.

I have primarily tested on three operating systems:

## Macos 15.5(Apple Silicone)

Macos needs a package manager to install many linux style programs. So install [Homebrew](https://brew.sh) and after installing homebrew, follow the next set of commands from the terminal shell which defaults to [zsh](https://en.wikipedia.org/wiki/Z_shell).

```bash
brew install uv
```

macos has git installed by default. You may also install git from brew by appending git after a space right behind uv in the above command.

```zsh
git clone https://gitlab.com/chetanpm/path-explorer
```

```zsh
cd path-explorer
```

```zsh
uv sync
```

There's a lockfile with the name uv.lock that has all the required package dependencies and their versions that I've tested in the project. UV installs all the dependencies lightning quick.

```zsh
uv run .
```

This will launch the gui. Since UV automatically manages the virtual environment, it automatically creates one, activates it and run the scripts. Once the code is terminated, the virtual environment is automatically deactivated.

You may create a virtual environment using python venv or conda if you don't like to use UV, activate the environment by sourcing the activate binary inside yourVirtualEnvironment/bin/activate and then run pip install -r requirements.txt to install all the dependencies and then run python __main__.py to launch the gui.

## Windows 11(Intel)

In latest iterations of windows, there is an inbuilt package manager that you can use to download the packages like uv and git

Either follow the installation instructions from UV's website or

```bash
winget install --id=astral-sh.uv  -e
```


## Arch Linux(Intel)

```bash
sudo pacman -S uv
```
