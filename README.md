Project Overview

The Path Explorer is a modern PyQt6-based application designed for visualizing additive manufacturing toolpaths from CLI files. It features thermal simulation, 3D preview inspection capabilities for detailed analysis of manufacturing processes.

## Installation

To streamline the python environment setup, I've decided to go with [UV](https://docs.astral.sh/uv/). Its a virtual environment manager cum package manager that streamlines multiple steps into one. You may use it for ease of setup or I've also made the requirements.txt made available for someone who likes to do it with their choice of package manager and setup a virtual environment.

I have primarily tested on three operating systems:

## Macos 15.5(Apple Silicone)

```bash
brew install uv
```

## Windows 11(Intel)

```bash
-ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Arch Linux(Intel)

```bash
sudo pacman -S uv
```
