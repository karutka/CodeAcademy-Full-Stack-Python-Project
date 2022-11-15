Final Full Stack Python Project

## Installation

#### Create virtual environment in project's root directory:

- ##### For Linux / Mac:

  ```Shell
  python3 -m venv venv
  ```

- ##### For Windows:
  ```Shell
  python -m venv venv
  ```

#### Activate the virtual environment:

- ##### For Linux / Mac:

  ```Shell
  source venv/bin/activate
  ```

- ##### For Windows:
  ```Shell
  source venv/Scripts/activate
  ```

#### Install the required packages:

```Shell
pip install -r requirements.txt
```

## Running

##### [1] Set the environment variables:

```Shell
export FLASK_APP=app
export FLASK_DEBUG=1
```

##### [2] Run the development server:
```Shell
flask run
```
##### Alternative without setting environment variables:
```Shell
flask --app app --debug run
```

## Software dependencies

[Flask](https://flask.palletsprojects.com) - a web development framework that is known for its lightweight and modular design. It has many out-of-the-box features and is easily adaptable to specific requirements.

[Jinja2](https://jinja.palletsprojects.com) - a fast, expressive, extensible templating engine. Special placeholders in the template allow writing code similar to Python syntax. Then the template is passed data to render the final document.

[SQLAlchemy](https://www.sqlalchemy.org) - the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.

[Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com) - an extension for Flask that adds support for SQLAlchemy to the app. It simplifies using SQLAlchemy with Flask by setting up common objects and patterns for using those objects, such as a session tied to each web request, models, and engines. This extension does not change how SQLAlchemy works or is used.

[Bootstrap Flask](https://bootstrap-flask.readthedocs.io) - a collection of Jinja macros for Bootstrap and Flask. It helps to render Flask-related data and objects to Bootstrap markup HTML more easily.

For the full list of software dependencies see [requirements.txt](requirements.txt).

## Latest releases

**v1.0.0** (2022-11-15)

## API references

None

Copyright (c) 2022 Kastė Rutkauskaitė