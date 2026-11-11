"""Make the backend modules importable when running pytest from the backend folder."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
