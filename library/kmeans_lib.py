# import modules
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import warnings

# set up warning settings
warnings.filterwarnings("ignore")

def process_data(df, column):
    X = df[column]
    X.dropna(inplace=True)
    X = X.sample(frac=1)
    return X


def vectorize(X, vectorizer):
    X_vc = vectorizer.fit_transform(X)
    return X_vc


# give optimal number of clusters
def elbow_method(k_clusters, X, max_iter, n_init):
    score = []
    for i in range(1, k_clusters + 1):
        kmeans = KMeans(
            n_clusters=i,
            init="k-means++",
            max_iter=max_iter,
            n_init=n_init,
            random_state=0,
        )
        kmeans.fit(X)
        score.append(kmeans.inertia_)

    # set plot graph labels
    plt.plot(range(1, k_clusters + 1), score)
    plt.title("The Elbow Method")
    plt.xlabel("Number of clusters")
    plt.ylabel("Score")
    plt.savefig("elbow.png")
    plt.show()


def kmeans_clustering(k_clusters, n_init, max_iter, tol, X_vc, X):
    model = KMeans(
        n_clusters=k_clusters,
        init="k-means++",
        n_init=n_init,
        max_iter=max_iter,
        tol=tol,
        random_state=0,
    )
    model.fit(X_vc)
    cluster = model.predict(X_vc)
    data = pd.DataFrame({"Title": X})
    data["Cluster"] = cluster
    return data


def get_top_features_cluster(vectorizer, prediction, tf_idf_array, n_feats):
    labels = np.unique(prediction)
    dfs = []
    for label in labels:
        id_temp = np.where(prediction == label)
        x_means = np.mean(tf_idf_array[id_temp], axis=0)
        sorted_means = np.argsort(x_means)[::-1][:n_feats]
        features = vectorizer.get_feature_names()
        best_features = [(features[i], x_means[i]) for i in sorted_means]
        df = pd.DataFrame(best_features, columns=["features", "score"])
        dfs.append(df)
    return dfs


def plot_words(dfs, n_feats):
    for i in range(len(dfs)):
        plt.figure(figsize=(8, 2))
        plt.title(
            ("Most Common Words in Cluster {}".format(i)),
            fontsize=10,
            fontweight="bold",
        )
        sns.barplot(x="score", y="features", orient="h", data=dfs[i][:n_feats])


def get_optimal_clusters(df, col_name, k_clusters):
    X = process_data(df, col_name)
    vectorizer = TfidfVectorizer(
        sublinear_tf=True,
        min_df=10,
        norm="l2",
        ngram_range=(1, 2),
        stop_words="english",
    )
    X_vc = vectorize(X, vectorizer)
    elbow_graph = elbow_method(k_clusters, X_vc, 300, 5)

    return X, X_vc, vectorizer


def get_kmeans_clusters(k_clusters, dataset, csv_name, n_feats):
    X = dataset[0]
    X_vc = dataset[1]
    kmeans_data = kmeans_clustering(k_clusters, 10, 600, 0.000001, X_vc, X)
    kmeans_data.to_csv("results/" + csv_name)
    dfs_train = get_top_features_cluster(
        dataset[2], kmeans_data["Cluster"], X_vc.toarray(), n_feats
    )
    plot_words(dfs_train, n_feats)
    return kmeans_data

