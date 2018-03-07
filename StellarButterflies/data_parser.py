import os
import re
from datetime import datetime
import uuid
from pprint import pprint as pp

DATA_DIR = "data\\raw"

def add_years(db, start, end):
    for year in range(start, end+1):
        add_year(db, year)

def add_year(db, year):
    data_file_path = None
    # Get the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    current_data_dir = os.path.join(current_dir, DATA_DIR)
    print("Current Path: {0}".format(current_dir))
    print("Current Data Path: {0}".format(current_data_dir))
    # Loop over 
    print("Looking for year [{0}]...".format(year))
    for filename in os.listdir(current_data_dir):
        data_year = os.path.splitext(filename)[0]
        data_year = data_year.lstrip("g")
        if int(year) == int(data_year):
            data_file_path = os.path.join(DATA_DIR, filename)

    print("Attempting to parse data file for year [{0}: {1}]".format(year, data_file_path))

    if not os.path.exists(data_file_path):
        print("File [{0}] does not exist!".format(data_file_path))
        return

    # Read in data from file
    with open(data_file_path, "r") as f:
        data_from_file = f.read()
    # Iterate over the lines and store them as
    # dicts in the sunspot data list
    for sunspot in data_from_file.split("\n"):
        sd = parse_data_str(sunspot)
        if sd:
            # Add it to the data list
            populate_database_from_dict(db, sd)
    db.commit()
    print("Year [{0}] successfully inserted!".format(year))

def parse_data_str(data):
    sunspot_dict = None
    if data:
        # Store the year for later use
        observed_year = int(data[0:4])  # 0-3
        observed_month = int(data[4:6])  # 4-5
        observed_day = int(data[6:8])  # 6-7
        observed_time = float(data[8:12])  # 8-11
        grp_num_data = data[12:20]
        if re.match("[ ]*[a-zA-Z0-9]+", grp_num_data):
            greenwich_spot_grp_num = int(data[12:20])  # 12-19
        else:
            greenwich_spot_grp_num = 0
        grp_suffix = str(data[20:22]).strip(" ") if observed_year < 1982 else str(data[20].strip(" "))  # 20-21 < 1982 or 20 > 1982
        grp_type = str(data[22:24]).strip(" ") if observed_year < 1982 else str(data[21:24].strip(" "))  # 22-23 < 1982 or 21-23 > 1982
        observed_umbral_area = int(data[26:29])  # 25-28
        observed_whole_spot_area = int(data[30:34])  # 30-33
        corr_umbral_area = int(data[35:39])  # 35-38
        corr_whole_spot_area = int(data[40:44])  # 40-43
        dist_from_centre = float(data[45:50])  # 45-49
        angle_from_helio_north = float(data[51:56])  # 51-55
        carrington_longitude = float(data[57:62])  # 57-61
        latitude = float(data[63:68])  # 63-67
        central_meridian_dist = float(data[69:])  # 69-73

        # Create the dictionary
        sunspot_dict = {"observed_year": observed_year,
                        "observed_month": observed_month,
                        "observed_day": observed_day,
                        "observed_time": observed_time,
                        "greenwich_spot_grp_num": greenwich_spot_grp_num,
                        "grp_suffix": grp_suffix,
                        "grp_type": grp_type,
                        "observed_umbral_area": observed_umbral_area,
                        "observed_whole_spot_area": observed_whole_spot_area,
                        "corr_umbral_area": corr_umbral_area,
                        "corr_whole_spot_area": corr_whole_spot_area,
                        "dist_from_centre": dist_from_centre,
                        "angle_from_helio_north": angle_from_helio_north,
                        "carrington_longitude": carrington_longitude,
                        "latitude": latitude,
                        "central_meridian_dist": central_meridian_dist}

        # Once we have the raw data, calculate a datetime string for the db
        observed_seconds_from_file = 86400.0*observed_time
        observed_hours_total = observed_seconds_from_file / 3600.0
        observed_hours = int(observed_hours_total)
        hours_remaining = observed_hours_total - observed_hours

        observed_minutes_total = hours_remaining * 60.0
        observed_minutes = int(observed_minutes_total)
        minutes_remaining = observed_minutes_total - observed_minutes

        observed_seconds_total = minutes_remaining * 60.0
        observed_seconds = int(observed_seconds_total)

        observed_datetime = datetime(observed_year, observed_month, observed_day, observed_hours, observed_minutes, observed_seconds)

        sunspot_dict["observed_datetime"] = observed_datetime.isoformat(" ")

        # Now create a uuid based on a hash of all the data
        uuid_gen_str = ""
        for name, val in sunspot_dict.items():
            if name not in ["observed_datetime"]:
                uuid_gen_str += "%s" % str(val)
        spot_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_gen_str))

        sunspot_dict["uuid"] = spot_uuid

    return sunspot_dict

def sunspot_entry_to_db_tuple(datadict):
    return (datadict["uuid"], 
            datadict["observed_datetime"], 
            datadict["greenwich_spot_grp_num"], 
            datadict["grp_suffix"], 
            datadict["grp_type"], 
            datadict["observed_umbral_area"], 
            datadict["observed_whole_spot_area"], 
            datadict["corr_umbral_area"], 
            datadict["corr_whole_spot_area"], 
            datadict["dist_from_centre"], 
            datadict["angle_from_helio_north"], 
            datadict["carrington_longitude"], 
            datadict["latitude"], 
            datadict["central_meridian_dist"], 
            datadict["observed_year"], 
            datadict["observed_month"], 
            datadict["observed_day"], 
            datadict["observed_time"])

def populate_database_from_dict(db, datadict):
    # Check if spot has been inserted
    already_exist_query = """
        SELECT * FROM sunspots WHERE uuid=?
    """
    results = db.execute(already_exist_query, (datadict["uuid"],))
    if results.rowcount > 0:
        print("Entry for sunspot [uuid: {0}] already exists.".format(datadict["uuid"]))
        return

    # Now insert into db
    sunspot_insert_statement = """
        INSERT INTO sunspots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    db.execute(sunspot_insert_statement, sunspot_entry_to_db_tuple(datadict))
    print("Inserted spot data [uuid: {0}, date: {1}, latitude {2}]".format(datadict["uuid"], datadict["observed_datetime"], datadict["latitude"]))

def get_sunspots_for_date_range(dateFrom, dateTo):
    return

def datetimestring_to_epoch_time(datetime_str):
    p = '%Y-%m-%d %H:%M:%S'
    epoch = datetime(1970, 1, 1)
    epoch_seconds = (datetime.strptime(datetime_str, p) - epoch).total_seconds()
    return epoch_seconds