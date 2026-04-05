#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_requirements.py - wrapper for backward compatibility.
Logic moved to processes/SETUP/setup_01_check_requirements.py
"""
import sys
from processes.SETUP.setup_01_check_requirements import check_all

if __name__ == "__main__":
    installed, missing = check_all()
    for p in installed:
        print(f"   OK  {p}")
    for p in missing:
        print(f"   MISS {p} -- not installed")
    if missing:
        print(f"\nMISSING: {len(missing)} package(s)")
        sys.exit(1)
    else:
        print("\nALL OK")
        sys.exit(0)
