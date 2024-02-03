# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Starter_Code\sqlalchemy-challenge\Surfsup\Resources\hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#  Start at the homepage.
#  List all the available routes.

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

#  Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary 
#  Uusing date as the key and prcp as the value.
#  Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Create a session from python to DB"""
    session = Session(engine)
    last_twelve_months = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    one_year_ago = dt.date(last_twelve_months.year, last_twelve_months.month, last_twelve_months.day)

    dp_scores = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.asc()).filter(Measurement.date>=one_year_ago).all()

    dp_dict = dict(dp_scores)

    print(f"Results for Precipitation - {dp_dict}")
    print("Out of Precipitation section.")
    return jsonify(dp_dict) 

#  Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["lat"] = lat
        station_dict["lon"] = lon
        station_dict["elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

#  Query the dates and temperature observations of the most-active station for the previous year of data.
#  Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    session.query( Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
     .filter(Measurement.date>='2016-08-23').all()

    tob_obs = []
    for date, tobs in queryresult:
         tobs_dict = {}
         tobs_dict["date"] = date
         tobs_dict["tobs"] = tobs
         tob_obs.append(tobs_dict)

    return jsonify(tob_obs)

#  Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#  For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#  For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.


@app.route("/api/v1.0/<start>")

def temp_start(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temp = []
    for min_temp, avg_temp, max_temp in result:
        temp_dict = {}
        temp_dict['Minimum Temperature'] = min_temp
        temp_dict['Average Temperature'] = avg_temp
        temp_dict['Maximum Temperature'] = max_temp
        temp.append(temp_dict)

    return jsonify(temp)


@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in result:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)