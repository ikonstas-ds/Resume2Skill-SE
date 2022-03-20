import json
from py2neo import Graph
from tools.dotenv_read import read_dotenv
from injection.cypher_queries import injections, full_injection, esco_injection, skills_injection
from tqdm import tqdm
from math import ceil
import logging
import pandas as pd

"""
This script injects json files as created by extraction.extract in a Neo4J graph database.
Configuration of .env file is necessary, see README.md
"""

logging.basicConfig(
    filename='../injection.log',
    filemode='w+',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def inject_experience_education(graph: Graph, path_to_json: str, batch_size: int = 1000, injections = injections):
    """
    Script for injecting json in Neo4J. Requires a :class:`py2neo.Graph` object to operate. The json must contain a
    dictionary following precise specifications, such as the ones created by extraction.extract_sql.
    :param graph: a Graph object.
    :param path_to_json: Path to a json file containing the nodes data.
    :param batch_size: Number of statements to process at once, defaults to 1000.
    :return: None
    """
    with open(path_to_json, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

    try:

        for k in data.keys():

            logging.info(f'Injecting {k}...')
            statement = injections[k]
            node_data = data[k]

            n_batches = ceil(len(node_data) / batch_size)
            for b in tqdm(range(n_batches)):
                tx = graph.auto()
                tx.run(statement, {k: node_data[b * batch_size:(b + 1) * batch_size]})

    except Exception as exc:
        logging.error(exc)


def inject_profiles(graph: Graph, path_to_json: str, batch_size: int = 200):
    """
    Script for injecting json in Neo4J. Requires a :class:`py2neo.Graph` object to operate. The json must contain a
    dictionary following precise specifications, such as the ones created by analyse_sample.create_grouped_summary.
    :param graph: a Graph object.
    :param path_to_json: Path to a json file containing the nodes data.
    :param batch_size: Number of statements to process at once, defaults to 200.
    :return: None
    """
    with open(path_to_json, 'r', encoding='utf-8') as file:
        data: dict = json.load(file)

    try:

        n_batches = ceil(len(data) / batch_size)
        for b in tqdm(range(n_batches)):
            tx = graph.auto()
            tx.run(full_injection, {'data': data[b * batch_size:(b + 1) * batch_size]})

    except Exception as exc:
        logging.error(exc)


def convert_esco_to_json():
    """
    Script for converting ESCO csv file to json in order to be loaded into Neo4j.
    :param file_path: Path to json file for saving the transformed ESCO data
    :return None
    """
    
    esco_csv_path = 'ESCO/skills_en.csv'
    esco_json_path = 'ESCO/esco_skills.json'

    esco_data = pd.read_csv(esco_csv_path)
    esco_data['skill_id'] = esco_data.index.tolist()
    esco_data = esco_data[['conceptUri', 'reuseLevel', 'skillType', 'preferredLabel', 'description', 'skill_id']]
    esco_transformed = dict()
    esco_transformed['esco_skills'] = esco_data.to_dict('records')

    with open(esco_json_path, 'w+') as f:
                json.dump(esco_transformed, f)


def convert_esco_occupations_to_json():
    """
    Script for converting ESCO csv file to json in order to be loaded into Neo4j.
    :param file_path: Path to json file for saving the transformed ESCO data
    :return None
    """
    
    esco_csv_path = 'ESCO/occupations_en.csv'
    esco_json_path = 'ESCO/occupations.json'

    esco_data = pd.read_csv(esco_csv_path)
    esco_data['occupation_id'] = esco_data.index.tolist()
    esco_data = esco_data[['conceptUri', 'preferredLabel', 'description', 'occupation_id', 'iscoGroup']]
    esco_transformed = dict()
    esco_transformed['esco_occupations'] = esco_data.to_dict('records')

    with open(esco_json_path, 'w+') as f:
                json.dump(esco_transformed, f)
    

def convert_esco_rels_to_json():
    esco_rel = pd.read_csv('ESCO/occupations to skills.csv')
    esco_rel.columns = ['occupationURI', 'skillURI']

    esco_transformed = dict()
    esco_transformed['occupations_skills'] = esco_rel.to_dict('records')

    injection_esco_file = 'ESCO/esco_rels.json'
    with open(injection_esco_file, 'w+') as f:
                json.dump(esco_transformed, f)


def combine_esco():
    injection_occ_file = 'ESCO/esco_occupations.json'
    with open(injection_occ_file, 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
    
    injection_skill_file = 'ESCO/esco_skills.json'
    with open(injection_skill_file, 'r', encoding='utf-8') as file:
            skill_data: dict = json.load(file)
    
    injection_rel_file = 'ESCO/esco_rels.json'
    with open(injection_rel_file, 'r', encoding='utf-8') as file:
            rel_data: dict = json.load(file)
    
    skill_data['esco_occupations'] = data['esco_occupations']
    skill_data['occupations_skills'] = rel_data['occupations_skills']

    injection_esco_file = 'ESCO/occupations_skills.json'
    with open(injection_esco_file, 'w+') as f:
                json.dump(skill_data, f)



def inject_esco_occupations_skills():
    g = Graph(**read_dotenv('neo_'))
    file_path = read_dotenv('injection_')['esco_occupations_skills_file']
    inject_experience_education(g, file_path, injections=esco_injection)
    print('ESCO occupations and skills injection is completed')  


# def inject_esco_rels():
#     g = Graph(**read_dotenv('neo_'))
#     file_path = read_dotenv('injection_')['esco_rels_file']
#     inject_experience_education(g, file_path, injections=esco_rel_injections)
#     print('ESCO occupations and skills relationships injection is completed') 


def inject_profile_skills():
    g = Graph(**read_dotenv('neo_'))
    file_path = read_dotenv('injection_')['skills_file']
    inject_experience_education(g, file_path, injections=skills_injection, batch_size=5000)
    print('Profile skills injection is completed')



if __name__ == '__main__':
    print('Start injection')
    inject_esco_occupations_skills()

    g = Graph(**read_dotenv('neo_'))
    file_path = read_dotenv('injection_')['file']
    inject_experience_education(g, file_path)
    print('Injection is completed')

    inject_profile_skills()

