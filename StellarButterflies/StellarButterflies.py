import os
import sqlite3
import click
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from .data_parser import add_year

# Create application
app = Flask(__name__)
# Bootstrap app
bootstrap = Bootstrap(app)

# Load config from this file - TODO: make this load from a .ini or .py file 
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database', 'stellar_butterflies.db'),
    SECRET_KEY='99A5D06D-F31F-4D61-B87F-6346682F8DBB',
    USERNAME='admin',
    PASSWORD='default'
))
#app.config.from_envvar('STELLAR_BUTTERFLIES_SETTINGS', silent=True)

############## DATABASE FUNCTIONALITY ##############
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is 
    none yet for the current application context"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

############## APP EXTENSIONS ##############
@app.cli.command('initdb')
def initdb_command():
    """Allow database creation via the commandline."""
    init_db()
    print('Initialized the database.')

@app.cli.command('addyear')
@click.argument('year')
def addyear_command(year):
    """Adds a raw data file for a year of observations to the database"""
    add_year(get_db(), year)
    print("Year [{0}] successfully inserted!".format(year))

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the 
    request"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

############## ROUTES ##############
@app.route('/')
@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/butterfly')
def butterfly():
    db = get_db()
    cur = db.execute('select observed_datetime, latitude from sunspots')
    entries = cur.fetchall()
    return render_template('butterfly.html', entries = entries)

