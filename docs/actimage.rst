ActImage Class
==============

ActImage object represent a Actifio backup image. This is a returned as part of a ActImageCollection through interable protocol, or through and index.

Method Actifio.get_image_bytime() would return the ``ActImage``, instead of the ``ActImageCollection``.


.. automodule:: Actifio
.. autoclass:: ActImage
   :members:

Example:
--------

.. code-block:: python

  images = appliance.get_images(appname="mydb", jobclass="OnVault")

  firstimage = images[0]

  print(type(firstimage))

  >>> Actifio.ActSupportClasses.ActImage

  