ActJob Class
============

ActJob object represent a Actifio backup image. This is returned as part of a ActJobsCollection through interable protocol, or through and index.

Method ``Actifio.clone_database()`` and ``Actifio.simple_mount()`` would return the ``ActJob`` and :doc: `ActImage </actimage>` in a tuple


.. automodule:: Actifio
.. autoclass:: ActJob
   :members:

Example:
--------

.. code-block:: python

  jobs = appliance.get_jobs(hostname="myVM", jobclass="dedup", status="running")

  if len(jobs) > 0:
    firstjob = jobs[0]

  # or from a mount operation 

  job, image = appliance.simple_mount(source_application=apps[0], target_host=hosts[0])

  while job.status == "running":
    print("Still Running")
  print("Phew, it's done.")

  