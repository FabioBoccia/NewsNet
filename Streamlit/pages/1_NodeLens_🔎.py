import streamlit as st
from neo4j_queries import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title='NewsGraph',
    page_icon=':newspaper:',
    layout='wide'
)

@st.cache_data()
def get_node_list():
    node_list = get_nodes_sorted()
    node_names = [el[0] for el in node_list]
    node_links = [el[1] for el in node_list]

    return pd.DataFrame({'Name': node_names, 'Number of relationships': node_links})

st.title('NodeLens 🔎')

st.text('''
        The aim of the following page is to visualize statistics and entities related to a specific node.
        ''')

# Nodes sorted by number of relationships
df_node = get_node_list()

left_column1, right_column1 = st.columns([0.3, 0.7])

with left_column1:
    st.header('Stats')
    st.dataframe(df_node, hide_index=True, use_container_width=True)

with right_column1:
    st.header('Top 50 nodes by number of relationships')
    fig = go.Figure(data=go.Bar(x=df_node['Name'][:50], y=df_node['Number of relationships'][:50], marker_color='#2ECC71'),layout=dict(barcornerradius=15))
    st.plotly_chart(fig)

with st.sidebar:
    st.header('Settings')

    limit = st.slider('Choose the number of nodes to display', min_value=1, max_value=300, value=10)
    show_legend = st.checkbox('Show legend', value=True)
    
    # Root of the spanning tree
    root = st.selectbox('Select the root', df_node['Name'], index=0)
    tree_or_neighbours = st.radio('Select spanning tree or neighbours visualization', ['Spanning Tree', 'Neighbours nodes'], index=0)
    
    # Max depth is 1 if Neighbours nodes is selected, (Spanning tree with depth 1 == Neighbours)
    max_depth = 1 if tree_or_neighbours == 'Neighbours nodes' else 10
    category = st.selectbox('Filter by category', entity_list, index=None)

# Getting spanning tree filtered by category
graph = get_spanning_tree(name=root, category=category, limit=limit, max_depth=max_depth)

st.header(f'{tree_or_neighbours} of {root}')

columns = st.columns(3)

with columns[0]:
    st.metric('Category', category)
with columns[1]:
    st.metric('Number of nodes', len(graph.nodes))
with columns[2]:
    st.metric('Number of relationships', len(graph.relationships))


graph = visualize_result(graph, show_legend=show_legend)

graph.save_graph('pyvis_graph.html')

HtmlFile = open('pyvis_graph.html', 'r', encoding='utf-8')

st.components.v1.html(HtmlFile.read(), height=610)

    
