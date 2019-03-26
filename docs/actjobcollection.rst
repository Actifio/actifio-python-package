ActJobsCollection Class
=======================

ActJobsCollection defines a iterable collection of Actifio jobs. ActJobCollection class objects are returned fron Actifio.get_jobs() method.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   actjob

.. automodule:: Actifio
.. autoclass:: ActJobsCollection
   :members:

Example: 
--------

.. code-block:: python

  jobs = appliance.get_images(appname="mydb", jobclass="snapshot")

  for job in jobs:
    print(image)

  # or refine further to find out running jobs

  jobs = appliance.get_images(appname="mydb", jobclass="snapshot", status="running")

  for job in jobs:
    print(image)

