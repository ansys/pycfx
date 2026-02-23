.. _ref_usability_features:

Usability features
==================

API search
----------

The :ref:`API search <ref_search>` lets you search for a word throughout PyCFX's object hierarchy.

Examples
~~~~~~~~

.. code-block:: python

   >>> import ansys.cfx.core as pycfx
   >>>
   >>> # Search across all PyCFX modules
   >>> pycfx.search("subdomain")
   <pre_processing_session>.setup.flow["<name>"].domain["<name>"].subdomain["<name>"] (Object)
   <pre_processing_session>.setup.flow["<name>"].mesh_adaption.subdomain_list (Parameter)
   <post_processing_session>.setup.subdomain["<name>"] (Object)
   <post_processing_session>.setup.case["<name>"].subdomain["<name>"] (Object)
   <post_processing_session>.setup.data_reader.case["<name>"].subdomain["<name>"] (Object)
   >>>
   >>> # Search within a specific API object
   >>> pypost = pycfx.PostProcessing.from_install()
   >>> pycfx.search("subdomain", search_root=pypost)
   <search_root>.setup.subdomain["<name>"] (Object)
   <search_root>.setup.case["<name>"].subdomain["<name>"] (Object)
   <search_root>.setup.data_reader.case["<name>"].subdomain["<name>"] (Object)
   >>>
   >>> # Perform a whole word search (doesn't match "subdomain")
   >>> pycfx.search("domain", search_root=pypost, match_whole_word=True)
   <search_root>.setup.domain["<name>"] (Object)
   <search_root>.setup.case["<name>"].domain["<name>"] (Object)
   <search_root>.setup.data_reader.case["<name>"].domain["<name>"] (Object)
