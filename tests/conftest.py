import pytest

import pandas as pd
import numpy as np


@pytest.fixture
def data_stub():
    return pd.DataFrame({
        'country': ['A', 'A', 'A', 'B', 'B', 'C'],
        'product': ['P1', 'P2', 'P3', 'P1', 'P2', 'P1'],
        'export': [10, 20, 30, 40, 50, 60],
    })


@pytest.fixture
def correct_m_stub():
    return pd.DataFrame(
        np.array([[10., 20., 30.],
                  [40., 50., 0.],
                  [60., 0., 0.]]),
        index=pd.Index(['A', 'B', 'C'], name='country'),
        columns=pd.Index(['P1', 'P2', 'P3'], name='product')
    )


@pytest.fixture
def correct_rca_stub():
    return pd.DataFrame(
        np.array([[0.3182, 1., 3.5],
                  [0.8485, 1.6667, 0.],
                  [1.9091, 0., 0.]]),
        index=pd.Index(['A', 'B', 'C'], name='country'),
        columns=pd.Index(['P1', 'P2', 'P3'], name='product')
    )
