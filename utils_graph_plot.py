
import numpy as np
import matplotlib.pyplot as plt

def get_all_markers():
    return [
    '.',  # point marker
    ',',  # pixel marker
    'o',  # circle marker
    'v',  # triangle_down marker
    '^',  # triangle_up marker
    '<',  # triangle_left marker
    '>',  # triangle_right marker
    '1',  # tri_down marker
    '2',  # tri_up marker
    '3',  # tri_left marker
    '4',  # tri_right marker
    's',  # square marker
    'p',  # pentagon marker
    '*',  # star marker
    'h',  # hexagon1 marker
    'H',  # hexagon2 marker
    '+',  # plus marker
    'x',  # x marker
    'D',  # diamond marker
    'd',  # thin_diamond marker
    '|',  # vline marker
    '_',  # hline marker
    'P',  # plus (filled) marker
    'X',  # x (filled) marker
    0,    # tickleft marker
    1,    # tickright marker
    2,    # tickup marker
    3,    # tickdown marker
    4,    # caretleft marker
    5,    # caretright marker
    6,    # caretup marker
    7    # caretdown marker
]

# Función genérica para crear una gráfica de barras dado unos ejes X e Y, los nombres de los ejes,
# la ruta de los archivos.
def plot_bar(x_axis, y_axis, name_x, name_y, name_plot, path, scale_log=True, alpha=0.7, figsize=(8,6)):
    
    plt.figure(figsize=figsize) 

    plt.bar(x_axis, y_axis, alpha=alpha)
    plt.xlabel(name_x)
    plt.ylabel(name_y)
    plt.title(name_plot)

    if scale_log:
        plt.xscale('log')  
        plt.yscale('log')  

    plt.savefig(path)
    plt.show()

# Funcion genérica que, dado un array con varios arrays de puntos, crea un histograma de los mismos haciendo una
# distribución en num_bins (100 por defecto)
# OJO, si quieremos plotear varios KT debemos pasar por parámetros un array de KTs
def plot_histogram(arr_points, name_x, name_y, name_plot, path, scale_log=True, num_bins=100, min_bins=0.001, max_bins=1, figsize=(8,6), arr_kt_plot=None, alpha=1):
    
    plt.figure(figsize=figsize) 
    if scale_log:
        plt.xscale('log')  
        plt.yscale('log')
    for index, points in enumerate(arr_points):
        if scale_log:
            if arr_kt_plot is None:         
                plt.hist(points, bins=np.logspace(np.log10(min_bins), np.log10(max_bins), num_bins), alpha=alpha)
            else:
                plt.hist(points, bins=np.logspace(np.log10(min_bins), np.log10(max_bins), num_bins), label="K_T = " + str(arr_kt_plot[index]), alpha=alpha)
        else:
            if arr_kt_plot is None:    
                plt.hist(points, bins=num_bins, alpha=alpha)
            else:
                plt.hist(points, bins=num_bins, label="K_T = " + str(arr_kt_plot[index]), alpha=alpha)

    plt.xlabel(name_x)
    plt.ylabel(name_y)
    plt.title(name_plot)

    if arr_kt_plot is not None:
        plt.legend()

    plt.savefig(path)
    plt.show()

# Función genérica para crear una gráfica de puntos dado un array de tuplas de arrays de ejes X e Y, los nombres de los ejes,
# la ruta de los archivos.
def plot_scatter(array_points, name_x, name_y, name_plot, path, scale_log=True, marker="x", dot_size=1, alpha=0.7, figsize=(8,6), arr_kt_plot=None):
    
    plt.figure(figsize=figsize) 
    
    if scale_log:
        plt.xscale('log')  
        plt.yscale('log')      

    for index, points in enumerate(array_points):
        if arr_kt_plot is None:         
            plt.scatter(points[0], points[1], marker=marker, s=dot_size, alpha=alpha)
        else:
            plt.scatter(points[0], points[1], marker=marker, s=dot_size, alpha=alpha, label="K_T = " + str(arr_kt_plot[index]))


    plt.xlabel(name_x)
    plt.ylabel(name_y)
    plt.title(name_plot)

    if arr_kt_plot is not None:
        plt.legend()

    plt.savefig(path)
    plt.show()
    

# Dado un diccionario, grafica un scatter plot con las claves en el eje X y los valores en el Y
def plot_clust_by_tres_fig2e(dict_tres, MANIFESTACION, hora, plots_folder):
    # Obtener las claves y los valores del diccionario
    claves = list(dict_tres.keys())
    valores = list(dict_tres.values())
    name_plot = str(hora) + " (" + MANIFESTACION + ") - Fig. 2e"
    path = plots_folder + hora + "_Fig_2e.png"
    figsize = (14,7)
    plot_scatter(claves, valores, name_x="K_T", name_y="average c(K_T)", name_plot=name_plot, path=path, figsize=figsize, scale_log=True)


