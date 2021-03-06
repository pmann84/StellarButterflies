import os
import sqlite3
import click
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from .data_parser import add_year, add_years, datetimestring_to_epoch_time
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import SubmitField
from wtforms.fields.html5 import DateField
from datetime import datetime
from .database_queries import *
from pprint import pprint
import json

# Globals
IMAGE_FOLDER = os.path.join('static', 'images')

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
    PASSWORD='default',
    WTF_CSRF_ENABLED = False
))
# CSRF
csrf = CSRFProtect()
csrf.init_app(app)
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

@app.cli.command('addyears')
@click.argument('start')
@click.argument('end')
def addyears_command(start, end):
    """Adds a range of raw data files for a span of years of observations to the database"""
    add_years(get_db(), int(start), int(end))

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
    main_image = load_image_info("sun_main")
    print(main_image)
    return render_template('main.html', main_image=main_image)

@app.route('/plots', methods=['GET', 'POST'])
def plots():
    entries = []
    form = DateRangePickerForm()
    print(form.errors)
    if form.is_submitted():
        print("submitted")
    if form.validate():
        print("valid")
    if form.validate_on_submit():
        print('Displaying data for date range: [{} - {}]'.format(form.dateFrom.data, form.dateTo.data))
        # Form the data query
        fromDateStr, toDateStr = get_date_range_from_form(form)
        db = get_db()
        # Get the butterfly data
        entries = get_observed_sunspots_in_date_range_data_entries(db, fromDateStr, toDateStr)
        # Transform into something the chart can understand namely a list of lists of size 2
        data, xmin, xmax, ymin, ymax = prepare_data_for_colour_chart(entries)
        ymin = -90.0
        ymax = 90.0
        # Sort the chart out
        scatter_chart_info = { "chart_id": 'butterfly_scatter',
                               "chart_type" : 'scatter',
                               "chart_title": 'Sunspot Appearance vs Latitude',
                               "yaxis": {"title": {"text": 'Latitude'}, "min": ymin, "max": ymax} ,
                               "xaxis": {"title": {"text": 'Date'}, "min": xmin, "max": xmax},
                               "data": data }
        # Get the count data
        entries = get_sunspot_count_in_date_range_data_entries(db, fromDateStr, toDateStr)
        # Transform into something the chart can understand namely a list of lists of size 2
        count_data, count_xmin, count_xmax, count_ymin, count_ymax = prepare_data_for_chart(entries)
        # Sort the chart out
        count_chart_info = { "chart_id": 'count_chart',
                             "chart_type" : 'spline',
                             "chart_title": 'Number of Sunspots per day',
                             "yaxis": {"title": {"text": 'Number of Sunspots'}, "min": count_ymin, "max": count_ymax} ,
                             "xaxis": {"title": {"text": 'Date'}, "min": count_xmin, "max": count_xmax},
                             "data": count_data }
        print(form.errors)
        return render_template("plots.html", scatter_chart_info = scatter_chart_info, count_chart_info = count_chart_info, form = form)
    # No form execution
    print(form.errors)
    scatter_chart_info = {}
    count_chart_info = {}
    return render_template('plots.html', scatter_chart_info = scatter_chart_info, count_chart_info = count_chart_info, form = form)

############## TEMPORARY STUFF ##############

def load_image_info(name):
    this_image_folder = os.path.join(IMAGE_FOLDER, name)
    this_image_path = os.path.join(this_image_folder, '{}.jpg'.format(name))
    this_image_text_path = os.path.join(this_image_folder, '{}.json'.format(name))
    # Read the text from the file
    image_info = {}
    with open(this_image_text_path, "r") as f:
        image_info = json.load(f)
    image_info["path"] = this_image_path
    return image_info

def get_date_range_from_form(form):
    fromDate = form.dateFrom.data
    fromDateStr = fromDate.isoformat()
    fromDateStr += " 12:00:00"
    toDate = form.dateTo.data
    toDateStr = toDate.isoformat()
    toDateStr += " 12:00:00"
    return fromDateStr, toDateStr
    
def get_observed_sunspots_in_date_range_data_entries(db, fromDateStr, toDateStr):
    queryString = get_observed_sunspots_in_date_range_coloured_by_area(fromDateStr, toDateStr)
    print(queryString)
    cur = db.execute(queryString)
    entries = cur.fetchall()
    return entries

def get_sunspot_count_in_date_range_data_entries(db, fromDateStr, toDateStr):
    queryString = get_sunspot_count_in_date_range(fromDateStr, toDateStr)
    print(queryString)
    cur = db.execute(queryString)
    entries = cur.fetchall()
    return entries

def get_area_colour(area):
    if area < 100:
        return '#000000'
    elif area < 1000:
        return '#ffff00'
    elif area < 10000:
        return '#ff9900'
    else:
        return 'ff0000' 

def prepare_data_for_colour_chart(entries):
    # Transform into something the chart can understand namely a list of lists of size 2
    # Or it can be a list of dictionaries - [{x: 0.21, y:194.1, marker : {fillColor:'#000000'}}, ... ] so you can set individual point colours
    # Loop entries and get max and min of the extra column
    min_area = 0
    max_area = entries[0][2]
    for entry in entries:
        if entry[2] > max_area:
            xmax = entry[2]
        if entry[2] < min_area:
            xmin = entry[2]

    # Billionths of solar area so 0.00000001 of the solar area
    data = []
    xmin = datetimestring_to_epoch_time(entries[0][0])*1000
    xmax = 0
    ymin = entries[0][1]
    ymax = 0
     # Loop here and add an entry "marker" : {"fillColor": '#000000'} to the point dict
    for entry in entries:
        epoch_seconds = datetimestring_to_epoch_time(entry[0])*1000
        point_dict = {"x": epoch_seconds, "y": entry[1], "marker" : {"fillColor": get_area_colour(entry[2])}}
        data.append(point_dict)
        if epoch_seconds > xmax:
            xmax = epoch_seconds
        if epoch_seconds < xmin:
            xmin = epoch_seconds
        if entry[1] > ymax:
            ymax = entry[1]
        if entry[1] < ymin:
            ymin = entry[1]
    return data, xmin, xmax, ymin, ymax

def prepare_data_for_chart(entries):
    # Transform into something the chart can understand namely a list of lists of size 2
    data = []
    xmin = datetimestring_to_epoch_time(entries[0][0])*1000
    xmax = 0
    ymin = entries[0][1]
    ymax = 0
    for entry in entries:
        epoch_seconds = datetimestring_to_epoch_time(entry[0])*1000
        point_dict = [epoch_seconds, entry[1]]
        data.append(point_dict)
        if epoch_seconds > xmax:
            xmax = epoch_seconds
        if epoch_seconds < xmin:
            xmin = epoch_seconds
        if entry[1] > ymax:
            ymax = entry[1]
        if entry[1] < ymin:
            ymin = entry[1]
    return data, xmin, xmax, ymin, ymax

class DateRangePickerForm(FlaskForm):
    # TODO: add min max validators validators=[DateRange(min=datetime(), max=datetime(datetime.now())]
    dateFrom = DateField('Start Date', format='%Y-%m-%d')
    dateTo = DateField('End Date', format='%Y-%m-%d')