#!/usr/bin/env python3
"""
Get Session Context for AI Agent.

Usage:
    C:\Users\limin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe get_context.py           Output context in text format
    C:\Users\limin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe get_context.py --json    Output context in JSON format
"""

from __future__ import annotations

from common.git_context import main


if __name__ == "__main__":
    main()
