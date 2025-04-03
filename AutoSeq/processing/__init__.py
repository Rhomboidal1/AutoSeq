"""Processing modules for different sequencing types."""
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ind import IndSequencing
from plate import PlateSequencing
from pcr import PCRSequencing

__all__ = ['IndSequencing', 'PlateSequencing', 'PCRSequencing']