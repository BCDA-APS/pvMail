.. $Id: test_database.rst 669 2011-11-28 19:01:45Z jemian $

EPICS test database
==================================

To test the program during its development, a test database
(:ref:`test_database`)
was prepared.  The database creates two PVs:

``pvMail:trigger``
	the PV to watch

``pvMail:message``
	the message to be sent

starting: softIoc
-----------------
	
Start the database by adding it to an existing EPIC IOC configuration
or by starting a soft IOC using the ``softIoc`` program :index:`softIOC`
from EPICS base.
Here is an example of how that looks from a Linux command shell:

.. code-block:: bash
   :linenos:

   $ softIoc -d test.db 
   Starting iocInit
   ############################################################################
   ## EPICS R3.14.12 $Date: Wed 2010-11-24 14:50:38 -0600$
   ## EPICS Base built Feb 27 2011
   ############################################################################
   iocRun: All initialization complete
   epics> 

.. note::
   Here, the shell prompt is signified by the ``$`` symbol.

watching: camonitor
-------------------

Once the EPICS IOC is started and the PVs are available, 
it is possible to watch them
for any changes from the command line using the ``camonitor`` :index:`camonitor`
application from EPICS base::
    
    $ camonitor pvMail:trigger pvMail:message
	pvMail:trigger                 <undefined> off UDF INVALID
	pvMail:message                 <undefined> pvMail default message UDF INVALID

.. note::
   Do not be concerned about the ``UDF INVALID`` notices, they will disappear
   once the PVs have been written to at least once.

changing a PV: caput
--------------------

You can test changing the value of the trigger PV using the ``caput`` :index:`caput`
application from EPICS base::

    $ caput pvMail:trigger 1
	Old : pvMail:trigger                 off
	New : pvMail:trigger                 on


.. _test_database:

test.db
---------------

.. index:: test.db

Here is the full listing of the test EPICS database used for program development.

.. literalinclude:: ../../src/PvMail/test.db
   :language: text
   :emphasize-lines: 17,23
   :linenos:
