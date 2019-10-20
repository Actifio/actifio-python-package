.. Actifio python Client Library documentation master file, created by
   sphinx-quickstart on Mon Mar 25 12:22:07 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Actifio python client library documentation!
=========================================================

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   actifio
   actimgcollection
   actjobcollection
   actappcollection
   acthostcollection


How to install?
---------------

To install the Actifio module, from a command line interaface:

.. code-block:: shell

  → pip install Actifio

This will ensure all the dependencies are managed and installed with the Actifio module installation. Once installed:

.. code-block:: shell

  → pip show Actifio
  Name: Actifio
  Version: 0.9.0
  Summary: Actifio Restful API wrapper for Python.
  Home-page: https://github.com/Actifio/actifio-python-package
  Author: Kosala Atapattu
  Author-email: kosala.atapattu@actifio.com
  License: MIT
  Location: /usr/local/lib/python2.7/site-packages
  Requires: urllib3
  Required-by: 


Geting started!!!
=================

By design philosophy of this library is to make sure that the user experience is consistent to the actual product. First you can import the module by:

.. code-block:: python

  from Actifio import Actifio

The library supports two modes of authentication, either using username or password, or using token generated locally.

* Username and Password
-----------------------

With the same information you use to login to the appliance, you can create a appliance object.

.. code-block:: python

  appliance = Actifio("myappliance", "my_scripting_user", "super_secret")

Or

* With Token
------------

You can generate a token using the script in '''bin/''' folder, or using the command. To generate a token:

.. code-block:: python

  $ bin/actgentoken 
  Username: demo
  Password: 
  Confirm password: 



  ================Token====================

  b'eyAidXNlcm5hbWUiOiAiZGVtbyIsICJwYXNzd29yZCI6ICJkZW1vIiB9\n'

  =========================================

Once the token is generated, appliance object can be instantiated as following:

.. code-block:: python

  appliance = Actifio("myappliance", token=b'eyAidXNlcm5hbWUiOiAiZGVtbyIsICJwYXNzd29yZCI6ICJkZW1vIiB9\n')


Once the appliance object is instatiated, we can perform the operations we perform on the applaince.

List all the hosts, for example:

.. code-block:: python

  hosts = appliance.get_hosts(hostname="my_host")

  # and to see the top host in my List

  host = hosts[0]

  # or refine further

  hosts = appliance.get_hosts(hostname="my_host", isvm="true")

Or find an application:

.. code-block:: python

  apps = appliance.get-applications(appname="mydb")

  # and to see the top application in my List

  if len(apps) > 0:
    app = apps[0]

  # or refine further, and get my Oracle database

  hosts = appliance.get_applications(appname="mydb", friendlytype="Oracle")

Once I have that, then I can perform the actions I usually perform... create a virtual clone of a DB ``appliance.clone_database()`` or create a instant mount ``appliance.clone_database()``. Checkout the examples section for more details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

