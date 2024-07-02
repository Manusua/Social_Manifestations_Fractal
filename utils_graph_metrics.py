# Contiene las funciones que calculan métricas en grafos

import networkx as nx
from tqdm import tqdm
import numpy as np
import powerlaw
import subprocess
from utils_graph_generation import tresh_normalization

# Dado un grafo y un diccionario con la información clust[nodo] = coeficiente de clusterizacion del nodo
# devuelve un diccionario con internal degrees normalizados como clave y la media de coeficiente de clusterización
# de los nodos que tienen dicho internal degree como valor
# TODO, no deberia normalizar el diccioanrio al final para que sea la figura 2a????
def calc_fig2a_avg_clust_coef_by_normalized_internal_degree(G, clust):
    dict_hid_var_aux = {}
    dict_hid_var = {}
    # Creamos un diccionario con cada internal degree como clave y un array con los coeficientes
    # de clusterización de los nodos que tienen dicho internal degree
    for node in G.nodes():
        att = G.nodes[node]["internalDegree"]
        if att in dict_hid_var_aux.keys():
            np.append(dict_hid_var_aux[att], clust[node])
        else:
            dict_hid_var_aux[att] = np.array(clust[node])

    average_internal_degree = np.mean(np.array(list(dict_hid_var_aux.keys())))
    # Ordenamos el diccionario en función de la clave (internal degree) de menor a mayor
    dict_hid_var_aux_2 = {k/average_internal_degree: dict_hid_var_aux[k] for k in sorted(dict_hid_var_aux)}

    # Creamos un diccionario con internal degrees como clave y la media de coeficiente de clusterización
    # de los nodos que tienen dicho internal degree como valor
    for key in dict_hid_var_aux_2.keys():
        dict_hid_var[key] = np.average(dict_hid_var_aux_2[key])

    return dict_hid_var


# Crea MAX_UMBRAL sucesivos subgrafos tras aplicar iterativamene el proceso de normalización
# y calcula la distribución de grados y devuelve 
#   - dict_tres_avg_clust_fig2e: diccionario con tresholds como claves 
#       y media de coeficientes de clusterización del subgrafo generado con dicho treshold como valor
#   - arr_norm_int_deg_fig2a: array con diccionarios con internal degrees como clave y la media de coeficiente de clusterización
#       de los nodos que tienen dicho internal degree como valor. Cada índice se corresponde con el treshold empleado
#       para generar el subgrafo
def calc_clust(G, MAX_UMBRAL):
    dict_tres_avg_clust_fig2e = {}
    arr_norm_int_deg_fig2a = []
    for i in tqdm(range(MAX_UMBRAL)):
        treshold = i
        # Creamos el subgrafo basándonos en el treshold seleccionado
        F = tresh_normalization(G, treshold)
        if F == -1:
            # Caso de grafo vacío o grafo inconexo
            return dict_tres_avg_clust_fig2e, arr_norm_int_deg_fig2a
        #TODO para ejecutar sobre gráfica cugraph https://github.com/rapidsai/cugraph/tree/branch-24.06/python/nx-cugraph
        # diccionario[nodo] = coeficiente de clusterización del nodo https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.cluster.clustering.html#networkx.algorithms.cluster.clustering
        clust  = nx.clustering(F)
        avg_clust = np.mean(np.array(list(clust.values())))
        dict_tres_avg_clust_fig2e[treshold] = avg_clust

        arr_norm_int_deg_fig2a.append(calc_fig2a_avg_clust_coef_by_normalized_internal_degree(F, clust))

    return dict_tres_avg_clust_fig2e, arr_norm_int_deg_fig2a


# Función genérica que, dado un diccionario con valores numéricos, divide todos los elementos
# entre un valor, param_normalize
def normalize_dict(dict_dd, param_normalize):
    for key in dict_dd:
        dict_dd[key] /= param_normalize

# Dado un grafo G, devuelve un diccionario con los grados de del grafo como clave y
# el número de nodos con ese grado ordenado según el número de apariciones de menos a mayor
def calc_dist_degree(G):
    dict_dd = {}
    for _, deg in G.degree:
        if deg in dict_dd.keys():
            dict_dd[deg] +=1
        else:
            dict_dd[deg] = 1
    
    normalize_dict(dict_dd, G.number_of_nodes())
    return dict(sorted(dict_dd.items()))


def get_exp(arr_points, name_graph, show_comparative=True, arr_kt=None):
    meas_path = "measures/plfit_degrees/" 
    for index, points in enumerate(arr_points):
        # Ordenamos los puntos de menor a mayor quitando los 0s (dan error al calcular el exponente)
        points_aux = np.sort(points)
        points_aux = points_aux[points_aux != 0]
        points_aux = points_aux[::-1]

        # Escribimos los grados de los nodos en un archivo
        if arr_kt is None or len(arr_kt) <=1:
            path = meas_path + name_graph + '.txt'
        else:
            path = meas_path + name_graph + '_' + str(arr_kt[index]) + '.txt'

        with open(path, "w") as f:
            for point in points_aux:
                f.writelines(str(point) + '\n')

        results = powerlaw.Fit(points_aux)
        if show_comparative:
            nombres_dist = ["truncated_power_law", "power_law", "lognormal", "exponential", "stretched_exponential", "lognormal_positive"]
            for i in range(len(nombres_dist)):
                for j in range(len(nombres_dist)):
                    ind_j = j
                    """R is the loglikelihood ratio between the two candidate distributions. This number will be positive if the data is more likely in the first distribution, and negative if the data is more likely in the second distribution. The significance value for that direction is p."""
                    R, p = results.distribution_compare(nombres_dist[i], nombres_dist[ind_j], normalized_ratio=True, nested=False)
                    print("Comparando", nombres_dist[i], 'y', nombres_dist[ind_j], 'R:', R, "p:", p)

        pl = results.power_law

        print("Resultados usando powerlaw (fit a powerlaw): ")
        print("alpha:", pl.alpha)
        print("sigma:", pl.sigma)
        print("x_min:", pl.xmin)
        print("(Kolgomorov Smirnov) D:", pl.KS())

        tpl = results.truncated_power_law

        print("\nResultados usando powerlaw (fit a truncated_powerlaw): ")
        print("alpha:", tpl.alpha)
        print("lambda:", tpl.parameter2)
        print("x_min:", tpl.xmin)
        print("(Kolgomorov Smirnov) D:", tpl.KS())

        print("\nResultados usando plfit-main (ntamas):")
        result = subprocess.run(['./plfit-main/build/src/plfit', path], stdout=subprocess.PIPE) #, '-M' en el run para ver momentos centrales
        print(result.stdout.decode('utf-8'))