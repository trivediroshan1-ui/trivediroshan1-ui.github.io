#!/usr/bin/env python3
"""The MCP lab's sub-nav now comes from lab_nav.py. Running this runs add-lab-nav.py, so the old tab bar never comes back."""
import pathlib, runpy
runpy.run_path(str(pathlib.Path(__file__).resolve().parent / "add-lab-nav.py"), run_name="__main__")
