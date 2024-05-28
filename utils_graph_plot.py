
import numpy as np
import matplotlib.pyplot as plt

# Función genérica para crear una gráfica de barras dado unos ejes X e Y, los nombres de los ejes,
# la ruta de los archivos.
def plot_bar(x_axis, y_axis, name_x, name_y, name_plot, path, bin_log=True, alpha=0.7, figsize=(8,6)):
    
    plt.figure(figsize=figsize) 

    plt.bar(x_axis, y_axis, alpha=alpha)
    plt.xlabel(name_x)
    plt.ylabel(name_y)
    plt.title(name_plot)

    if bin_log:
        plt.xscale('log')  
        plt.yscale('log')  

    plt.savefig(path)
    plt.show()

# Funcion genérica que, dado una serie de puntos, crea un histograma de los mismos haciendo una
# distribución en num_bins (100 por defecto)
def plot_histogram(points, name_x, name_y, name_plot, path, bin_log=True, num_bins=100, min_bins=0.001, max_bins=1, figsize=(8,6)):
    
    plt.figure(figsize=figsize) 

    if bin_log:
        plt.xscale('log')  
        plt.yscale('log')         
        plt.hist(points, bins=np.logspace(np.log10(min_bins), np.log10(max_bins), num_bins))
    else:
        plt.hist(points, bins=num_bins)

    plt.xlabel(name_x)
    plt.ylabel(name_y)
    plt.title(name_plot)

    plt.savefig(path)
    plt.show()

# Función genérica para crear una gráfica de puntos dado unos arrays de ejes X e Y, los nombres de los ejes,
# la ruta de los archivos.
def plot_scatter(points_x, points_y, name_x, name_y, name_plot, path, bin_log=True, marker="x", dot_size=1, alpha=0.7, figsize=(8,6)):
    
    plt.figure(figsize=figsize) 
    
    if bin_log:
        plt.xscale('log')  
        plt.yscale('log')      

    plt.scatter(points_x, points_y, marker=marker, s=dot_size, alpha=alpha)

    plt.xlabel(name_x)
    plt.ylabel(name_y)
    plt.title(name_plot)

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
    plot_scatter(claves, valores, name_x="K_T", name_y="average c(K_T)", name_plot=name_plot, path=path, figsize=figsize)


# Dado un array con diccionarios con internal degrees como clave y la media de coeficiente de clusterización
# de los nodos que tienen dicho internal degree como valor, plotea el scatter con la clave en eje X y los valores en eje Y
# Plotea tantos tipos como elementoss haya en el array
def plot_avg_clust_by_norm_int_deg_fig2a(arr_norm_int_deg_fig2a, MANIFESTACION, hora, plots_folder):

    #print(len(arr_2a))
    arr_index = [5, 10, 20, 50, 100, 150, 200, 250]
    #arr_index = [5, 50, 100]
    markers = [".", "o", "v", "<", ">", "s", "p", "*"]
    # Crea el histograma
    plt.xscale('log')  
    plt.yscale('log')      
    for i, index in enumerate(arr_index):
        points_x = arr_norm_int_deg_fig2a[index].keys()
        points_y = arr_norm_int_deg_fig2a[index].values()
        plt.plot(points_x, points_y, alpha=1)
    
    plt.title(str(hora) + " (" + MANIFESTACION + ") - Fig. 2a")
    plt.legend(arr_index)
    plt.savefig(plots_folder + hora + "_Fig_2a.png")
    plt.show()


# Dado una arra con una serie de valores correspondiente al grado de los nodos normalizado
# por el número total de nodos, imprime el histograma (frecuencia) de estos valores
def plot_bar_degree_distribution(arr_norm_degrees, name_graph, plots_folder):
    
    plot_histogram(arr_norm_degrees, name_x="Degree", name_y="Frequency", name_plot="Degree of nodes", path=plots_folder + name_graph + ".png", bin_log=True)

# Dado un array con una serie de valores correspondiente al grado de los nodos normalizado
# por el número total de nodos, imprime el scatter con la distribucion cumulativa de estos
def plot_bar_degree_cummulative_distribution(arr_norm_degrees, name_graph, plots_folder):
    
    cum_freq = np.cumsum(arr_norm_degrees)
    cdf = cum_freq/cum_freq[-1]

    plot_bar(arr_norm_degrees, cdf, "Degree", "Cummlative frequency", "Degree of nodes", plots_folder + name_graph + "_cdf.png", bin_log=True)

# Dado un array con una serie de valores correspondiente al grado de los nodos normalizado
# por el número total de nodos, imprime el scatter con la distribucion complementaria cumulativa de estos
def plot_bar_degree_complementary_cummulative_distribution(arr_norm_degrees, name_graph, plots_folder):

    cum_freq = np.cumsum(arr_norm_degrees)
    cdf = cum_freq/cum_freq[-1]
    ccdf = 1 - cdf

    plot_bar(arr_norm_degrees, ccdf, "Degree", "Complementary Cummulative frequency", "Degree of nodes", plots_folder + name_graph + "_ccdf.png", bin_log=True)