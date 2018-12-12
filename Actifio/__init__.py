import sys

if sys.version [:3] == "2.7":
  from Actifio import Actifio
elif sys.version[0] == "3":
  from .Actifio import Actifio 

__all__ = ['Actifio']