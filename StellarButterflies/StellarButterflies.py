import os
import sqlite3
import click
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from .data_parser import add_year
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.html5 import DateField
from datetime import datetime
from .sqlite_query_builder import SqliteSelectBuilder

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
    entries = []
    form = DateRangePickerForm()
    print(form.errors)
    if form.is_submitted():
        print("submitted")
    if form.validate():
        print("valid")
    print(form.errors)
    if form.validate_on_submit():
        print('Displaying data for date range: [{} - {}]'.format(form.dateFrom.data, form.dateTo.data))
        # Form the data query
        fromDate = form.dateFrom.data
        fromDateStr = fromDate.isoformat()
        fromDateStr += " 12:00:00"
        toDate = form.dateTo.data
        toDateStr = toDate.isoformat()
        toDateStr += " 12:00:00"

        qryBuilder = SqliteSelectBuilder()
        queryString = qryBuilder.sSelect("observed_datetime", "latitude") \
                                .sFrom("sunspots") \
                                .sWhere("observed_datetime") \
                                .sGt(fromDateStr) \
                                .sAnd("observed_datetime") \
                                .sLt(toDateStr) \
                                .endWhere() \
                                .endSelect()
        print(queryString)
        db = get_db()
        cur = db.execute(queryString)
        entries = cur.fetchall()

        # Sort the chart out
        chart = {"renderTo": "Butterfly", "type": 'scatter', "height": 350}
        title = {"text": 'Sunspot Appearance vs Latitude'}
        series = [{"name": 'Sunspot Latitudinal Position', "data": entries}]
        xAxis = {"title": {"text": 'Time'}, "gridLineWidth": 1}
        yAxis = {"title": {"text": 'Latitude'}, "min": 0, "max": 100}
        return render_template('butterfly.html', chartID='Sunspot_1', chart=chart, series=entries, title=title, xAxis=xAxis, yAxis=yAxis, form = form)
        #return render_template('butterfly.html', entries = entries, form = form)
    return render_template('butterfly.html', entries = entries, form = form)

############## TEMPORARY STUFF ##############
class DateRangePickerForm(FlaskForm):
    # TODO: add min max validators validators=[DateRange(min=datetime(), max=datetime(datetime.now())]
    dateFrom = DateField(format='%Y-%m-%d')
    dateTo = DateField(format='%Y-%m-%d')
    submit = SubmitField('Go')