# Dado un array con diccionarios con internal degrees como clave y la media de coeficiente de clusterización
# de los nodos que tienen dicho internal degree como valor, plotea el scatter con la clave en eje X y los valores en eje Y
# Plotea tantos tipos como elementos haya en arr_index(esos indices en concreto)
def plot_avg_clust_by_norm_int_deg_fig2a(arr_norm_int_deg_fig2a, MANIFESTACION, hora, plots_folder, arr_kt_plot=[5, 10, 20, 50, 100, 150, 200, 250]):
    if len(arr_kt_plot) > 32:
        print("Error, el número de elementos a graficar no puede ser mayor a 32")
        return
    #arr_index = [5, 50, 100]
    markers = get_all_markers()
    # Crea el histograma
    plt.xscale('log')  
    plt.yscale('log')      
    for i, index in enumerate(arr_kt_plot):
        points_x = arr_norm_int_deg_fig2a[index].keys()
        points_y = arr_norm_int_deg_fig2a[index].values()
        plt.plot(points_x, points_y, alpha=0.7)
        plt.scatter(points_x, points_y, alpha=0.7, s=4,marker=markers[i])

        
    
    plt.xlabel("Grado interno normalizado")
    plt.ylabel("coeficiente de clusterización medio\n de nodos con mismo internal degree normalizado")

    plt.title(str(hora) + " (" + MANIFESTACION + ") - Fig. 2a")
    plt.legend(list("K_T:" + str(kt) for kt in arr_kt_plot))
    plt.savefig(plots_folder + hora + "_Fig_2a.png")
    plt.show()


# Dado una array con una serie de valores correspondiente al grado de los nodos normalizado
# por el número total de nodos (cada elemento corresponde con una kt), imprime el histograma (frecuencia) de estos valores
def plot_degree_distribution(arr_norm_degrees, name_graph, plots_folder, name_x="Normalized degree", name_y="Frequency", name_plot="Degree of nodes", scale_log=True, num_bins=100, min_bins=0.001, max_bins=1, arr_kt_plot=None, alpha=1):
    
    plot_histogram(arr_norm_degrees, name_x=name_x, name_y=name_y, name_plot=name_plot, path=plots_folder + name_graph + ".png", scale_log=scale_log,num_bins=num_bins, min_bins=min_bins, max_bins=max_bins, arr_kt_plot=arr_kt_plot, alpha=alpha)

# Dado una array con una serie de valores correspondiente al grado de los nodos normalizado
# por el número total de nodos, imprime la funcion de distribucion de probabilidad de estos valores
def plot_degree_probability_distribution(arr_norm_degrees, number_of_nodes, name_graph, plots_folder, name_x="Normalized degree", name_y="Probability Distribution", name_plot="PDF - P(X=x)", scale_log=True, arr_kt_plot=None):
    arr_deg_prob = []
    for points in arr_norm_degrees:
        degrees, counts = np.unique(points, return_counts=True)
        probs = counts / number_of_nodes
        arr_deg_prob.append((degrees, probs))

    plot_scatter(arr_deg_prob, name_x=name_x, name_y=name_y, name_plot=name_plot, path=plots_folder + name_graph + "_cdf.png", scale_log=scale_log, arr_kt_plot=arr_kt_plot)
    return arr_deg_prob


# Dado un arra# por el número total de nodos, imprime el scatter cony con una serie de valores correspondiente al grado de los nodos normalizado
# la distribucion cumulativa de estos
def plot_degree_cummulative_distribution(arr_deg_prob, name_graph, plots_folder, name_x="Normalized degree", name_y="Cummulative Distribution", name_plot="CDF - P(X<x)", scale_log=True, arr_kt_plot=None):
    arr_deg_cum = []
    for deg_prob in arr_deg_prob:
        cum_freq = np.cumsum(deg_prob[1])
        cdf = cum_freq/cum_freq[-1]
        arr_deg_cum.append((deg_prob[0], cdf))

    plot_scatter(arr_deg_cum, name_x=name_x, name_y=name_y, name_plot=name_plot, path=plots_folder + name_graph + "_cdf.png", scale_log=scale_log, arr_kt_plot=arr_kt_plot)
    return arr_deg_cum

# Dado un array con una serie de valores correspondiente al grado de los nodos normalizado
# por el número total de nodos, imprime el scatter con la distribucion complementaria cumulativa de estos
def plot_degree_complementary_cummulative_distribution(arr_deg_cum, name_graph, plots_folder, name_x="Normalized degree", name_y="Complementary Cummulative Distribution", name_plot="CCDF - P(X>x)", scale_log=True, arr_kt_plot=None):
    arr_deg_comp_cum = []
    for deg_cum in arr_deg_cum:
        ccdf = 1 - deg_cum[1]
        arr_deg_comp_cum.append((deg_cum[0], ccdf))

    plot_scatter(arr_deg_comp_cum, name_x=name_x, name_y=name_y, name_plot=name_plot, path=plots_folder + name_graph + "_ccdf.png", scale_log=scale_log, arr_kt_plot=arr_kt_plot)
    
