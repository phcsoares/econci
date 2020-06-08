import pandas as pd
import numpy as np
import networkx as nx
# import sys
# sys.path.append('/media/D/Documents/github/econci/econci')
from .utils import check_if_indexes, check_if_graph

class Complexity():
    '''
    Calculates complexity indexes.
    '''

    def __init__(self, df, c, p, values, m_cp_thresh=1.0):
        '''
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
            Threshold applied to RCA values when creating M_cp. Larger or equal values of RCA become 1 in M_cp, by default 1.0
        '''
        self.__check_df(df)
        self.__df = df.copy()
        self.__c = c
        self.__p = p
        self.__values = values
        self.__m_cp_thresh = m_cp_thresh

    def __check_df(self, df):
        '''
        Checks if df is a pandas.DataFrame.

        Parameters
        ----------
        df : 
            Data used in calculations.

        Raises
        ------
        Exception
            `df` is not pandas.DataFrame.
        '''
        if not isinstance(df, pd.DataFrame):
            raise Exception('df must be a pandas.DataFrame.')

    def __get_m(self):
        '''
        Pivots the initial `df` so that rows are `c`, columns are `p` and cells are the sum of `values`.
        '''
        self.__m = self.__df.groupby([self.__c, self.__p])[self.__values].sum().unstack().fillna(0)

    def __calc_rca(self):
        '''
        Calculates Balassa's RCA.
        '''
        sum_p = self.__m.sum(axis=0)
        sum_c = self.__m.sum(axis=1)
        sum_tt = sum_c.sum()
        
        self.__rca = self.__m.apply(lambda x: (x/sum_c.loc[x.index])/(sum_p.loc[x.name]/sum_tt))

    def __get_m_cp(self):
        '''
        Creates the M_cp binary matrix.
        '''
        m_cp = self.__rca.copy()
        thresh = self.__m_cp_thresh
        m_cp[m_cp >= thresh] = 1
        m_cp[m_cp < thresh] = 0
        m_cp = m_cp[(m_cp != 0).all(axis=0).index]
        m_cp = m_cp.loc[(m_cp != 0).all(axis=1).index]
        self.__m_cp = m_cp

    def __fix_sign(self, k, ci):
        '''
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
        '''
        corr = np.corrcoef(k, ci.iloc[:,0])[0,1]
        corr_sign = np.sign(corr)
        ci *= corr_sign
        return ci

    def __get_diversity(self):
        '''
        Calculates the diversity of countries.
        '''
        self.__diversity = self.__m_cp.sum(axis=1)
    
    def __get_ubiquity(self):
        '''
        Calculates the ubiquity of proudcts.
        '''
        self.__ubiquity = self.__m_cp.sum(axis=0)

    def __calc_eci(self):
        '''
        Calculates the Ecomomic Complexity Index.
        '''
        kc0 = self.__diversity
        kp0 = self.__ubiquity
        
        m_tilda_cc = ((self.__m_cp).dot((self.__m_cp/kp0).T) / kc0).T

        vals_c, vecs_c = np.linalg.eig(m_tilda_cc)
        ind = vals_c.argsort()[-2]
        eci = np.real(vecs_c[:,ind])
        eci = (eci - eci.mean())/eci.std()
        eci = pd.DataFrame(eci, index=self.__m_cp.index, columns=["eci"])

        self.__eci = self.__fix_sign(kc0, eci)

    def __calc_pci(self):
        '''
        Calculates the Product Complexity Index.
        '''
        kc0 = self.__diversity
        kp0 = self.__ubiquity

        m_tilda_pp = ((self.__m_cp.T).dot((self.__m_cp.T/kc0).T) / kp0).T

        vals_p, vecs_p = np.linalg.eig(m_tilda_pp)
        ind = vals_p.argsort()[-2]
        pci = np.real(vecs_p[:,ind])
        pci = (pci - pci.mean())/pci.std()
        pci = pd.DataFrame(pci, index=self.__m_cp.columns, columns=["pci"])

        self.__pci = self.__fix_sign(kp0, pci) * (-1)  # PCI is negatively correlated with ubiquity

    def __calc_proximity(self):
        '''
        Calculates the proximity matrix between products.
        '''
        kp0 = self.__ubiquity
        phi = self.__m_cp.T.dot(self.__m_cp)
        phi_pp = phi.apply(lambda x: x/np.maximum(kp0.loc[x.name], kp0.loc[x.index]))
        np.fill_diagonal(phi_pp.values, 0)
        self.__proximity = phi_pp

    def __calc_density(self):
        '''
        Calculates the density of a product in a country.
        '''
        self.__density = self.__m_cp.dot(self.__proximity) / self.__proximity.sum(axis=1)

    def __calc_distance(self):
        '''
        Calculates the distance of a product to a country.
        '''
        self.__distance = 1 - self.__density

    def calculate_indexes(self):
        '''
        Calculates all indexes.
        '''
        self.__get_m()
        self.__calc_rca()
        self.__get_m_cp()
        self.__get_diversity()
        self.__get_ubiquity()
        self.__calc_eci()
        self.__calc_pci()
        self.__calc_proximity()
        self.__calc_density()
        self.__calc_distance()

    def __generate_graphs(self):
        '''
        Creates the complete graph from the proximity matrix and finds its
        maximum spanning tree.
        '''
        self.__complete_graph = nx.from_pandas_adjacency(self.__proximity)
        self.__maxst = nx.maximum_spanning_tree(self.__complete_graph)
    
    @check_if_indexes
    def create_product_space(self, edge_weight_thresh=0.65):
        '''
        Creates the product space

        Parameters
        ----------
        edge_weight_thresh : float, optional
            Wheight threshold for extra edges to be added to the maximum
            spanning tree, by default 0.65
        '''
        if not hasattr(self, '__complete_graph'):
            self.__generate_graphs()
        
        self.__product_space = self.__maxst.copy()
        for e in self.__complete_graph.edges(data=True):
            if (e not in self.__product_space.edges()) and (e[2]['weight'] > edge_weight_thresh):
                self.__product_space.add_edges_from([e])

    @property
    def c(self):
        return self.__c
    
    @property
    def p(self):
        return self.__p
    
    @property
    def values(self):
        return self.__values
    
    @property
    def m_cp_thresh(self):
        return self.__m_cp_thresh

    @property
    @check_if_indexes
    def m(self):
        return self.__m.copy()

    @property
    @check_if_indexes
    def rca(self):
        return self.__rca.copy()

    @property
    @check_if_indexes
    def m_cp(self):
        return self.__m_cp.copy()

    @property
    @check_if_indexes
    def diversity(self):
        return self.__diversity.to_frame('diversity').reset_index().copy()

    @property
    @check_if_indexes
    def ubiquity(self):
        return self.__ubiquity.to_frame('ubiquity').reset_index().copy()

    @property
    @check_if_indexes
    def eci(self):
        return self.__eci.reset_index().copy()

    @property
    @check_if_indexes
    def pci(self):
        return self.__pci.reset_index().copy()

    @property
    @check_if_indexes
    def proximity(self):
        return self.__proximity.copy()

    @property
    @check_if_indexes
    def density(self):
        return self.__density.copy()

    @property
    @check_if_indexes
    def distance(self):
        return self.__distance.copy()

    @property
    @check_if_graph
    def complete_graph(self):
        return self.__complete_graph

    @property
    @check_if_graph
    def maxst(self):
        return self.__maxst

    @property
    @check_if_graph
    def product_space(self):
        return self.__product_space