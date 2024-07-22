# Contiene las funciones que calculan métricas en grafos

import networkx as nx
from tqdm import tqdm
import numpy as np
import powerlaw
import pandas as pd
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


def get_exp(arr_points, name_graph, show_comparative=True, arr_kt=None, only_ntamas=False):

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
        if not only_ntamas:
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
            print("\n-----------------------------------\n")
            print("Resultados usando powerlaw (fit a powerlaw): ")
            print("alpha:", pl.alpha)
            print("sigma:", pl.sigma)
            print("x_min:", pl.xmin)
            print("(Kolgomorov Smirnov) D:", pl.KS())

            """tpl = results.truncated_power_law

            print("\nResultados usando powerlaw (fit a truncated_powerlaw): ")
            print("alpha:", tpl.alpha)
            print("lambda:", tpl.parameter2)
            print("x_min:", tpl.xmin)
            print("(Kolgomorov Smirnov) D:", tpl.KS())"""
        
        """print("\n-----------------------------------\n")
        print("Resultados usando plfit-main (ntamas):")
        result = subprocess.run(['./plfit-main/build/src/plfit', path, '-p', 'exact'], stdout=subprocess.PIPE) #, '-M' en el run para ver momentos centrales
        print(result.stdout.decode('utf-8'))
        output = result.stdout.decode('utf-8')
        # Define el patrón regex para extraer los valores
        pattern_a = r"alpha\s=\s+([\d.]+)"
        pattern_x = r"xmin\s=\s+([\d.]+)"
        pattern_L = r"L\s=\s+([\d.]+)"
        pattern_D = r"D\s=\s+([\d.]+)"
        pattern_p = r"p\s=\s+([\d.]+)"

        # Utiliza re.search para encontrar el patrón en el output
        match_a = re.search(pattern_a, output)
        match_x = re.search(pattern_x, output)
        match_L = re.search(pattern_L, output)
        match_D = re.search(pattern_D, output)
        match_p = re.search(pattern_p, output)
        print(match_a)"""
        """print(match_x)
        print(match_L)
        print(match_D)
        print(match_p)
        if match_a and match_x and match_L and match_D and match_p:
            alpha = float(match_a.group(1))
            xmin = float(match_x.group(1))
            L = float(match_L.group(1))
            D = float(match_D.group(1))
            p = float(match_p.group(1))

            print(f"alpha = {alpha}")
            print(f"xmin = {xmin}")
            print(f"L = {L}")
            print(f"D = {D}")
            print(f"p = {p}")
        else:
            print("No se encontraron coincidencias en el output.")"""
    return results

# Dado un array de arrays correpspondiente con los grados (o los grados normalizados) de un grafo por cada K_T
# y el numero de nodos del grafo, devuelve un array de tuplas de cada K_T. 
# cada tupla tiene como primer elementos los grados de los nodos (eje X) y las probabilidades de que 
# cada nodo tenga dicho grado (o grado normalizado) (eje Y)
def calc_pdf_points(arr_points, number_of_points):
    arr_pdf_points = []
    for points in arr_points:
        degrees, counts = np.unique(points, return_counts=True)
        probs = counts / number_of_points
        arr_pdf_points.append((degrees, probs))
    return arr_pdf_points

def calc_cdf_points(arr_pdf_points):
    arr_cdf_points = []
    for pdf_points in arr_pdf_points:
        cdf = np.cumsum(pdf_points[1])
        # No deberia ser necesario, pues las probs deberían sumar 1
        #cdf = cum_freq/cum_freq[-1]
        arr_cdf_points.append((pdf_points[0], cdf))
    return arr_cdf_points

def calc_ccdf_points(arr_cdf_points):
    arr_ccdf_points = []
    for deg_cum in arr_cdf_points:
        ccdf = 1 - deg_cum[1]
        # Quitamos el último punto pues, al ser escala logaritimica en los ejes y ser su probablidad
        # complementaria 0 o muy ceercana a 0, hace que el grafico quede deformado y no es util
        arr_ccdf_points.append((deg_cum[0][:-1], ccdf[:-1]))   
    return arr_ccdf_points

def check_number_hashtags_hour():
    file = "data/csv/9n/hashtag_usages_per_hour_9n_9ngranmarchaporlajusticia_weighted.txt"
    #file = "data/csv/nat/hashtag_usages_per_hour_noaltarifazo_ruidazonacional_weighted.txt"
    df = pd.read_csv(file, sep=' ')
    df_h = df["hour"].unique()
    my_dict ={}
    for hour in df_h:
        #my_dict[hour] = len(df[(df["hour"] == hour)]["hashtag"].unique())
        my_dict[hour] = len(df[(df["hour"] == hour)]["hashtag"])
        key_max =max(my_dict, key=my_dict.get)
    print("Hora con mayor número de hashtags:", key_max, "num hashtags:", my_dict[key_max] )
    plt.scatter(my_dict.keys(), my_dict.values())