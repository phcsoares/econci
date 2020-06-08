======
econci
======


.. image:: https://img.shields.io/pypi/v/econci.svg
        :target: https://pypi.python.org/pypi/econci




Calculates Economic Complexity Indexes


* Free software: MIT license

This package implements the indexes found in the Atlas of Economic Complexity [HaRH2014]_.
It also creates the Product Space.

Installation
------------

:code:`econci` can be installed from PyPI::

        pip install econci

or from Anaconda::

        conda install -c phcsoares econci

Usage
-----

.. code-block:: python

        import econci
        
        comp = econci.Complexity(df, c='country', p='product', values='export')
        comp.calculate_indexes()
        eci = comp.eci
        pci = comp.pci

        # creating the product space
        comp.create_product_space()
        
        # the graphs are networkx.Graph objects
        complete_graph = comp.complete_graph  # complete product space
        max_spanning_tree = comp.maxst  # maximum spanning tree
        prod_space = comp.product_space  # product space

        # edges_nodes_to_csv saves one csv file with edges and weights
        # and another file with nodes information
        econci.edges_nodes_to_csv(prod_space, graph_name='prod_space', dir_path='./data/')

Complete list of calculated indexes:

* Economic Complexity Index: :code:`comp.eci`
* Product Complexity Index: :code:`comp.pci`
* Country Diversity: :code:`comp.diversity`
* Product Ubiquity: :code:`comp.ubiquity`
* Balassa's RCA: :code:`comp.rca`
* Proximity: :code:`comp.proximity`
* Density: :code:`comp.density`
* Distance: :code:`comp.distance`

You can also vary the threshold of RCA value when creating the Mcp matrix.
The :code:`Complexity` class accepts the parameter :code:`m_cp_thresh`, which by default is :code:`1.0`.

:code:`comp.create_product_space()` also accepts the argument :code:`edge_weight_thresh`, by default :code:`0.65`.
This argument filters edges to be added to the maximum spanning tree by weight.

References
----------

.. [HaRH2014] Hausmann, R., Hidalgo, C. A., Bustos, S., Coscia, M., Chung, S., Jimenez, J., … Yildirim, M. A. (2014). The Atlas of Economic Complexity: Mapping Paths to Prosperity. MIT Press.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
