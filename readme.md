# Stellar Butterflies Project
## Overview

This is a project that converts text based sunspot observations to a database representation so that they can be queried and displayed via a simple webpage. Note this used data collected from the Royal Observatory, Greenwich (https://solarscience.msfc.nasa.gov/greenwch.shtml), however the funding for the capturing of this data has terminated and doesn't seem to have been updated past 2016. As such the period of results only covers the years 1874 - 2016.

## Setting up from scratch

### Creating a new virtual environment

Create a python virtual environment and install flask

    python -m venv <env name>
	
Start the environment

    $ pyenv\Scripts\activate
	
Recreate the python virtual environment dependencies

    pip install -r env_requirements.txt

### Setup flask app

Set the location of the app

    set FLASK_APP=StellarButterflies.py

### Initialise database

Create a folder "database"

	cd stellarbutterflies
	mkdir database

Next create an empty version of the database using

    flask initdb
	
### Add data to the database

Once you have created an empty database you can then add data to it by running commmands like below

    flask addyear 2016
	
You can add all years of data to it

	flask addyears 1874 2016

### Running App Locally (after setup)

To run the server run

    $ set FLASK_APP=StellarButterflies.py
    $ flask run

Then access the webpage from 

    http://localhost:5000/

## Adding new Package Dependencies

Install any packages you need with the pip installer

    pip install <package>

then take a snapshot using

    pip freeze > env_requirements.txt

Then commit the changes in this file to the repository

## Deactivating virtual environment

    $ pyenv\Scripts\deactivate