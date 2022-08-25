import pandas as pd
from ..library import title_analysis_lib
from ..library import kmeans_lib
from ..library import dnn_lib

data = pd.read_csv("Healthcare.csv")

kmeans_csv_name = "kmeans_healthcare_data.csv"
clusters_csv_name = "clusters_healthcare.csv"

title_analysis_lib.df_to_csv(data, kmeans_csv_name, only_title=True).head()

df_train = pd.read_csv("results/" + kmeans_csv_name)
cluster_test = kmeans_lib.get_optimal_clusters(df_train, "Title", 10)

# the algorithm uses a constant of 10 clusters
kmeans_lib.get_kmeans_clusters(10, cluster_test, clusters_csv_name, 4)

df_train = pd.read_csv("healthcare_data.csv", index_col=0)
df_test = pd.read_csv("df_title_test.csv", index_col=0)

kmeans_train = pd.read_csv("results/" + clusters_csv_name, index_col=0)
kmeans_test = pd.read_csv("KMeans_test_data.csv", index_col=0)

# initialize dnn model settings
top_10 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
nodes = 32
regularizer = 0.01
dropout = 0.2
epochs = 1000
batch_size = 30

# run dnn model
dnn_model = dnn_lib.run_model(df_train, df_test, kmeans_train, kmeans_test, top_10,
      nodes, regularizer, dropout, epochs, batch_size, same_train_test=True)