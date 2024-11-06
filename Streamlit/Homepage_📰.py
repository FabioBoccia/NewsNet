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
def get_cat_freq():
    cat_freq = get_categories_frequencies()
    categories = list(cat_freq.keys())
    categories_count = [cat_freq[cat] for cat in categories]
    cat_and_count = [(cat, count) for cat, count in zip(categories, categories_count)]
    cat_and_count.sort(key=lambda x: x[1])
    categories = [el[0] for el in cat_and_count]
    categories_count = [el[1] for el in cat_and_count]
    return pd.DataFrame({'Category': categories, 'Count': categories_count})

st.title('NewsNet Knowledge Graph via LLM :newspaper:')

st.text('''
        A knowledge graph is a structured framework that organizes information into entities and their relationships. 
        Imagine it as a vast network where each entity, such as a person, place, or concept, is a node, and the connections between them, representing how they are related,
        are edges.
        The aim of this project is to develop a system capable of transforming unstructured text into a structured knowledge graph representation.
        This system harnessed the capabilities of Named Entity Recognition (NER) and Relation Extraction (RE), empowered by Large Language Models (LLMs).
        Through the systematic processing of raw data extracted from news articles and the utilization of advanced AI techniques, the system identified, classified,
        and linked entities, ultimately constructing a comprehensive knowledge graph.
        By transforming raw text into a structured knowledge graph representation, we can uncover hidden connections and patterns.
        ''')

left_column1, right_column1 = st.columns(2)

cat_freq = get_cat_freq()

with left_column1:
    st.header('Stats')
    first_column, second_column = st.columns([0.3, 0.7])
    with first_column:
        number_of_relationships = get_number_of_relationships()
        number_of_nodes = get_number_of_nodes()
        st.metric('Number of relationships', number_of_relationships)
        st.metric('Number of nodes', number_of_nodes)
    with second_column:
        st.dataframe(cat_freq, hide_index=True, use_container_width=True)

with right_column1:
    st.header('Histogram of categories')
    fig = go.Figure(data=go.Bar(x=cat_freq['Category'], y=cat_freq['Count'], marker_color='#3357FF'),layout=dict(barcornerradius=15))
    st.plotly_chart(fig)

with st.sidebar:
    st.header('Settings')

    limit = st.slider('Choose the number of nodes to display', min_value=1, max_value=300, value=10)
    show_legend = st.checkbox('Show legend', value=True)
    spanning_tree_root = st.selectbox('Select the spanning tree root', ['GIORGIA MELONI', 'URSULA VON DER LEYEN', 'UNITED NATIONS', 'VLADIMIR PUTIN', 'EUROPEAN PARLIAMENT ELECTION'], index=0)

st.header('Spanning Tree')
st.text('''
        The following graph is a spanning tree starting from the root node selected in the setting. Due to graph size, at most 300 nodes can be displayed.
        Since the legend is fixed, it can be hidden. However hovering over the node, will diplay its category.
        ''')
graph = get_spanning_tree(name=spanning_tree_root, limit=limit)

graph = visualize_result(graph, show_legend=show_legend)

graph.save_graph('pyvis_graph.html')

HtmlFile = open('pyvis_graph.html', 'r', encoding='utf-8')

st.components.v1.html(HtmlFile.read(), height=610)