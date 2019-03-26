ActImageCollection Class
========================

Iterable class of :doc:`ActImage </actimage>` collections. Returned by :ref: `Actifio.get_images()` method. 


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   actimage

.. automodule:: Actifio
.. autoclass:: ActImageCollection
   :members:


Example: 
--------

.. code-block:: python

  images = appliance.get_images(appname="mydb", jobclass="OnVault")

  for image in images:
    print(image)

  # or to list all backups taken last 24 hours.

  from datetime import datetime

  yesterday = datetime.today() - datetime.timedelta(day=1)

  for image in images:
    consistencydate = datetime.strptime(image.consistencydate[:-4], "%Y-%m-%d %H:%M:%S")
    if consistencydate > yesterday:
      print(image)

