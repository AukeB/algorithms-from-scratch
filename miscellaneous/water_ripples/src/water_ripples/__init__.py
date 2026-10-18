"""Water ripples simulation: a 2D discrete wave equation rendered with PyGame."""

import os

# Make sure numba-compiled code runs on different CPU architectures. This must be set before numba is
# imported, which is why it lives in the package __init__ (it runs before any submodule).
os.environ["NUMBA_CPU_NAME"] = "generic"
