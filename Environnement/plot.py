import os
import pandas as pd
try:
    import geopandas as gpd
except ImportError:
    pass
import numpy as np
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates
import seaborn as sns
from utils import regroupe_crop

#admin_level stands for administrative level : states, districts,...
def get_liste_admin_level_cluster(list_admin_level, df_admin_level_cluster, admin_level):
    liste_admin_level_cluster = []
    for i in range(len(list_admin_level)):
        l = []
        l.append(list_admin_level[i])
        #print(df_admin_level_cluster[df_admin_level_cluster[admin_level] == list_admin_level[i]]["cluster"].to_numpy())
        if len(df_admin_level_cluster[df_admin_level_cluster[admin_level] == list_admin_level[i]]["cluster"].to_numpy().astype(int)) > 0 :
            l.append(np.bincount(df_admin_level_cluster[df_admin_level_cluster[admin_level] == list_admin_level[i]]["cluster"].to_numpy().astype(int)).argmax())
        liste_admin_level_cluster.append(l)
    return liste_admin_level_cluster

# plot clusters on map of India
# typiquement admin_level = 'District', method_labels = kmeans.labels_ par exemple
# pathData renvoie vers les données brutes initiales
def plot_on_map(method_labels,pathData,admin_level):      
    labels_df = pd.DataFrame(method_labels, columns=['labels'])
    df_init = pd.read_csv(pathData)
    df_init['cluster'] = labels_df['labels'] 
    df_admin_level_cluster = df_init[[admin_level, 'cluster']]

    list_admin_level = pd.unique(df_admin_level_cluster[admin_level])

    list_admin_level_cluster = get_liste_admin_level_cluster(list_admin_level, df_admin_level_cluster, admin_level)
    df_reduced = pd.DataFrame(list_admin_level_cluster, columns=[admin_level, 'Clusters'])

    if admin_level == 'State' :
        map_path = "../../maps/ind_adm_shp/IND_adm2.shp"
        name = 'NAME_1'
    elif admin_level == 'District' :
        map_path = "../../maps/ind_adm_shp/IND_adm2.shp"
        name = 'NAME_2'
    else :
        map_path = "../../maps/ind_adm_shp/IND_adm3.shp"
        name = 'NAME_3'

    map_gdf = gpd.read_file(map_path)
    merged = map_gdf.set_index(name).join(df_reduced.set_index(admin_level))

    fig, ax = plt.subplots(1, figsize=(12, 12))
    ax.axis('off')
    ax.set_title('Clustering with k-means, averaged on each '+ admin_level,
                fontdict={'fontsize': '15', 'fontweight' : '3'})
    fig = merged.plot(column='Clusters', cmap='RdYlGn', linewidth=0.5, ax=ax, edgecolor='0.2', categorical=True, legend=True)
# %%


def get_liste_admin_level_crop(list_admin_level, list_crops, df_admin_level_crop, admin_level):
    list_admin_level_crop = []
    for i in range(len(list_admin_level)):
        l = []
        l.append(list_admin_level[i])
        #print(df_admin_level_crop[df_admin_level_crop[admin_level] == list_admin_level[i]]["Crop"].to_numpy())
        if len(df_admin_level_crop[df_admin_level_crop[admin_level] == list_admin_level[i]]["numCrop"].to_numpy().astype(int)) > 0 :
            max_crop_num = np.bincount(df_admin_level_crop[df_admin_level_crop[admin_level] == list_admin_level[i]]["numCrop"].to_numpy().astype(int)).argmax()
            max_crop = df_admin_level_crop.loc[df_admin_level_crop['numCrop'] == max_crop_num, 'Crop'].iloc[0]
            l.append(max_crop)
        list_admin_level_crop.append(l)
    return list_admin_level_crop

def plot_crops(pathData,admin_level):      
    df_init = pd.read_csv(pathData)
    df_admin_level_crop = regroupe_crop(df_init[[admin_level, 'Crop']])
    df_admin_level_crop['numCrop'] = pd.factorize(df_admin_level_crop['Crop'])[0]
    # print(df_admin_level_crop)
    list_admin_level = pd.unique(df_admin_level_crop[admin_level])
    list_crops = pd.unique(df_admin_level_crop['Crop'])

    list_admin_level_crop = get_liste_admin_level_crop(list_admin_level, list_crops, df_admin_level_crop, admin_level)
    df_reduced = pd.DataFrame(list_admin_level_crop, columns=[admin_level, 'Crop'])


    if admin_level == 'State' :
        map_path = "../../maps/gadm36_IND_shp/gadm36_IND_1.shp"
        name = 'NAME_1'
    elif admin_level == 'District' :
        map_path = "../../maps/ind_adm_shp/IND_adm2.shp"
        name = 'NAME_2'
    else :
        map_path = "../../maps/ind_adm_shp/IND_adm3.shp"
        name = 'NAME_3'

    map_gdf = gpd.read_file(map_path)
    merged = map_gdf.set_index(name).join(df_reduced.set_index(admin_level))

    fig, ax = plt.subplots(1, figsize=(12, 16))
    ax.axis('off')
    ax.set_title('Main crop in each '+ admin_level,
                fontdict={'fontsize': '15', 'fontweight' : '3'})
    fig = merged.plot(column='Crop', cmap='RdYlGn', linewidth=0.5, ax=ax, edgecolor='0.2', categorical=True, legend=True)

