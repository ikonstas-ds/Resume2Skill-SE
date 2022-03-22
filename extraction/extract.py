from tools.dotenv_read import read_dotenv
# from tools.sql import QueryMaker
# from extraction.sql_queries import extractions, comp_questions
import json
import logging
from py2neo import Graph
import pandas as pd
from bs4 import BeautifulSoup
import unicodedata


logging.basicConfig(
    filename='extraction.log',
    filemode='w+',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_experience_descriptions(text_html):
    soup = BeautifulSoup(text_html, "html.parser")

    experiences_list = soup.find_all('span', class_='jobline')
    # print(experiences_list)
    if experiences_list:
        # print(True)
        experiences_list = [item.text.strip() for item in experiences_list ]
        experiences_list = [str(unicodedata.normalize("NFKD", item)) for item in experiences_list if len(item)>10]
    
    return experiences_list


def extract_experiences(df):
    df['experience_description'] = df['Resume_html'].apply(get_experience_descriptions)
    df = df.explode('experience_description')
    df.drop(['Resume_str', 'Resume_html'], axis=1, inplace=True)
    df.dropna(inplace=True)

    return df


if __name__ == '__main__':

    try:
        print('Start extraction')
        injection_file = read_dotenv('injection_')['file']

        df = pd.read_csv('data/Resume.csv')

        df = extract_experiences(df)

        data = {
            'experiences': df.to_dict(orient='records')
        }

        with open(injection_file, 'w+') as f:
            json.dump(data, f)
        
        print('json file loaded')

    except Exception as exc:
        logging.error(exc)
        exit(1)
