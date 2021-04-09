import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import numpy as np

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>-<end><br/>"
        f"/api/v1.0/<start>"
    )


@app.route("/api/v1.0/precipitation")
def names():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()

    session.close()
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Pull in only the last year worth of data
    singleYearData = session.query(Measurement.station,Measurement.date, Measurement.tobs).\
    filter(Measurement.date <= '2017-08-23').\
            filter(Measurement.date >= '2016-08-23').all()
    oneYrdf = pd.DataFrame(singleYearData)

    # filter down to just the station that was most active. 
    singleStationdf = oneYrdf.loc[oneYrdf['station']== 'USC00519397']
    data = singleStationdf['tobs']
    session.close()
    temps = list(np.ravel(data))

    return jsonify(temps)

@app.route("/api/v1.0/<start>-<end>")
def start_end(start, end):
  print(f"Enter both a start and end date. yyyy-mm-dd")
  session = Session(engine)
  custom_data = session.query(Measurement.tobs).\
  filter(Measurement.date <= start).\
      filter(Measurement.date >= end).all()
  min = custom_data.min()
  max = custom_data.max()
  average = custom_data.mean()
  try:
    return (
      f"The minimum temperature for your date range was: {min}.<br/>"
      f"The maximum temperature for your date range was: {max}.<br/>"
      f"The average temperature for your date range was: {average}."
    )
  except:
    return jsonify({"error": f"Date not found."}), 404

  session.close()
  
@app.route("/api/v1.0/<start>")
def start(start):
  print(f"Enter a start date. yyyy-mm-dd")
  session = Session(engine)
  custom_data = session.query(Measurement.tobs).\
  filter(Measurement.date <= start).\
      filter(Measurement.date >= '2016-08-23').all()
  min = custom_data.min()
  max = custom_data.max()
  average = custom_data.mean()
  try:
    return (
      f"The minimum temperature for your date range was: {min}.<br/>"
      f"The maximum temperature for your date range was: {max}.<br/>"
      f"The average temperature for your date range was: {average}."
    )
  except:
    return jsonify({"error": f"Date not found."}), 404
  session.close()
  


if __name__ == '__main__':
    app.run(debug=True)


