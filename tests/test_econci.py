import pytest

import pandas as pd
import networkx as nx

from econci import Complexity


class TestComplexity():

    def _get_instance(self, df: pd.DataFrame) -> Complexity:
        return Complexity(df=df, c='country', p='product', values='export', m_cp_thresh=1)

    def test_initialization(self):
        df = pd.DataFrame()
        c = 'country'
        p = 'product'
        values = 'export'
        m_cp_thresh = 0.5

        comp = Complexity(df, c, p, values, m_cp_thresh)

        assert comp._df.equals(df)
        assert comp.c == c
        assert comp.p == p
        assert comp.values == values
        assert comp.m_cp_thresh == m_cp_thresh

        # test check_df
        with pytest.raises(TypeError):
            comp = Complexity(None, c, p, values, m_cp_thresh)

    def test_calculate_correct_indexes(
        self,
        data_stub: pd.DataFrame,
        correct_rca_stub: pd.DataFrame,
        correct_m_stub: pd.DataFrame,
    ):
        comp = self._get_instance(data_stub)
        comp.calculate_indexes()

        assert comp.m.equals(correct_m_stub)
        assert comp.rca.round(4).equals(correct_rca_stub)
        assert list(comp.eci['eci'].round(3).values) == [0.707, 0.707, -1.414]
        assert list(comp.pci['pci'].round(3).values) == [1.414, -0.707, -0.707]

    def test_create_product_space(
        self,
        data_stub: pd.DataFrame
    ):
        comp = self._get_instance(data_stub)
        comp.calculate_indexes()
        comp.create_product_space()

        assert isinstance(comp.complete_graph, nx.Graph)
        assert isinstance(comp.maxst, nx.Graph)
        assert isinstance(comp.product_space, nx.Graph)
