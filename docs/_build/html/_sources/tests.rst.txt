Tests for Portal Functionality
==============================

The unit tests that we have in place for testing all of the CSLC portal functionality utilize the PyTest module.
PyTest is a framework for writing varius tytpes of tests that we have in place such as unit tests, integration tests,
and end-to-end tests that involve every aspect of the CSLC portal. Below we will outline the framework and what the indivudal tests do.

Configuration for Tests
-----------------------

.. automodule:: tests.conftest
   :members:
   :undoc-members:
   :show-inheritance:

Create Ticket Tests
---------------------------------

.. automodule:: tests.test_create_ticket
   :members:
   :undoc-members:
   :show-inheritance:

Testing Unauthorized Functionality
------------------------------------

.. automodule:: tests.test_portal_anonymous
   :members:
   :undoc-members:
   :show-inheritance:

Testing Authorized Functionality
---------------------------------

.. automodule:: tests.test_portal_auth
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: tests
   :members:
   :undoc-members:
   :show-inheritance:
