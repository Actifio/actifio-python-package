import sys

if sys.version [:3] == "2.7":
  from Actifio import Actifio
  from ActSupportClasses import ActHost, ActHostCollection, ActApplication, ActAppCollection, ActImage, ActImageCollection, ActJob, ActJobsCollection
elif sys.version[0] == "3":
  from .Actifio import Actifio 
  from Actifio.ActSupportClasses import ActHost, ActHostCollection, ActApplication, ActAppCollection, ActImage, ActImageCollection, ActJob, ActJobsCollection

__all__ = ['Actifio','ActHost', 'ActHostCollection', 'ActApplication', 'ActAppCollection', 'ActImage', 'ActImageCollection', 'ActJob', 'ActJobsCollection']
