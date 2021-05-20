## Step 2 - Climate App

#################################################
#import dependencies
#################################################

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

###########################################################################
# Database Setup
###########################################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

##########################################################################
# Flask Setup
##########################################################################
app = Flask(__name__)
	
##########################################################################
# Flask Routes
##########################################################################

##################################################
#Home page
##################################################
    #List all routes that are available.

@app.route("/")
def home():
    #List all available api routes
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"This route is to enter in a start date in the form of YYYY-MM-DD. Ex. /api/v1.0/2017-06-01: <br>"
        f"/api/v1.0/<start><br/>"
        f"This route is to enter a start then an end date in the form of YYYY-MM-DD. Ex. /api/v1.0/2017-06-01/2017-08-01:<br>"
        f"/api/v1.0/<start>/<end>"
    )

##################################################
# `/api/v1.0/precipitation`
##################################################
@app.route("/api/v1.0/precipitation")
def precip():
  #Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    session = Session(engine)
    year_prior = dt.date(2017,8,23) - dt.timedelta(weeks = 52)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date > year_prior).all()
    session.close()
    results_dict = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        results_dict.append(precip_dict)
  #Return the JSON representation of your dictionary.
    return jsonify(results_dict)

###################################################
#`/api/v1.0/stations`
###################################################
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results_station = session.query(measurement.station).distinct(measurement.station).all()
    session.close()
  #Return a JSON list of stations from the dataset.
    return jsonify(results_station)

##################################################
# `/api/v1.0/tobs`
##################################################
@app.route("/api/v1.0/tobs")
def temp():
    session = Session(engine)    
    #Query the dates and temperature observations of the most active station for the last year of data.
    year_prior_active= dt.date(2017,8,23) - dt.timedelta(weeks = 52)
    results_active = session.query(measurement.tobs).filter(measurement.date > year_prior_active).filter(measurement.station == 'USC00519281').all()
    session.close()
  #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(results_active)

################################################
#`/api/v1.0/<start>` and   `/api/v1.0/<start>/<end>`
################################################
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results_start = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    results_unravel = list(np.ravel(results_start))
    return jsonify(results_unravel)

@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    results_unravel = list(np.ravel(results))
    return jsonify(results_unravel)

if __name__ == '__main__':
    app.run(debug=True)