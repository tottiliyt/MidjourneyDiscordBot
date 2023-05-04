# MidjourneyAPI

#### 1. Setup Virtual Environment

We recommend creating a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html)
for running the API server.

```
python3 -m venv mjapi-env
```

For Windows:

```
.\mjapi-env\scripts\activate
```

For Linux

```
source mjapi-env/bin/activate
```

#### 2. Install Requirements

Then install the requirements (with your virtual environment activated)

```
pip install -r requirements.txt
```

After adding any new dependencies to the project, please update the requirements.txt file

```
pip freeze > requirements.txt 
```

#### 3. Running

Running Dev:

```
python3 bot.py
```