ActHost Class
=============

ActHost object represent a Actifio host entry. This is returned as part of a ActHostsCollection through interable protocol, or through and index.

Method ``Actifio.clone_database()`` and ``Actifio.simple_mount()`` would take ``ActHost`` as an argument.


.. automodule:: Actifio
.. autoclass:: ActHost
   :members:

Example:
--------

.. code-block:: python

  hosts = appliance.get_hosts(hostname="myVM", isvm="true")

  for host in hosts:
    print(host)

  print(type(host))

  >>> Actifio.ActSupportClasses.ActHost
