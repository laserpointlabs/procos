"""
ProcOS Microkernel Package

The minimal bootstrap system for Process-Oriented Operating System.
"""

from .procos_kernel import ProcOSKernel, ProcOSConfig

__version__ = "1.0.0"
__author__ = "ProcOS Development Team"

__all__ = ['ProcOSKernel', 'ProcOSConfig']