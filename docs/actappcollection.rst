ActAppCollection Class
======================

ActAppsCollection represents a collection of Actifio applications generated using :doc: `Actifio.get_applications() </actifio>` method. ActAppsCollection is a iterable collection.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   actapplication

.. automodule:: Actifio
.. autoclass:: ActAppCollection
   :members:


Example: 
--------

.. code-block:: python

  # to get all SQL Server..

  sql_apps = appliance.get_applications(friendlytype="SQLServer")

  # or to get both SQL Server and SQL Instance types

  all_sql_apps = appliance.get_applications(friendlytype="SQLServer*")

  for app in sql_apps:
    print(app)

