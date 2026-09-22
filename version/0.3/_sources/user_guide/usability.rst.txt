.. _ref_usability_features:

Explore usability features
==========================

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
   <post_processing_session>.results.subdomain["<name>"] (Object)
   <post_processing_session>.results.case["<name>"].subdomain["<name>"] (Object)
   <post_processing_session>.results.data_reader.case["<name>"].subdomain["<name>"] (Object)
   >>>
   >>> # Search within a specific API object
   >>> pypost = pycfx.PostProcessing.from_install()
   >>> pycfx.search("subdomain", search_root=pypost)
   <search_root>.results.subdomain["<name>"] (Object)
   <search_root>.results.case["<name>"].subdomain["<name>"] (Object)
   <search_root>.results.data_reader.case["<name>"].subdomain["<name>"] (Object)
   >>>
   >>> # Perform a whole word search (doesn't match "subdomain")
   >>> pycfx.search("domain", search_root=pypost, match_whole_word=True)
   <search_root>.results.domain["<name>"] (Object)
   <search_root>.results.case["<name>"].domain["<name>"] (Object)
   <search_root>.results.data_reader.case["<name>"].domain["<name>"] (Object)
