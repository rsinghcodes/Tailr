import os
import sys

# Add the apps/backend directory to python search path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
