import pandas as pd
from ..library import title_analysis_lib
from ..library import kmeans_lib
from ..library import dnn_lib

data = pd.read_csv("Healthcare.csv")

# different file for clusterings declared
kmeans_train=pd.read_csv('clusters/kmeans_clusters.csv', index_col=0)
agg_train=pd.read_csv('clusters/agg_clusters.csv', index_col=0)
gaussian_train=pd.read_csv('clusters/gaussian_clusters.csv', index_col=0)
minibatch_train=pd.read_csv('clusters/minibatch_clusters.csv', index_col=0)
spectral_train=pd.read_csv('clusters/spectral_clusters.csv', index_col=0)

kmeans_csv_name = "kmeans_healthcare_data.csv"
clusters_csv_name = "clusters_healthcare.csv"

title_analysis_lib.df_to_csv(data, kmeans_csv_name, only_title=True).head()

df_train = pd.read_csv("results/" + kmeans_csv_name)
cluster_test = kmeans_lib.get_optimal_clusters(df_train, "Title", 10)

# the algorithm uses a constant of 10 clusters
kmeans_lib.get_kmeans_clusters(10, cluster_test, clusters_csv_name, 4)

kmeans_train = pd.read_csv("results/" + clusters_csv_name, index_col=0)

# initialize dnn model settings
top_10 = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# run dnn model
dnn_model = dnn_lib.run_model(df_train, spectral_train, top_10, 'reports/spectral_dnn.txt')