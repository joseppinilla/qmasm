'''
Created on April 3, 2018

@author: JosePinilla
'''

import traceback
import networkx as nx
import dwave_networkx as dnx
import qmasm
import math
import sys

SPACING=1

try:
    from embed import layoutEmbed, layoutToModels
    from embed import layoutConfiguration, setProblem, setTarget
except Exception as e:
    sys.stderr.write('Could not load layout embedding method...')
    print (traceback.print_exc())

def linear_to_tuple(qubit,N,M,L):

    qpr = 2*N*L     # qbits per row
    qpt = 2*L       # qbits per tile

    row, rem = divmod(qubit, qpr)
    col, rem = divmod(rem, qpt)
    horiz, ind = divmod(rem, L)

    qubit_tuple = (row, col, horiz, ind)

    return qubit_tuple

def tuple_to_linear(tup, M, N, L=4):
    '''Convert a tuple format index of a qubit in an (N, M, L) processor
    to linear format'''

    qpr = 2*N*L     # qbits per row
    qpt = 2*L       # qbits per tile

    return qpr*tup[0]+qpt*tup[1]+L*tup[2]+tup[3]

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
    chimera_adj = {linear_to_tuple(k,m,n,t): [linear_to_tuple(i,m,n,t) for i in chimera.adj[k].keys()] for k in nodeset}

    chimera_adj_tuples = set( (u,v) for u in chimera_adj_linear for v in chimera_adj_linear[u] ) | set( (u,u) for u in chimera_adj_linear )

    return chimera_adj, m, n, t

def parse_problem(edgeset):

    problem = nx.Graph(edgeset)
    problem_adj = {k : [i for i in problem.adj[k].keys()] for k in problem}

    return problem_adj


def find_layout_embedding(Q, A, **params):
    """Attempts to find an embedding of a QUBO/Ising problem in a graph.

    This function is entirely heuristic: failure to return an embedding
    does not prove that no embedding exists. (can be interrupted by
    Ctrl-C, will return the best embedding found so far.)

    Function call:
       embeddings = find_layout_embedding(Q, A, **params)

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

            locations: problem nodes locations (list of coordinate pairs)

    Returns:
        embeddings: A list of lists of embeddings. embeddings[i] is the
            list of qubits representing logical variable i. If
            the algorithm fails, the output is an empty list."""

    if 'verbose'  in params:
        verbose = params['verbose']
    else:
        verbose = 0

    if 'locations'  in params:
        locations = params['locations']
    else:
        qmasm.abend("Embedder requires nodes locations")

    chimera_adj, m, n, t = parse_chimera(A)

    problem_adj = parse_problem(Q)

    stats = {}
    configuration = {}
    test_conf = {}
    test_conf['M'] = m
    test_conf['N'] = n
    test_conf['L'] = t
    test_conf['CIRCUIT'] = 'problem'
    test_conf['VERBOSE'] = False
    test_conf['SEED'] = 8
    test_conf['RANDOMIZE_CANDIDATES'] = False
    test_conf['PLOT'] = False
    layoutConfiguration(configuration,test_conf)

    try:
        setProblem(problem_adj, locations, SPACING)
        setTarget(chimera_adj)
        good, cell_map = layoutEmbed(configuration, stats)
        if good:
            sys.stderr.write('Layout-Aware Embedding Successful\n')
    except Exception as e:
        good = False
        if type(e).__name__ == 'KeyboardInterrupt':
            raise KeyboardInterrupt
        sys.stderr.write('Layout-Aware Embedding Failed')
        print (traceback.print_exc())
        return

    models = layoutToModels(cell_map)

    embedding = []

    for k in models:
        qubits = [tuple_to_linear(tup=v,M=m,N=n) for v in k]
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

    embedding = find_layout_embedding(Q, A, verbose=0, locations=[(0,0),(0,1),(1,0)])

    print(embedding)
