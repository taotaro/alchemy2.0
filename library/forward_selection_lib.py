import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mlxtend.feature_selection import SequentialFeatureSelector as sfs
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import os

def sort_features_based_on_relevance(data, target, significance_level=0.05):
    initial_features=data.columns.tolist()
    best_features=[]
    while(len(initial_features)>0):
        remaining_features=list(set(initial_features)-set(best_features))
        new_pval=pd.Series(index=remaining_features, dtype='float64')
        for new_column in remaining_features:
            model=sm.OLS(target, sm.add_constant(data[best_features+[new_column]])).fit()
            new_pval[new_column]=model.pvalues[new_column]
        min_p_value=new_pval.min()
        if(min_p_value<significance_level):
            best_features.append(new_pval.idxmin())
        else:
            break
    return best_features

def forward_selection(data, name='test', folder='test'):
    #product_id not relevant in forward selection
    if 'Product_id' in data.columns:
        data=data.drop('Product_id', axis=1)
    X=data.drop('Sales',axis=1)
    y=data['Sales']
    ordered_features=sort_features_based_on_relevance(X, y)
    file_path=os.path.join(folder, name+'.txt')
    with open(file_path, 'w') as fp:
        fp.write('\n'.join(str(item) for item in ordered_features))
        fp.close()

