import pandas as pd
import numpy as np
from scipy import linalg
from sklearn.preprocessing import scale
import networkx as nx

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

    # TODO: verificar o fix_sign, está funcionando com eci mas é o contrário com o pci

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

        _, vecs_c = linalg.eig(m_tilda_cc)
        eci = np.real(vecs_c[:,1:2])
        eci = scale(eci[:, 0:1], 
                    axis=0, 
                    with_mean=True, 
                    with_std=True, 
                    copy=True)
        eci = pd.DataFrame(eci, index=self.__m_cp.index, columns=["eci"])

        self.__eci = self.__fix_sign(kc0, eci)

    def __calc_pci(self):
        '''
        Calculates the Product Complexity Index.
        '''
        kc0 = self.__diversity
        kp0 = self.__ubiquity

        m_tilda_pp = ((self.__m_cp.T).dot((self.__m_cp.T/kc0).T) / kp0).T

        _, vecs_p = linalg.eig(m_tilda_pp)
        pci = np.real(vecs_p[:,1:2])
        pci = scale(pci[:, 0:1], 
                    axis=0, 
                    with_mean=True, 
                    with_std=True, 
                    copy=True)
        pci = pd.DataFrame(pci, index=self.__m_cp.columns, columns=["pci"])

        self.__pci = self.__fix_sign(kp0, pci) * (-1)  # Falta ser verificado

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
    def m(self):
        return self.__m

    @property
    def rca(self):
        return self.__rca

    @property
    def m_cp(self):
        return self.__m_cp

    @property
    def diversity(self):
        return self.__diversity

    @property
    def ubiquity(self):
        return self.__ubiquity

    @property
    def eci(self):
        return self.__eci

    @property
    def pci(self):
        return self.__pci

    @property
    def proximity(self):
        return self.__proximity

    @property
    def density(self):
        return self.__density

    @property
    def distance(self):
        return self.__distance

    @property
    def complete_graph(self):
        return self.__complete_graph

    @property
    def maxst(self):
        return self.__maxst

    @property
    def product_space(self):
        return self.__product_space