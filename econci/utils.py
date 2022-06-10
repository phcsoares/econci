import pandas as pd
import networkx as nx
import functools


def edges_nodes_to_csv(graph: nx.Graph, graph_name: str, dir_path: str) -> None:
    '''
    Saves two csv files, one with the edges and another with the nodes information.

    Parameters
    ----------
    graph : networkx.Graph
        Graph to be saved.
    graph_name : str
        Name of the graph.
    dir_path : str
        Path to directory where graph will be saved.
    '''
    nodes = [(ind, node) for ind, node in zip(range(len(list(graph.nodes))), list(graph.nodes))]
    dic_nodes = {node: ind for ind, node in zip(range(len(list(graph.nodes))), list(graph.nodes))}
    nodes = pd.DataFrame(nodes, columns=['id', 'name'])

    edges = nx.to_pandas_edgelist(graph)
    edges[['source', 'target']] = edges[['source', 'target']].replace(dic_nodes)

    if not dir_path.endswith('/'):
        dir_path += '/'
    edges_path = dir_path + graph_name + '_edges.csv'
    nodes_path = dir_path + graph_name + '_nodes.csv'

    edges.to_csv(edges_path, index=False)
    nodes.to_csv(nodes_path, index=False)


def check_if_indexes(func):
    @functools.wraps(func)
    def decor_check(self, *args, **kwargs):
        if hasattr(self, '_m'):
            return func(self, *args, **kwargs)
        else:
            raise Exception('First, calculate indexes!')
    return decor_check


def check_if_graph(func):
    @functools.wraps(func)
    def decor_check(self, *args, **kwargs):
        if hasattr(self, '_complete_graph'):
            return func(self, *args, **kwargs)
        else:
            raise Exception('First, create the Product Space!')
    return decor_check
