import pytest
from unittest.mock import Mock

import pandas as pd

from econci import Complexity


class TestComplexity():

    def test_initialization(self):
        df = pd.DataFrame()
        c = 'country'
        p = 'product'
        values = 'export'
        m_cp_thresh = 0.5

        comp = Complexity(df, c, p, values, m_cp_thresh)

        assert comp._df.equals(df)
        assert comp._c == c
        assert comp._p == p
        assert comp._values == values
        assert comp._m_cp_thresh == m_cp_thresh

        # test check_df
        with pytest.raises(TypeError):
            comp = Complexity(None, c, p, values, m_cp_thresh)
