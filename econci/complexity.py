import pandas as pd
import numpy as np
import networkx as nx
from .utils import check_if_indexes, check_if_graph


class Complexity():
    """
    Calculates complexity indexes.
    """

    def __init__(self, df: pd.DataFrame, c: str, p: str, values: str, m_cp_thresh: float = 1.0):
        """
        Parameters
        ----------
        df : pandas.DataFrame
            Data used in calculations.
        c : str
            Column equivalent to country.
        p : str
            Column equivalent to product.
        values : str
            Column with the values on which to calculate the indexes.
        m_cp_thresh : float, optional
            Threshold applied to RCA values when creating M_cp. Larger or equal values of RCA become 1 in M_cp,
            by default 1.0
        """
        self._check_df(df)
        self._df = df.copy()
        self._c = c
        self._p = p
        self._values = values
        self._m_cp_thresh = m_cp_thresh

    def _check_df(self, df: pd.DataFrame):
        """
        Checks if df is a pandas.DataFrame.

        Parameters
        ----------
        df :
            Data used in calculations.

        Raises
        ------
        Exception
            `df` is not pandas.DataFrame.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError('df must be a pandas.DataFrame.')

    def _get_m(self):
        """
        Pivots the initial `df` so that rows are `c`, columns are `p` and cells are the sum of `values`.
        """
        self._m = self._df.groupby([self._c, self._p])[self._values].sum().unstack().fillna(0)

    def _calc_rca(self):
        """
        Calculates Balassa's RCA.
        """
        sum_p = self._m.sum(axis=0)
        sum_c = self._m.sum(axis=1)
        sum_tt = sum_c.sum()

        self._rca = self._m.apply(lambda x: (x / sum_c.loc[x.index]) / (sum_p.loc[x.name] / sum_tt))

    def _get_m_cp(self):
        """
        Creates the M_cp binary matrix.
        """
        m_cp = self._rca.copy()
        thresh = self._m_cp_thresh
        m_cp[m_cp >= thresh] = 1
        m_cp[m_cp < thresh] = 0
        m_cp = m_cp[(m_cp != 0).all(axis=0).index]
        m_cp = m_cp.loc[(m_cp != 0).all(axis=1).index]
        self._m_cp = m_cp

    def _fix_sign(self, k: pd.Series, ci: pd.DataFrame) -> pd.DataFrame:
        """
        Fixes the sign of a complexity index.
        The Eigenvalues and Eigenvectors may switch sign, hence the need for the correction.

        Parameters
        ----------
        k : pandas.Series
            Either diversity or ubiquity.
        ci : pandas.DataFrame
            Calculated complexity index.

        Returns
        -------
        pandas.DataFrame
            Corrected sign of complexity index
        """
        corr = np.corrcoef(k, ci.iloc[:, 0])[0, 1]
        corr_sign = np.sign(corr)
        ci *= corr_sign
        return ci

    def _get_diversity(self):
        """
        Calculates the diversity of countries.
        """
        self._diversity = self._m_cp.sum(axis=1)

    def _get_ubiquity(self):
        """
        Calculates the ubiquity of proudcts.
        """
        self._ubiquity = self._m_cp.sum(axis=0)

    def _calc_eci(self):
        """
        Calculates the Ecomomic Complexity Index.
        """
        kc0 = self._diversity
        kp0 = self._ubiquity

        m_tilda_cc = ((self._m_cp).dot((self._m_cp / kp0).T) / kc0).T

        vals_c, vecs_c = np.linalg.eig(m_tilda_cc)
        ind = vals_c.argsort()[-2]
        eci = np.real(vecs_c[:, ind])
        eci = (eci - eci.mean()) / eci.std()
        eci = pd.DataFrame(eci, index=self._m_cp.index, columns=["eci"])

        self._eci = self._fix_sign(kc0, eci)

    def _calc_pci(self):
        """
        Calculates the Product Complexity Index.
        """
        kc0 = self._diversity
        kp0 = self._ubiquity

        m_tilda_pp = ((self._m_cp.T).dot((self._m_cp.T / kc0).T) / kp0).T

        vals_p, vecs_p = np.linalg.eig(m_tilda_pp)
        ind = vals_p.argsort()[-2]
        pci = np.real(vecs_p[:, ind])
        pci = (pci - pci.mean()) / pci.std()
        pci = pd.DataFrame(pci, index=self._m_cp.columns, columns=["pci"])

        self._pci = self._fix_sign(kp0, pci) * (-1)  # PCI is negatively correlated with ubiquity

    def _calc_proximity(self):
        """
        Calculates the proximity matrix between products.
        """
        kp0 = self._ubiquity
        phi = self._m_cp.T.dot(self._m_cp)
        phi_pp = phi.apply(lambda x: x / np.maximum(kp0.loc[x.name], kp0.loc[x.index]))
        np.fill_diagonal(phi_pp.values, 0)
        self._proximity = phi_pp

    def _calc_density(self):
        """
        Calculates the density of a product in a country.
        """
        self._density = self._m_cp.dot(self._proximity) / self._proximity.sum(axis=1)

    def _calc_distance(self):
        """
        Calculates the distance of a product to a country.
        """
        self._distance = 1 - self._density

    def calculate_indexes(self):
        """
        Calculates all indexes.
        """
        self._get_m()
        self._calc_rca()
        self._get_m_cp()
        self._get_diversity()
        self._get_ubiquity()
        self._calc_eci()
        self._calc_pci()
        self._calc_proximity()
        self._calc_density()
        self._calc_distance()

    def _generate_graphs(self):
        """
        Creates the complete graph from the proximity matrix and finds its
        maximum spanning tree.
        """
        self._complete_graph = nx.from_pandas_adjacency(self._proximity)
        self._maxst = nx.maximum_spanning_tree(self._complete_graph)

    @check_if_indexes
    def create_product_space(self, edge_weight_thresh: float = 0.65):
        """
        Creates the product space

        Parameters
        ----------
        edge_weight_thresh : float, optional
            Wheight threshold for extra edges to be added to the maximum
            spanning tree, by default 0.65
        """
        if not hasattr(self, '_complete_graph'):
            self._generate_graphs()

        self._product_space = self._maxst.copy()
        for e in self._complete_graph.edges(data=True):
            if (e not in self._product_space.edges()) and (e[2]['weight'] > edge_weight_thresh):
                self._product_space.add_edges_from([e])

    @property
    def c(self):
        return self._c

    @property
    def p(self):
        return self._p

    @property
    def values(self):
        return self._values

    @property
    def m_cp_thresh(self):
        return self._m_cp_thresh

    @property
    @check_if_indexes
    def m(self):
        return self._m.copy()

    @property
    @check_if_indexes
    def rca(self):
        return self._rca.copy()

    @property
    @check_if_indexes
    def m_cp(self):
        return self._m_cp.copy()

    @property
    @check_if_indexes
    def diversity(self):
        return self._diversity.to_frame('diversity').reset_index().copy()

    @property
    @check_if_indexes
    def ubiquity(self):
        return self._ubiquity.to_frame('ubiquity').reset_index().copy()

    @property
    @check_if_indexes
    def eci(self):
        return self._eci.reset_index().copy()

    @property
    @check_if_indexes
    def pci(self):
        return self._pci.reset_index().copy()

    @property
    @check_if_indexes
    def proximity(self):
        return self._proximity.copy()

    @property
    @check_if_indexes
    def density(self):
        return self._density.copy()

    @property
    @check_if_indexes
    def distance(self):
        return self._distance.copy()

    @property
    @check_if_graph
    def complete_graph(self):
        return self._complete_graph

    @property
    @check_if_graph
    def maxst(self):
        return self._maxst

    @property
    @check_if_graph
    def product_space(self):
        return self._product_space
