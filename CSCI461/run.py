#!/usr/bin/env python3
"""
Executable CLI entrypoint for the registry scoring system.
This satisfies the autograder spec.
"""
from __future__ import annotations

import sys
from src.registry.cli import main

if __name__ == "__main__":
    sys.exit(main())

