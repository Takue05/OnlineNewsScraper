import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import os
import glob


def load_cluster_keywords():
    """Load the cluster keywords if available"""
    try:
        keywords = {}
        with open('data/cluster_keywords.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(': ', 1)
                if len(parts) == 2:
                    cluster = parts[0].replace('Cluster ', '')
                    keywords[int(cluster)] = parts[1]
        return keywords
    except:
        return {}


def run_app():
    st.set_page_config(
        page_title="Live News Clustering Dashboard",
        page_icon="📰",
        layout="wide"
    )

    st.title("📰 Live News Clustering Dashboard")

    # Check when data was last updated
    try:
        latest_file = 'data/clustered_news.csv'
        last_modified = datetime.fromtimestamp(os.path.getmtime(latest_file))
        st.sidebar.info(f"Last updated: {last_modified.strftime('%Y-%m-%d %H:%M')}")
    except:
        st.sidebar.warning("No data found. Please wait for the first update.")
        return

    # Load the clustered data
    try:
        df = pd.read_csv('data/clustered_news.csv')
    except:
        st.error("Data file not found. The system may still be collecting data.")
        return

    # Load cluster keywords
    cluster_keywords = load_cluster_keywords()

    # Sidebar filters
    st.sidebar.header("Filters")

    selected_newspaper = st.sidebar.multiselect(
        "Select Newspapers",
        options=df['newspaper'].unique(),
        default=df['newspaper'].unique()
    )

    selected_category = st.sidebar.multiselect(
        "Select Categories",
        options=df['category'].unique(),
        default=df['category'].unique()
    )

    # Filter data
    filtered_df = df[
        (df['newspaper'].isin(selected_newspaper)) &
        (df['category'].isin(selected_category))
        ]

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles", len(df))
    with col2:
        st.metric("Newspapers", len(df['newspaper'].unique()))
    with col3:
        st.metric("Categories", len(df['category'].unique()))
    with col4:
        st.metric("Clusters", len(df['cluster'].unique()))

    # Cluster visualization
    st.header("Cluster Visualization")

    fig = px.scatter(
        filtered_df,
        x='x',
        y='y',
        color='cluster',
        hover_data=['title', 'newspaper', 'category'],
        title="News Articles Clustered by Content Similarity",
        color_continuous_scale=px.colors.qualitative.Bold
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display category distribution
    st.header("News Category Distribution")
    cat_dist = px.histogram(
        filtered_df,
        x='category',
        color='newspaper',
        barmode='group',
        title="Articles per Category by Source"
    )
    st.plotly_chart(cat_dist, use_container_width=True)

    # Display clusters and their articles
    st.header("News Clusters")

    clusters = sorted(filtered_df['cluster'].unique())

    for cluster in clusters:
        cluster_df = filtered_df[filtered_df['cluster'] == cluster]

        # Get cluster keywords if available
        cluster_desc = f"Cluster {cluster}"
        if cluster in cluster_keywords:
            cluster_desc += f" - Keywords: {cluster_keywords[cluster]}"

        with st.expander(f"{cluster_desc} ({len(cluster_df)} articles)"):
            # Show dominant categories in this cluster
            st.subheader("Category Distribution")
            cat_counts = cluster_df['category'].value_counts().reset_index()
            cat_counts.columns = ['Category', 'Count']

            cat_chart = px.pie(
                cat_counts,
                values='Count',
                names='Category',
                title=f"Category Distribution in Cluster {cluster}"
            )
            st.plotly_chart(cat_chart, use_container_width=True)

            # Show articles table
            st.subheader("Articles in this cluster")

            # Create a DataFrame for display with hyperlinks
            display_df = cluster_df[['title', 'newspaper', 'category', 'url']].copy()

            # Format with clickable links
            st.write("Click on article titles to read the full story:")

            for i, row in display_df.iterrows():
                st.markdown(f"[{row['title']}]({row['url']}) - {row['newspaper']} ({row['category']})")


if __name__ == "__main__":
    run_app()