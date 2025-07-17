# Project Overview

The Path Explorer is a modern PyQt6-based application designed for visualizing additive manufacturing toolpaths from CLI files. It offers thermal simulation and 3D preview inspection capabilities, enabling detailed analysis of manufacturing processes.

## Installation

To simplify the Python environment setup, I opted for [UV](https://docs.astral.sh/uv/), a virtual environment manager and extremely fast package manager written in Rust. It consolidates multiple setup steps into one, making it easier to set up the environment. Alternatively, I’ve provided the requirements.txt file for those who prefer using their preferred package manager and setting up a virtual environment as they are accustomed to.

I’ve primarily tested the application on three operating systems:

## macOS 15.5 (ARM V9.2A: Apple Silicone)

Installing a package manager to install many Linux-style programs is highly beneficial on macOS. Therefore, I recommend installing [Homebrew](https://brew.sh). After installing Homebrew, follow the next set of commands from the terminal shell, which defaults to [zsh](https://en.wikipedia.org/wiki/Z_shell).

```zsh
brew install uv
```

MacOS typically comes with Git installed by default. However, if you need to install Git from Homebrew, append “git” to the above command: brew install uv git.

Although macOS ships with an older Python version by default, I used Python 3.13.5 in this project, which I installed from Homebrew. Interestingly, I also tested the project with the shipped Python 2.10 on macOS, and it ran smoothly with the older version.

```zsh
git clone https://gitlab.com/chetanpm/path-explorer && cd path-explorer
```

```zsh
uv sync
```

The repository contains a lockfile named uv.lock that lists the required package dependencies and their versions I tested in the project. UV installs all the dependencies swiftly.

```zsh
uv run .
```

This will launch the GUI. Since UV automatically manages the virtual environment, it creates one, activates it, and runs the scripts. Once the code is terminated, the virtual environment is automatically deactivated.

If you don’t like to use UV, you can create a virtual environment using Python’s venv or conda. Activate the environment by sourcing the activate binary inside yourVirtualEnvironment/bin/activate, then run pip install -r requirements.txt to install all the dependencies, and finally, run python __main__.py to launch the GUI.

## Windows 11 (Intel)

In the latest versions of Windows, there’s an inbuilt package manager that you can use to download packages like UV and Git.

You can either follow the installation instructions from UV’s website or use the following command:

```bash
winget install —id=astral-sh.uv -e
```
Also you need to install git

```bash
winget install git.git
```

Once these are installed clonning the path-explorer repository, running the uv commands are exactly the same since it manages the platform specific virtual environment setting scripts automatically.

## Arch Linux (Intel)

```bash
sudo pacman -S uv
```
