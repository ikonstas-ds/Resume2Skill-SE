from tools.dotenv_read import read_dotenv
from tools.sql import QueryMaker
from extraction.sql_queries import extractions, comp_questions
import json
import logging
from py2neo import Graph
import pandas as pd


"""
This scripts extracts the content from the MySql database and generates an injection file in json format.
Configuration of .env file is necessary, see README.md
"""

logging.basicConfig(
    filename='extraction.log',
    filemode='w+',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def extract_comp_questions(filepath='epso_data/talent_screener_questions.json', comp_questions=comp_questions):
    # Get columns "SHOW COLUMNS FROM TPL_D1_APP_FORM_TAL_SCREENER"
    query_maker = QueryMaker()
    res = query_maker.get_query(comp_questions, None)
    res.drop_duplicates(subset=['MAIN_TEXT', 'TAL_COMPET_ID'], keep='last', inplace=True)

    tal_comps = res.groupby('TAL_COMPET_ID')
    comp_questions = dict()
    for comp_id, item in tal_comps:
        comp_questions[str(comp_id)] = item['MAIN_TEXT'].tolist() 
    
    with open(filepath, 'w+') as f:
            json.dump(comp_questions, f)
    

def filter_epso_data():
    try:
        print('Start extraction')
        injection_file = read_dotenv('injection_')['file']

        with open(injection_file, 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
        
        df_exp = pd.DataFrame(data['experiences'])
        # Keep only English and with length more than 10
        df_exp = df_exp[df_exp['DUTIES_LG']=='en']
        df_exp = df_exp[df_exp['DUTIES'].apply(lambda x: False if len(x)<10 else True)]

        # Load education
        df_edu = pd.DataFrame(data['education'])

        # Keep only English follow up answers
        df_fup = pd.DataFrame(data['follow_up_answers'])
        df_fup = df_fup[df_fup['FOLLOW_UP_ANSWER_LG']=='en']

        data = {
            'experiences': df_exp.to_dict(orient='records'),
            'education': df_edu.to_dict(orient='records'),
            'follow_up_answers': df_fup.to_dict(orient='records')
        }

        with open(injection_file, 'w+') as f:
            json.dump(data, f)
        
        print('json file loaded')

    except Exception as exc:
        logging.error(exc)
        exit(1)

if __name__ == '__main__':

    try:
        print('Start extraction')
        injection_file = read_dotenv('injection_')['file']

        query_maker = QueryMaker()

        experiences = query_maker.get_query(extractions['experiences'], None)
        education = query_maker.get_query(extractions['education'], None)
        follow_up_answers = query_maker.get_query(extractions['follow_up_answers'], None)

        data = {
            'experiences': experiences.to_dict(orient='records'),
            'education': education.to_dict(orient='records'),
            'follow_up_answers': follow_up_answers.to_dict(orient='records')
        }

        with open(injection_file, 'w+') as f:
            json.dump(data, f)
        
        print('json file loaded')

    except Exception as exc:
        logging.error(exc)
        exit(1)
