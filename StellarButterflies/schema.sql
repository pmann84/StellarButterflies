DROP TABLE IF EXISTS sunspots;
CREATE TABLE sunspots ( 
    uuid TEXT, 
    observed_datetime TEXT, 
    greenwich_spot_grp_num INTEGER, 
    grp_suffix TEXT, 
    grp_type TEXT, 
    observed_umbral_area INTEGER, 
    observed_whole_spot_area INTEGER, 
    corr_umbral_area INTEGER, 
    corr_whole_spot_area INTEGER, 
    dist_from_centre REAL, 
    angle_from_helio_north REAL, 
    carrington_longitude REAL, 
    latitude REAL, 
    central_meridian_dist REAL, 
    observed_year INTEGER, 
    observed_month INTEGER, 
    observed_day INTEGER, 
    observed_time REAL
);
