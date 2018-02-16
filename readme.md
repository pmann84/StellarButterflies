# Stellar Butterflies Project
## Overview

This is a project that converts text based sunspot observations to a database representation so that they can be queried and displayed via a simple webpage. Then downloaded etc.

## Setting up from scratch

Recreate the python virtual environment
    pip install -r env_requirements.txt
Start the environment
    $ pyenv\Scripts\activate
Set the location of the app
    set FLASK_APP=StellarButterflies.py
    $ flask run
Then access the webpage from 
http://localhost:5000/

## Running App Locally (after setup)

For Windows start the virtual environment:
    $ pyenv\Scripts\activate
To run the server run
    $ set FLASK_APP=StellarButterflies.py
    $ flask run
    
Then access the webpage from 
    http://localhost:5000/butterfly

## Creating a new virtual environment

Create a python virtual environment and install flask
    python -m venv <env name>
Install any packages you need with the pip installer
    pip install <package>
e.g. Install Flask
    pip install flask
Start the environment
    $ pyenv\Scripts\activate

## Deactivating virtual environment
    $ pyenv\Scripts\deactivate