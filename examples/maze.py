import networkx as nx
import matplotlib.pyplot as plt
from string import ascii_uppercase

cardinal = ['N',
            'S',
            'W',
            'E',
            '$a1']

c_loc = {   '$a1':(1,1),
            'N' : (1,0),
            'S' : (1,2),
            'E' : (2,1),
            'W' : (0,1)}

pin_loc = { 'N' : (2,0),
            'S' : (0,2),
            'E' : (2,2),
            'W' : (0,0)}


def maze(n=3,m=3):

    M = nx.Graph()
    loc_dict = {}

    for i in range(1,n+1):
        for j, C in enumerate(ascii_uppercase[:m], 1):
            # K5 per maze cell
            K5 = nx.complete_graph(5)
            label_dict = { c: C + str(i) + '.' + l   for c,l in enumerate(cardinal) }
            M = nx.compose(M, nx.relabel_nodes(K5,label_dict))
            # Maze cell and neighbours
            K5_ij = C + str(i)
            K5_E  = ascii_uppercase[j] + str(i)
            K5_S  = C + str(i+1)
            # Connect E to W
            if j < n:
                M.add_edge(K5_ij + '.E', K5_E + '.W')
            # Connect S to N
            if i < m:
                M.add_edge(K5_ij + '.S', K5_S + '.N')


            # Node locatons (x,y)
            for c in cardinal:
                #Name convention start at 1, but locations start at 0
                x_off = i - 1
                y_off = j - 1

                node = K5_ij + '.' + c
                loc_dict[node] = ( y_off*n + c_loc[c][0] , x_off*m + c_loc[c][1] )

                if 'a' in c:
                    continue

                # Pins locations
                pin = '$' + node
                M.add_edge(pin, node)
                pin_x = y_off*n + pin_loc[c][0]
                pin_y = x_off*m + pin_loc[c][1]
                loc_dict[pin] = ( pin_x, pin_y )

    return M, loc_dict

if __name__ == '__main__':

    n=3
    m=3

    M, loc_dict = maze(m,n)

    plt.clf()
    plt.gca().invert_yaxis()
    nx.draw(M, pos=loc_dict, with_labels=True, node_size=20, font_size=8)
    plt.savefig('test.svg')
    plt.show()

    file = open('maze%sx%s.xy' % (n,m), 'w')
    for node, loc in loc_dict.items():
        x,y = loc
        file.write('%s %s %s\n' % (node, x, y))
    file.close()
