Portal Blueprints
======================

The blueprints module is the main driving code of the CSLC portal. It includes two key "submodules" that are: views and auth
Views is the main componenet that sets up all of the routes that handle all of the logic that deals with ticket creation, deletion,
editing, etc. Auth is the main component that ensures that the MicrosfotAuthenticator library is setup correctly and that all users who
access the UNO CSLC Tutoring Portal are correctly authenticated and only certain access is granted to certain web pages.

Authorization (Auth) Component
------------------------------

.. automodule:: app.blueprints.auth
   :members:
   :undoc-members:
   :show-inheritance:

Views Component
---------------------------

.. automodule:: app.blueprints.views
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: app.blueprints
   :members:
   :undoc-members:
   :show-inheritance:
