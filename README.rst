======
econci
======


.. image:: https://img.shields.io/pypi/v/econci.svg
        :target: https://pypi.python.org/pypi/econci

.. image:: https://img.shields.io/travis/phcsoares/econci.svg
        :target: https://travis-ci.com/phcsoares/econci

.. image:: https://readthedocs.org/projects/econci/badge/?version=latest
        :target: https://econci.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




"Calculates Economic Complexity Indexes"


* Free software: MIT license

This package implements the indexes found in the Atlas of Economic Complexity [HaRH2014]_.

Installation
------------

        pip install econci

Usage
-----

.. code-block:: python

        import econci
        
        comp = econci.Complexity(df, c='country', p='product', values='export')
        comp.calculate_indexes()
        eci = comp.eci
        pci = comp.pci

        comp.create_product_space()
        prod_space = com.product_space
        econci.edges_nodes_to_csv(prod_space, graph_name='prod_space', dir_path='./data/')


References
----------

.. [HaRH2014] Hausmann, R., Hidalgo, C. A., Bustos, S., Coscia, M., Chung, S., Jimenez, J., … Yildirim, M. A. (2014). The Atlas of Economic Complexity: Mapping Paths to Prosperity. MIT Press.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
