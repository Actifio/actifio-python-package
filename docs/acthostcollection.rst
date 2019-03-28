ActHostCollection Class
=======================

ActHostCollection represents a collection of Actifio hosts generated using :doc: `Actifio.get_hosts() </actifio>` method. ActHostCollection is a iterable collection.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   acthost

.. automodule:: Actifio
.. autoclass:: ActHostCollection
   :members:


Example: 
--------

.. code-block:: python

  hosts = appliance.get_hosts(hostname="myVM", isvm="true")

  print(hosts)

  >>> Collection of 1 hosts.

  print(len(hosts))

  >>> 1