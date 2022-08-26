# import modules
import pandas as pd
import numpy as np
import warnings
import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.callbacks import EarlyStopping
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import MinMaxScaler

# set up warning settings
warnings.filterwarnings("ignore")

# initialize keras
config = tf.compat.v1.ConfigProto(device_count={"GPU": 3})
sess = tf.compat.v1.Session(config=config)
keras.backend.set_session(sess)

early_stopping = EarlyStopping(
    monitor="binary_accuracy", patience=5, verbose=1, restore_best_weights=True
)

reduce_lr = keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss", factor=0.2, patience=5, min_lr=0.001
)
log_path = "text_file_name.txt"  # it will be created automatically


def process_data(df):
    df = df.fillna(0)
    df = df.reindex(np.random.permutation(df.index))
    return df


def combine_df(df, name, columns):
    for item in columns:
        df[item] = np.where(df[name] == item, 1, 0)
    df = df[[name] + columns]
    return df


def split_df_equal(df, value):
    df_split = np.array_split(df, value)
    return df_split


def split_df_frac(df):
    df_train = df.sample(frac=0.7, random_state=0)
    df_valid = df.drop(df_train.index)
    return df_train, df_valid


def get_datasets(df, drop_col, y_col):
    X = df.drop(drop_col, axis=1)
    y = df[y_col]
    return X, y


def dnn_model(nodes, reg, length, dropout, X_train, y_train, X_valid, y_valid, epochs, batch_size):
    model = keras.Sequential(
        [
            layers.Dense(
                nodes * 2,
                activation="relu",
                kernel_regularizer=keras.regularizers.l2(reg),
                input_shape=(length,),
            ),
            layers.Dropout(dropout),
            layers.Dense(
                nodes, activation="relu", kernel_regularizer=keras.regularizers.l2(reg)
            ),
            layers.Dropout(dropout),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics="binary_accuracy",
        run_eagerly=True,
    )
    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_valid, y_valid),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=early_stopping,
        verbose=1,
    )
    return model


def scale_col(data):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)
    data_scaled = pd.DataFrame(scaled, columns=data.columns)
    return data_scaled


def metrics_classification_report(X, y, model):
    T = 0.5
    y_pred = model.predict(X)
    y_pred_bool = y_pred >= T
    return classification_report(y, y_pred_bool)


def metrics_confusion_matrix(X, y, model):
    pred = (model.predict(X) > 0.5).astype(int)
    return confusion_matrix(y, pred)


def add_clusters_df(df, kmeans_df, cluster_cols):
    df["Cluster"] = kmeans_df["Cluster"]
    df_cluster = combine_df(df, "Cluster", cluster_cols)
    df = df.drop(["Cluster"], axis=1)
    df = process_data(df)
    return df


def get_vectors(df, drop_cols):
    data = get_datasets(df, drop_cols, "Sales")
    X = scale_col(data[0])
    y = data[1]
    return X, y


def get_reports(model, X_test, y_test, csv_name):
    classification_report=metrics_classification_report(X_test, y_test, model)
    confusion_matrix=metrics_confusion_matrix(X_test, y_test, model)
    name_file=csv_name+'.txt'
    file1=open(name_file, "w")
    file1.write(str(classification_report))
    file1.write(str(confusion_matrix))
    file1.close()
    print(classification_report)
    print(confusion_matrix)


def split_train_test(df):
    df_new=split_df_equal(df, 2)
    df_train=df_new[0]
    df_test=df_new[1]
    df=split_df_frac(df_train)
    df_train=df[0]
    df_valid=df[1]
    return df_train, df_valid, df_test


def run_model(df, kmeans_df, cluster_cols, csv_name, nodes=32, regularizer=0.001, dropout=0.2, epochs=1000, batch_size=30):
    df=add_clusters_df(df, kmeans_df, cluster_cols)
    datasets=split_train_test(df)
    df_train, df_valid, df_test=datasets[0], datasets[1], datasets[2]
    drop_cols=['Sales', 'Product_id']
    train=get_vectors(df_train, drop_cols)
    X_train, y_train=train[0], train[1]
    valid=get_vectors(df_train, drop_cols)
    X_valid, y_valid=valid[0], valid[1]
    test=get_vectors(df_test, drop_cols)
    X_test, y_test=test[0], test[1]
    len_train=len(X_train.columns)
    model=dnn_model(nodes, regularizer, len_train, dropout, X_train, y_train, X_valid, y_valid, 1000, 30)
    reports=get_reports(model, X_test, y_test, csv_name)
