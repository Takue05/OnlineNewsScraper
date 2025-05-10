import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from datetime import datetime


def perform_clustering(csv_path, n_clusters=4):
    """Perform clustering on the latest data"""
    print(f"[{datetime.now()}] Running clustering algorithm...")

    # Load data
    df = pd.read_csv(csv_path)

    # Text preprocessing and vectorization
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X = vectorizer.fit_transform(df['category'])

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X)

    # Add PCA for visualization
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X.toarray())
    df['x'] = pca_result[:, 0]
    df['y'] = pca_result[:, 1]

    # Find the most common terms in each cluster
    feature_names = vectorizer.get_feature_names_out()
    cluster_keywords = {}

    for i in range(n_clusters):
        # Get cluster center
        center = kmeans.cluster_centers_[i]
        # Get top terms
        top_indices = center.argsort()[-10:][::-1]
        top_terms = [feature_names[idx] for idx in top_indices]
        cluster_keywords[i] = ', '.join(top_terms)

    # Save as a dictionary for easy access
    with open('data/cluster_keywords.txt', 'w') as f:
        for cluster, keywords in cluster_keywords.items():
            f.write(f"Cluster {cluster}: {keywords}\n")

    # Save clustered data
    df.to_csv('data/clustered_news.csv', index=False)

    print(f"[{datetime.now()}] Clustering completed")
    return df