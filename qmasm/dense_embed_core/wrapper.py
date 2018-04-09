'''
Created on April 3, 2018

@author: JosePinilla
'''

import traceback
import networkx as nx
import dwave_networkx as dnx
import math

try:
    from embed import denseEmbed, setChimera
    from convert import convertToModels
    from utilities import linear_to_tuple, tuple_to_linear
except Exception as e:
    print('Could not load dense embedding method...')
    print (traceback.print_exc())


DENSE_TRIALS = 10

def parse_chimera(edgeset, t=4):
    '''
    Args:
        edgeset:
            Iterable object containing pairs of integers representing edges
        t:
            Number of qubits per shore in the chimera graph. (default=4)
    '''
    # Create the graph from the nodes and edges of the structured solver
    nodeset = set()
    for u,v in edgeset:
        nodeset.add(u)
        nodeset.add(v)

    m = n = int(( math.sqrt( (len(nodeset)/(t*2))) ))
    chimera = dnx.chimera_graph(m,n,t,None,nodeset,edgeset)

    chimera_adj_linear = {k : [i for i in chimera.adj[k].keys()] for k in nodeset}
    chimera_adj = {linear_to_tuple(k,m,n,t,True): [linear_to_tuple(i,m,n,t,True) for i in chimera.adj[k].keys()] for k in nodeset}

    chimera_adj_tuples = set( (u,v) for u in chimera_adj_linear for v in chimera_adj_linear[u] ) | set( (u,u) for u in chimera_adj_linear )

    return chimera_adj, m, n, t

def parse_problem(edgeset):

    problem = nx.Graph(edgeset)
    problem_adj = {k : [i for i in problem.adj[k].keys()] for k in problem}

    return problem_adj


def find_dense_embedding(Q, A, **params):
    """Attempts to find an embedding of a QUBO/Ising problem in a graph.

    This function is entirely heuristic: failure to return an embedding
    does not prove that no embedding exists. (can be interrupted by
    Ctrl-C, will return the best embedding found so far.)

    Function call:
       embeddings = find_dense_embedding(Q, A, **params)

    Args:
        Q: Edge structures of a problem. The embedder only cares about
            the edge structure (i.e. which variables have a nontrivial
            interactions), not the coefficient values. (must be an
            iterable object containing pairs of integers representing
            edges)

        A: Adjacency matrix of the graph. (must be an iterable object
            containing pairs of integers representing edges)

        **params: keyword parameters for find_dense_embedding.

            verbose: 0/1/2

    Returns:
        embeddings: A list of lists of embeddings. embeddings[i] is the
            list of qubits representing logical variable i. If
            the algorithm fails, the output is an empty list."""

    if 'verbose'  in params:
        verbose = params['verbose']
    else:
        verbose = 0

    chimera_adj, m, n, t = parse_chimera(A)

    problem_adj = parse_problem(Q)

    # format embedding parameters
    setChimera(chimera_adj, m, n, t)

    # run a number of embedding and choose the best
    embeds = []
    for trial in range(DENSE_TRIALS):
        if verbose: print('Trial {0}...'.format(trial))
        try:
            cell_map, paths = denseEmbed(problem_adj, write=False)
            if verbose: print('success')
        except Exception as e:
            print('failed')
            print (traceback.print_exc())
            continue
        embeds.append((cell_map, paths))

    if len(embeds) == 0:
        raise Exception('No embedding found')

    # sort embedding by number of qubits used (total path length)
    cell_map, paths = sorted(embeds, key=lambda x: sum([len(p) for p in x[1]]))[0]

    # get cell models
    if verbose: print('Converting to models...')
    models, max_model = convertToModels(paths, cell_map)
    if verbose: print('done')

    embedding = []

    for k in models:
        qubits = [tuple_to_linear(tup=v,M=m,N=n,index0=True) for v in models[k]['qbits']]
        embedding.append(qubits)

    return embedding


if __name__ == '__main__':

    chimera_file = "../../extras/chimera16.txt"

    file = open(chimera_file,"r")

    A = []

    for line in file:
        u,v = line.split()
        A.append((int(u),int(v)))

    #Q = [   (0,1), (0,3), (0,2), (1,2), (1,4), (2,3), (2,4), (2,5), (3,5), (4,6), (5,6)]
    #Q = [   (0,1), (0,3), (0,2), (3,2)]


    # K3, which can only be embedded by adding a chain
    Q = [(1,2),(2,3),(1,3)]

    find_dense_embedding(Q, A, verbose=0)
