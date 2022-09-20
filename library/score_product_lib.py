def get_score(product, sorted_features):
    weight=100
    score=0
    for feature in sorted_features:
        if feature=='Cluster' or feature not in product.columns:
            continue
        weight/=2
        value=product[feature]
        score+=value*weight
    return score