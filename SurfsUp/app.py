# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# Create our session (link) from Python to the DB
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def All():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
#route for precipitation information
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #query the last 12 months of data
    sel = [Measurement.date,
           func.sum(Measurement.prcp)]
    results = session.query(*sel).filter(func.strftime(Measurement.date) >= first_date).group_by(Measurement.date).\
            order_by(Measurement.date).all()

    #close session
    session.close()

    #create dictionary using dates as the key and prcp as the value
    precipitation_info = []

    for date, prcp in results:
        precipitation_dictionary = {}
        precipitation_dictionary["date"] = date
        precipitation_dictionary["prcp"] = prcp
        precipitation_info.append(precipitation_dictionary)
    
    return jsonify(precipitation_info)

#route for station
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query list of stations
    sel = [Measurement.station,func.count(Measurement.date)]
    most_active_stations = session.query(*sel).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.date).desc()).all()

    #close session
    session.close()

    # Create a dictionary of a list of stations
    all_stations = list(np.ravel(most_active_stations))

    #jsonify
    return jsonify(all_stations)

#route for tobs
@app.route("/api/v1.0/tobs")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temps of the most active stations for the previous year.
    sel = [Measurement.date, Measurement.tobs]
    station_temps_year = session.query(*sel).\
        filter(func.strftime(Measurement.date)>=first_date, Measurement.station == 'USC00519281').\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    #close session
    session.close()

    # return a json list of temp observations for the previous year
    temperature_observations = []
    date_of_observation = []

    for date, observation in station_temps_year:
        date_of_observation.append(date)
        temperature_observations.append(observation)

    big_list_dict = dict(zip(date_of_observation, temperature_observations))

    #jsonify
    return jsonify(big_list_dict)

#route for api start and api end
@app.route("/api/v1.0/start")
def first_date(start):
    session = Session(engine)

    #query for start date
    first_date_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= first_date).all()

    #close
    session.close()

    #list of value to append
    first_date_values = []
    for min, avg, max in start_date_values:
        first_date_values_dict = []
        first_date_values_dict["min"] = min
        first_date_values_dict["average"] = avg
        first_date_values_dict["max"] = max
        first_date_values.append(first_date_values_dict)

    #jsonify
    return jsonify(first_date_values)

#route for api start and api end
@app.route("/api/v1.0/start/end")
def first_end_date(start):
    session = Session(engine)

    #query for start date
    first_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= first).\
        filter(Measurement.date <= end).all()

    #close
    session.close()

    #list of value to append
    first_end_date_values = []
    for min, avg, max in first_end_date_values:
        first_end_date_values_dict = []
        first_end_date_values_dict["min"] = min
        first_end_date_values_dict["average"] = avg
        first_end_date_values_dict["max"] = max
        first_end_date_values.append(first_end_date_values_dict)

    #jsonify
    return jsonify(first_end_date_values)


if __name__ == '__main__':
    app.run(debug=True)
