# Funciones necesarias par la carga del grafo y las operaciones necesarias para realizar el proceso de 
# renormalización
import networkx as nx


# Establece las paths a las carpeta de grafo para cargar y de plot para guardar el gráfico generado
def get_paths(MODE, MANIFESTACION, metric="correlation"):
    graphs_folder = "graphs/"
    plots_folder = "plots/" + metric + '/'

    modes_folder = "nodes_" + MODE + '/'
    graphs_folder = graphs_folder + modes_folder + MANIFESTACION + '/'
    plots_folder = plots_folder + modes_folder + MANIFESTACION + '/'
    return graphs_folder, plots_folder

# Cargamos el grafo seleccionado
def load_graph(name_graph, graphs_folder):
    full_graph_path = graphs_folder + name_graph + ".gexf"
    # Cargamos el grafo
    G = nx.read_gexf(full_graph_path)
    print("Cargado el grafo de la hora " + name_graph.split('_')[-1] + ', numero de nodos: ' + str(G.number_of_nodes()) + ', numero de aristas: ' + str(G.number_of_edges()))
    return G

# Función que añade los nodos a un grafo dado un treshold
def add_nodes_subgraph(G, treshold):
    F = nx.Graph()
    for node in G.nodes():
        # Comprobamos si el grado del nodo es mayor que el umbral
        if G.degree[node] > treshold:
            # Añadimos el nodo
            F.add_node(node)
    return F


# Función que dado un grafo G y un subgrafo suyo, F, solo con nodos, añade las aristas a F
# si dos nodos de F tienen arista en G
def add_edges_subgraph(G, F):
    for node in F.nodes():
        # Se itera sobre los vecinos en G de cada nodo y vemos si estan en F
        for neighbor in G.neighbors(node):
            if neighbor in F.nodes():
                # Se añade la arista si no existe ya
                if not neighbor in F.neighbors(node):
                    F.add_edge(node, neighbor)
    return F


# Añadimos la variable "internalDegree" a cada nodo dada la media de gradoscel subgrafo
# y el grado del propio nodo
def add_hidden_variable(F, avg_deg):
    dict_hidd_var = {}
    for node in F.nodes():
        dict_hidd_var[node] = F.degree[node] / avg_deg
    nx.set_node_attributes(F, dict_hidd_var, "internalDegree")


# Calcula la media de grados de un grafo
def calc_avg_degree(G):
    return sum(dict(G.degree).values())/G.number_of_nodes()


# Dado un grafo original y un umbral, aplica el proceso de treshold normalization del artículo 
# "Self-similarity of complex networks and hidden metric spaces" de Angeles et al.
def tresh_normalization(G, treshold):

    # Añadimos solamente los nodos que cumplan el umbral
    F = add_nodes_subgraph(G, treshold)
    
    # Si ya no hay nodos que cumplan el umbral, acabamos el proceso
    if F.number_of_nodes() == 0:
        return -1
    
    # Ahora añadimos las aristas de G de los nodos en el subgrafo F
    F = add_edges_subgraph(G, F)

    # Añadimos como variable oculta el grado entre la media del grafo a cada nodo
    avg_deg = calc_avg_degree(F)
    if avg_deg != 0:
        add_hidden_variable(F, avg_deg)
    else:
        return -1
    return F
