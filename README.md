# Resume2Skill-SE

# EPSO DATA LOAD

A collection of scripts to extract data from the MySql database created for the EPSO Talent Search prototype and load it 
into a Neo4J graph database.

-----
### Environment and installation

- Runtime: Python 3.8

Install main libraries

```commandline
pip install -r requirements.txt
```
Install Faiss
```commandline
conda install -c pytorch faiss-cpu [or faiss-gpu]
```


-----
### Configuration

Most scripts require some configuration to run. Please create a ```.env``` file at the root of the project and include 
the following content (replace <placeholder_text> with adequate values):

##### For extraction.extract script:

It is recommended to create a folder epso_data for any personal data related to candidates
and a folder ESCO for the exports from ESCO linked open data.

```
injection_file=<path_to_injection_file_for_candidate_information.json>
injection_esco_occupations_skills_file=<path_to_occupations_skills_file.json>
injection_skills_file=<path_to_extracted_skills_of_profiles.json>
```

##### For injection.inject script:

```
injection_file=<path_to_injection_file>
neo_user=<neo4j_username>
neo_password=<neo4j_password>
neo_uri=<neo4j_uri>
```

##### For indexation.index script:

```
neo_user=<neo4j_username>
neo_password=<neo4j_password>
neo_uri=<neo4j_uri>
```



-----

### Usage:

**Before running any script, navigate to the root of the project and create and activate the environment.**

```commandline
conda create -n py_resume python=3.8
conda activate py_resume
```

```commandline
cd /path/to/project/root/folder
pip install -r requirements.txt
```


Install FAISS library to be used for skills extraction

```commandline
conda install -c pytorch faiss-gpu (or cpu for cpu only)
```

To extract data into a JSON file:

```commandline
python -m extraction.extract
```

To extract skills from the candidate profile descriptions into a JSON file:

```commandline
python -m skills_extract.esco_skills_match
```

To create the indexes necessary for injection in Neo4j (needs to be run once *before* injection, subsequent calls will do 
nothing):

```commandline
python -m indexation.index
```
To inject the data file in Neo4J:

```commandline
python -m injection.inject
```

To evaluate the results:

```commandline
python -m evaluation.evaluation_setup
```
