import os
import sys

# Ensure the package runs from its directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

# Import package modules (if needed)
# from .core import scene_manager
# from .ui import main_window

# Package metadata
__version__ = "0.1.0"
__author__ = "thomasprogramming2018, raytopia projects, s.u.p.e"
__all__ = []