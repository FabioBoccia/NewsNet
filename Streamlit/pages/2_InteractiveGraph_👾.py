import pandas as pd
import streamlit as st
import pymongo
import sys
import plotly.express as px
 
from rebel import text_to_sentences, ner_re
from utils import *

sys.path.insert(1, '../')

st.set_page_config(
    page_title='NewsGraph',
    page_icon=':newspaper:',
    layout='wide'
)

mongo_uri = 'mongodb+srv://simdotolo:bdeluglio2024@cluster0.eajzwct.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

def get_mongo_client(mongo_uri):
    """Establish connection to the MongoDB."""
    try:
        client = pymongo.MongoClient(mongo_uri)
        print("Connection to MongoDB successful")
        return client
    except pymongo.errors.ConnectionFailure as e:
        print(f"Connection failed: {e}")
        return None

@st.cache_data
def get_data():
    mongo_client = get_mongo_client(mongo_uri)

    db = mongo_client["WorldNews"]
    collection = db["News"]

    cursor = collection.find()

    df = pd.DataFrame(list(cursor))
    df = df.drop(columns='_id')
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['Country'] = df['Country'].str.upper()

    return df

st.title('InteractiveGraph 👾')

st.text('The aim of the following page is to visualize the knowledge graph of a selected article.')

with st.spinner('Loading Data...'):
    df = get_data()

countries = df['Country'].unique()

with st.sidebar:
    st.header('Filters')
    selected_countries = st.multiselect('Select the countries', countries, placeholder='Select the countries',label_visibility='collapsed')

    all_countries = st.checkbox('Select all countries', value=True)

    if all_countries:
        selected_countries = countries

    start_date = st.date_input('Start date', value=pd.to_datetime(df['Date'].min()).date())
    end_date = st.date_input('End date', value=pd.to_datetime(df['Date'].max()).date())

    generate_graph = st.button('Generate Graph')

# Filtering data based on date and country selected in the sidebar
filtered_df = df[(df['Date'] >= start_date) & 
                 (df['Date'] <= end_date) &
                 (df['Country'].isin(selected_countries))]

# Adding checkbox column for article selection
filtered_df.insert(0, 'Show on Graph', False)

filtered_df = st.data_editor(
filtered_df,
column_config={'Show on Graph': st.column_config.CheckboxColumn(required=True)},
hide_index=True,
use_container_width=True
)

# Getting (Country: number of articles) for each country
df_location = filtered_df['Country'].value_counts().rename_axis('Country').reset_index(name='Count')

# Mapping country code to coordinates
df_location['coordinates'] = df_location['Country'].map(code_to_coords)

df_location['lat'] = [el[0] for el in df_location['coordinates'].to_list()]
df_location['lon'] = [el[1] for el in df_location['coordinates'].to_list()]

left, right = st.columns(2)

st.header('Map')

fig = px.scatter_mapbox(df_location, lat='lat', lon='lon', hover_name='Country', size='Count', hover_data='Count', color_discrete_sequence=['red'], zoom=2, height=500)
fig.update_layout(mapbox_style='open-street-map')
fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})
st.plotly_chart(fig)

selected_news = filtered_df.loc[filtered_df['Show on Graph'] == True]

selected_text = selected_news['Text']

print(len(text_to_sentences(selected_text)))

# Generating knowledge graph based on article selected above
if generate_graph:
    with st.spinner('Generating Knowledge Graph for selected articles...'):
        sentences =  text_to_sentences(selected_text)

        head_entities, tail_entities, relations = ner_re(sentences)

        st.subheader('Knowledge Graph')

        graph = visualize_result(head_entities, tail_entities, relations)

        graph.save_graph('pyvis_graph.html')

        HtmlFile = open('pyvis_graph.html', 'r', encoding='utf-8')

        st.components.v1.html(HtmlFile.read(), height=610)
