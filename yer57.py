import numpy as np 
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import networkx as nx
from datetime import date, datetime, timedelta
from pandas.plotting import register_matplotlib_converters
import sys
import matplotlib.dates as mdates
import community
from nestedness_calculator import NestednessCalculator
from matplotlib.dates import DateFormatter

caso = sys.argv[1]
print caso

register_matplotlib_converters()

edge = pd.read_csv("input_edge.csv")
data = pd.read_csv("input_data.csv")
data['inhashtag'] = data['hashtag'].astype(int)

#print(data['inhashtag'])

edge["hour"] = 3600 * edge["hour"]
data["hour"] = 3600 * data["hour"]
#print(edge)

edge["human_hour"] = pd.to_datetime(edge["hour"],unit='s')
data["human_hour"] = pd.to_datetime(data["hour"],unit='s')
#print(edge)

#ini = edge["hour"].min()
#fin = edge["hour"].max()

if caso == '15m':                                    # change the date here
    ini = datetime(2011, 05, 14, 06, 00)
    fin = datetime(2011, 05, 16, 23, 00)
    y0 = 1750
    y1 = 12
    x1 = datetime(2011, 5, 15, 23, 0)
    xc = datetime(2011, 05, 15, 12, 0)

elif caso == 'noaltarifazo':    
    ini = datetime(2019, 01, 01, 06, 00)
    fin = datetime(2019, 01, 07, 23, 00)
    y0 = 1450
    y1 = 7.2
    x1 = datetime(2019, 1, 5, 0, 0)
    xc = datetime(2019, 1, 4, 3, 0)
    
elif caso == '9n':    
    ini = datetime(2019, 11, 8, 06, 00)
    fin = datetime(2019, 11, 10, 20, 00)
    y0 = 1500
    y1 = 7.7
    x1 = datetime(2019, 11, 9, 21, 0)
    x2 = datetime(2019, 11, 10, 21, 0)
    xc = datetime(2019, 11, 9, 3, 0)   
    
elif caso == 'charliehebdo':    
    ini = datetime(2015, 01, 10, 00, 00)
    fin = datetime(2015, 01, 12, 00, 00)
    y0 = 1500
    y1 = 7.7
    x1 = datetime(2015, 01, 11, 21, 0)
    x2 = datetime(2015, 01, 11, 21, 0)
    xc = datetime(2015, 01, 11, 00, 0)    
    
def datespan(startDate, endDate, delta=timedelta(hours=1)):
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta

fig, axs = plt.subplots(2)
for timestamp in datespan(ini,fin,delta=timedelta(hours=1)):
   average = 0
   average2 = 0
#   print timestamp
   short_edge = edge[edge['human_hour'] == timestamp] [['h1','h2','hour','weight']]
   short_data = data[data['human_hour'] == timestamp] [['user','hashtag','inhashtag','hour']] 
   short_edge = short_edge.reset_index(drop=True)
   short_data = short_data.reset_index(drop=True)
   nusers = short_data['user'].nunique()
   
#   print(short_data)
#   print(short_edge)
   G=nx.from_pandas_edgelist(short_edge,'h1','h2',edge_attr='weight')
   n = nx.number_connected_components(G)
   print n
   #   print('En',timestamp,'hay',G.number_of_nodes(),'nodos',',',G.number_of_edges(),'enlaces y',n,'componentes')
   ncompo=0
   if n>0 :
         Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
         component = G.subgraph(Gcc[0])
         part = community.best_partition(component,weight='weight')
         r=community.modularity(part,component)
         GG = nx.to_numpy_array(component,weight=None)
         nest = NestednessCalculator(GG).nodf(GG)
         axs[0].scatter(timestamp,nusers,s=10,zorder=2,c='black',edgecolors='grey',linewidths=0.2)
         axs[1].scatter(timestamp,r,s=10,zorder=2,c='blueviolet',edgecolors='grey',linewidths=0.2)
         axs[1].scatter(timestamp,nest,s=17,zorder=2,c='magenta',edgecolors='grey',linewidths=0.2)  
         users = []
         nn = component.number_of_nodes()
         path = nx.average_shortest_path_length(component) 
         average += nn
         ncompo+=1
#         print ("En componente numero",ncompo,'hay',component.number_of_nodes(),'nodos',)
         lista = component.nodes()
#         print(lista)
         usuarios = []
         for has in lista:
#           print int(has)
#           print (short_data.loc[short_data["inhashtag"] == int(has)] ) 
           finding = short_data['user'].loc[short_data["inhashtag"] == int(has)]
           for cada in finding:
              if cada not in usuarios:
                 usuarios.append(cada)
#           print (len(usuarios),'usuarios en elhashtag',int(has),'del componente numero',ncompo)
         for ca in usuarios:
            if ca not in users:
              users.append(ca)
#         print users     
         nu = len(users)
         axs[0].scatter(timestamp,nu,s=10,zorder=2,c='r',edgecolors='grey',linewidths=0.2)
#         axs[1].scatter(timestamp,path,s=10,c='b')
#         average2 += nu
#     average2 = average2 / n   
#     axs[0].scatter(timestamp,average2,s=10,c='magenta')      
#     average = average / n
#     print timestamp,average
#     axs[1].scatter(timestamp,average,s=10,c='b')
#     plt.title("In blue Average number of users in components, in red scatter number of users in components")
axs[0].set_xlim(ini,fin)
axs[1].set_xlim(ini,fin)
axs[1].set_ylim(0,1)
axs[0].scatter(timestamp,nu,s=10,c='r',edgecolors='grey',linewidths=0.2,zorder=2,label='N. of users in the giant component')
axs[1].scatter(timestamp,r,s=10,c='blueviolet',edgecolors='grey',linewidths=0.2,zorder=2,label="Modularity") 
axs[1].scatter(timestamp,nest,s=10,c='magenta',edgecolors='grey',linewidths=0.2,zorder=2,label="Nestedness") 
axs[0].scatter(timestamp,nusers,s=10,c='black',zorder=2,label='Number of users')
axs[0].legend(loc="upper left",prop={'size': 8})
axs[1].legend(loc="upper left",prop={'size': 8})
axs[0].axvspan(mdates.date2num(ini), mdates.date2num(xc), alpha=0.5, color='#00678a')
axs[1].axvspan(mdates.date2num(ini), mdates.date2num(xc), alpha=0.5, color='#00678a') 
axs[0].axvspan(mdates.date2num(xc), mdates.date2num(fin), alpha=0.5, color='#e6a176')
axs[1].axvspan(mdates.date2num(xc), mdates.date2num(fin), alpha=0.5, color='#e6a176')
axs[0].tick_params(axis="x", labelsize=6)
axs[1].tick_params(axis="x", labelsize=6)       
axs[0].xaxis.set_major_formatter(DateFormatter('%m-%d-%H'))
axs[1].xaxis.set_major_formatter(DateFormatter('%m-%d-%H')) 
axs[1].set_xlabel('Date in month-day-hour (year 2015)')        
plt.savefig('fig6_charlie.pdf')             
