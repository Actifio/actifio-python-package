ActApplication Class
====================

ActImage object represent a Actifio backup image. This is a returned as part of a ActImageCollection through interable protocol, or through and index.

Method Actifio.get_image_bytime() would return the ``ActImage``, instead of the ``ActImageCollection``.


.. automodule:: Actifio
.. autoclass:: ActApplication
   :members:

Example:
--------

.. code-block:: python

  apps = appliance.get_applications(appname="mydb")

  if len(apps) > 0:
    myapp = apps[0]
    
  print(type(myapp))

  >>> Actifio.ActSupportClasses.ActApplication

  