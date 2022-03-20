from py2neo import Graph
from tools.dotenv_read import read_dotenv
from indexation.schema import indexes
import logging
from tqdm import tqdm

"""
This script creates indexes on a Neo4J graph database. It needs only be run once against a given database.
Configuration of .env file is necessary, see README.md
"""

logging.basicConfig(
    filename='indexation.log',
    filemode='w+',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


if __name__ == '__main__':

    try:
        print("Start indexing")
        schema = Graph(**read_dotenv('neo_')).schema

        for label, index_list in tqdm(indexes.items()):
            graph_indexes = schema.get_indexes(label)
            for index in index_list:
                if index in graph_indexes:
                    logging.info(f'Index {index} on {label} already exists.')
                else:
                    logging.info(f'Index {index} is missing on {label}. Creating index.')
                    schema.create_index(label, *index)
                    logging.info(f'Index {index} created on {label}.')
        print('Finished indexing')

    except Exception as exc:
        logging.error(exc)
        exit(1)
