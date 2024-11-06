import neo4j
import pyvis
from neo4j import GraphDatabase

URI = '<ADD YOUT TOKEN>'
AUTH = ('neo4j', '<ADD YOUR TOKEN>')

entity_list = [
'PERSON',
'ORGANIZATION',
'PARTY',
'LOCATION',
'DATE OR TIME PERIOD',
'MEASURE OR QUANTITY',
'PRODUCT OR SERVICE',
'EVENT',
'REGULATION',
'ECONOMIC SECTOR',
'NATURAL RESOURCE',
'TECHNOLOGY',
'INCIDENT'
]

hex_colors = [
    '#FF5733',  # PERSON
    '#33FF57',  # ORGANIZATION
    '#3357FF',  # PARTY
    '#F1C40F',  # LOCATION
    '#8E44AD',  # DATE OR TIME PERIOD
    '#16A085',  # MEASURE OR QUANTITY
    '#E74C3C',  # PRODUCT OR SERVICE
    '#3498DB',  # EVENT
    '#2ECC71',  # REGULATION
    '#9B59B6',  # ECONOMIC SECTOR
    '#1ABC9C',  # NATURAL RESOURCE
    '#E67E22',  # TECHNOLOGY
    '#D35400'   # INCIDENT
]

color_dict = dict(zip(entity_list, hex_colors))

def visualize_result(query_graph, show_legend=True):
    '''
        Visualize Neo4j Graph Object
    '''
    visual_graph = pyvis.network.Network(bgcolor='#0E1117', font_color='#FAFAFA')

    for node in query_graph.nodes:
        node_name = node.get('name')
        node_category = node.get('category')
        color = color_dict[node_category]
        visual_graph.add_node(node.element_id, node_name, color=color, group=node_category, title=node_category)

    for relationship in query_graph.relationships:
        visual_graph.add_edge(
            relationship.start_node.element_id,
            relationship.end_node.element_id,
            title=relationship.type
        )

    if show_legend:
        i = 0
        step = 50
        x = -700
        y = -300
        for cat in color_dict.keys():
            if i == 7:
                x += 170
                i = 0
            color = color_dict[cat]
            visual_graph.add_node(cat, size=10, shape='square', color=color, group=cat, x=x, y=y+i*step, fixed=True)
            i += 1        

    # visual_graph.show('network.html', notebook=False)
    
    return visual_graph

def get_number_of_nodes(category=None):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

        if category:
            records = driver.execute_query(
            'MATCH (n:Entity {category: $category}) RETURN count(n) as count',
            category=category,
            database_='neo4j',
            result_transformer_=neo4j.Result.single
            )
        else:
            records = driver.execute_query(
                    'MATCH (n) RETURN count(n) as count',
                    database_='neo4j',
                    result_transformer_=neo4j.Result.single
                    )

        count = records[0]

        return count

def get_number_of_relationships(name=None, direction='bidirectional'):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

        count = 0

        if name:
            if direction == 'to':
                records = driver.execute_query(
                    'MATCH ()-[r]->(e:Entity {name: $name}) RETURN count(r) as count',
                    name=name,
                    database_='neo4j',
                    result_transformer_=neo4j.Result.single
                    )
                count = records[0]
            elif direction == 'from':
                records = driver.execute_query(
                    'MATCH (e:Entity {name: $name})-[r]->() RETURN count(r) as count',
                    name=name,
                    database_='neo4j',
                    result_transformer_=neo4j.Result.single
                    )
                count = records[0]
            elif direction == 'bidirectional':
                records = driver.execute_query(
                    'MATCH (e:Entity {name: $name})-[r]-() RETURN count(r) as count',
                    name=name,
                    database_='neo4j',
                    result_transformer_=neo4j.Result.single
                    )
                count = records[0]
        else:
            records = driver.execute_query(
                    'MATCH ()-[r]->() RETURN count(r) as count',
                    database_='neo4j',
                    result_transformer_=neo4j.Result.single
                    )
            count = records[0]

        return count

def get_nodes_sorted():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

        records = driver.execute_query(
                '''
                MATCH (e:Entity)-[r]-()
                RETURN e, count(r) AS n
                ORDER BY n DESC;
                ''',
                database_='neo4j',
                result_transformer_=neo4j.Result.values
                )

        return [(record[0].get('name'), record[1])for record in records]

def get_categories_frequencies():
    categories_freq = {}

    for entity in entity_list:
        category_count = get_number_of_nodes(category=entity)
        categories_freq[entity] = category_count

    return categories_freq

def get_node_neighbours(name, limit=10):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

        records = driver.execute_query(
                f'MATCH p=(e:Entity {{name: $name}})-[]-() RETURN p LIMIT {limit};',
                name=name,
                database_='neo4j',
                result_transformer_=neo4j.Result.graph
                )

        return records

def get_spanning_tree(name, category=None, limit=10, max_depth=10):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

        if category:
            records = driver.execute_query(
                    f'''
                        MATCH (e: Entity {{name: $name}})
                        CALL apoc.path.spanningTree(e, {{
                            minLevel: 0,
                            maxLevel: {max_depth}
                        }})
                        YIELD path WHERE ALL(node in nodes(path) WHERE node.category = '{category}' OR node.name = '{name}')
                        RETURN path LIMIT {limit}
                    ''',
                    name=name,
                    category=category,
                    database_='neo4j',
                    result_transformer_=neo4j.Result.graph
                    )
        else:
            records = driver.execute_query(
                    f'''
                        MATCH (e: Entity {{name: $name}})
                        CALL apoc.path.spanningTree(e, {{
                            minLevel: 0,
                            maxLevel: {max_depth},
                            limit: {limit}
                        }})
                        YIELD path
                        RETURN path;
                    ''',
                    name=name,
                    database_='neo4j',
                    result_transformer_=neo4j.Result.graph
                    )

        return records

