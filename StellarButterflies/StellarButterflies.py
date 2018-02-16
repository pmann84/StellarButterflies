import os
import sqlite3
import click
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from .data_parser import add_year
from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField

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

@app.route('/butterfly', methods=['GET', 'POST'])
def butterfly():
    form = DateRangePickerForm()
    db = get_db()
    if form.validate_on_submit():
        print('Displaying data for date range: [{} - {}]'.format(form.dateFrom.data, form.dateTo.data))
        return render_template('butterfly.html', entries = entries, form = form)
    #queryString = 'SELECT observed_datetime, latitude FROM sunspots WHERE observed_datetime > \"' + fromDateStr + '\" AND observed_datetime < \"' + toDateStr + '\";'
    queryString = 'SELECT observed_datetime, latitude FROM sunspots'
    cur = db.execute(queryString)
    entries = cur.fetchall()
    return render_template('butterfly.html', entries = entries, form = form)

############## TEMPORARY STUFF ##############
class DateRangePickerForm(FlaskForm):
    dateTo = DateField('Pick a Start Date', format="%d/%m/%Y")
    dateFrom = DateField('Pick an End Date', format="%d/%m/%Y")
    submit = SubmitField('Go')