#%%

# il faut modifier un peu clean data pour que ce plot fonctionne
def get_liste_admin_level_yield(list_admin_level, df_admin_level_yield, admin_level, K):
    liste_admin_level_yield = []
    yields = []
    for i in range(len(list_admin_level)):
        l = []
        l.append(list_admin_level[i])
        #print(df_admin_level_yield[df_admin_level_yield[admin_level] == list_admin_level[i]]["2017 Yield"].to_numpy())
        if len(df_admin_level_yield[df_admin_level_yield[admin_level] == list_admin_level[i]]["2017 Yield"].to_numpy().astype(int)) > 0 :
            mean_yield = np.mean(df_admin_level_yield[df_admin_level_yield[admin_level] == list_admin_level[i]]["2017 Yield"].to_numpy().astype(float))
            yields.append(mean_yield)
            l.append(mean_yield)
        liste_admin_level_yield.append(l)
    yields_arr = np.array(yields)
    m = np.min(yields_arr)
    M = np.max(yields_arr)
    step = (M-m)/K
    for i in range(len(list_admin_level)):
        val = liste_admin_level_yield[i][1]
        value = m
        for j in range(K):
            if val >= (m + j*step) and val < (m + (j+1)*step) :
                value = m + (j+1/2)*step
        liste_admin_level_yield[i][1] = value
    return liste_admin_level_yield

def plot_yields(pathData,admin_level,K):      
    df_init = pd.read_csv(pathData)
    df_clean = add_Loss(clean_data(df_init))
    df_admin_level_yield = df_clean[[admin_level,'2017 Yield']]

    #m = df_admin_level_yield['2017 Yield'].min()
    #M = df_admin_level_yield['2017 Yield'].max()

    # print(df_admin_level_yield)
    list_admin_level = pd.unique(df_admin_level_yield[admin_level])

    list_admin_level_yield = get_liste_admin_level_yield(list_admin_level, df_admin_level_yield, admin_level, K)
    df_reduced = pd.DataFrame(list_admin_level_yield, columns=[admin_level, 'Yield'])
    print(df_reduced)

    if admin_level == 'State' :
        map_path = "../../maps/gadm36_IND_shp/gadm36_IND_1.shp"
        name = 'NAME_1'
    elif admin_level == 'District' :
        map_path = "../../maps/ind_adm_shp/IND_adm2.shp"
        name = 'NAME_2'
    else :
        map_path = "../../maps/ind_adm_shp/IND_adm3.shp"
        name = 'NAME_3'

    map_gdf = gpd.read_file(map_path)
    merged = map_gdf.set_index(name).join(df_reduced.set_index(admin_level))

    fig, ax = plt.subplots(1, figsize=(12, 12))
    ax.axis('off')
    ax.set_title('Average yield in each '+ admin_level,
                fontdict={'fontsize': '15', 'fontweight' : '3'})
    fig = merged.plot(column='Yield', cmap='RdYlGn', linewidth=0.5, ax=ax, edgecolor='0.2',legend=True)
    
    

palette = sns.color_palette("bright", 10)

def display_parallel_coordinates(df, num_clusters):
    '''Display a parallel coordinates plot for the clusters in df'''

    # Select data points for individual clusters
    cluster_points = []
    for i in range(num_clusters):
        cluster_points.append(df[df.cluster==i])
    
    # Create the plot
    fig = plt.figure(figsize=(12, 15))
    title = fig.suptitle("Parallel Coordinates Plot for the Clusters", fontsize=18)
    fig.subplots_adjust(top=0.95, wspace=0)

    # Display one plot for each cluster, with the lines for the main cluster appearing over the lines for the other clusters
    for i in range(num_clusters):    
        plt.subplot(num_clusters, 1, i+1)
        for j,c in enumerate(cluster_points): 
            if i!= j:
                pc = parallel_coordinates(c, 'cluster', color=[addAlpha(palette[j],0.2)])
        pc = parallel_coordinates(cluster_points[i], 'cluster', color=[addAlpha(palette[i],0.5)])

        # Stagger the axes
        ax=plt.gca()
        for tick in ax.xaxis.get_major_ticks()[1::2]:
            tick.set_pad(20)        


def display_parallel_coordinates_centroids(df, num_clusters):
    '''Display a parallel coordinates plot for the centroids in df'''

    # Create the plot
    fig = plt.figure(figsize=(12, 5))
    title = fig.suptitle("Parallel Coordinates plot for the Centroids", fontsize=18)
    fig.subplots_adjust(top=0.9, wspace=0)

    # Draw the chart
    parallel_coordinates(df, 'cluster', color=palette)

    # Stagger the axes
    ax=plt.gca()
    for tick in ax.xaxis.get_major_ticks()[1::2]:
        tick.set_pad(20)   