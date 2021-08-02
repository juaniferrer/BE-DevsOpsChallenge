# DevsOps Code Challenge - Backend

This repository contains the Python backend for the asset/license management app, as well as the script for generating the Postgresql database to run the project locally.

## Getting Started

### Prerequisites

Things you need to install:

- [Node.js](https://nodejs.org/es/)
- [Python3](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- pip3 installed, as well as the following packages:
  - [Flask](https://pypi.org/project/Flask/)
  - [Flask-Cors](https://pypi.org/project/Flask-Cors/)
  - [Python-dotenv](https://pypi.org/project/python-dotenv/)
  - [Psycopg2](https://pypi.org/project/psycopg2/)
  - psycopg2-binary -> pip install psycopg2-binary

### Installing

First restore the DB:

```
psql -U your_user_name your_db_name < DBScript
```

After installing all the packages listed above on your venv, add a .env file with:

```
DATABASE="codeChallenge"
DATABASE_USERNAME="your_username"
DATABASE_PASSWORD="your_db_password"
```

then, run...
On BASH:

```
export FLASK_APP=index.py
export FLASK_ENV=development
```

or on CMD:

```
set FLASK_APP=index.py
set FLASK_ENV=development
```

and finally:

```
flask run
```
