#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports like src.microkernel.procos_kernel
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


