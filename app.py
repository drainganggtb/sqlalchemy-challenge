import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

from flask import Flask, jsonify

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn=engine.connect()

#reflect db into new model
Base = automap_base()
#reflect tables
Base.prepare(engine, reflect=True)

Measurement=Base.classes.measurement
Station=Base.classes.station

#Flask setup
app= Flask(__name__)

@app.route("/")
def index():
    """List all available api routes."""
    return (
        "<h1>Available Hawaii API Routes:</h1>"
        "<br/>"

        "/api/v1.0/precipitation<br/>"

        "On this page you will find the dates and precipitation observations "
        "in JSON representation.<br/><br/>"

        f"/api/v1.0/stations<br/>"
        f"On this page there exists a list of stations in JSON.<br/><br/>"

        f"/api/v1.0/tobs<br/>"
        f"This page houses a list of temperature observations (tobs) "
        "from the most active station<br/><br/>"

        f"/api/v1.0/temp/enter_start_date<br/>"
        f"This page has a list of 'TMIN'. 'TAVG', 'TMAX' for all dates greater than or equal to the queried start date, "
        "be sure to use the format YYYY-MM-DD.<br/><br/>"

        f"/api/v1.0/temp/enter_start_date/enter_end_date<br/>"
        f"On this page, you will find the 'TMIN', 'TAVG', 'TMAX' for dates between the start and end dates (YYYY-MM-DD)<br/>"
    )

@app.route("/api/v1.0/precipitation")
# on this page you will find a JSON representation of a dictionary of dates and precipitation in Hawaii
def prcp():
    precip = engine.execute("SELECT date, prcp FROM measurement ORDER BY date DESC").fetchall()
    pre_dict={}
    for x in precip:
        pre_dict[x[0]]=x[1]
    return jsonify(pre_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query = engine.execute("SELECT station, name, latitude, longitude, elevation FROM station").fetchall()
    session.close()

    stations_dict={}
    for x in stations_query:
        stations_dict[x[0]]={'name':x[1],'latitude':x[2], 'longitude':x[3], 'elevation':x[4]}
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
# query the dates and temperature observations of the most active station last year('USC00519281')
def temp():
    temp_query=engine.execute("SELECT date, tobs FROM measurement WHERE station = 'USC00519281' ORDER BY date DESC").fetchall()
    temp_dict={}
    for x in temp_query:
        temp_dict[x[0]]=x[1]
    return jsonify(temp_dict)

@app.route("/api/v1.0/temp/<start>")
def start_only(start):
    #go back to start date and get min/avg/max until last data point
    session=Session(engine)
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.date(2017,8,23)
    start_query=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(
        Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    start_dict = list(np.ravel(start_query))
    return jsonify(start_dict)


@app.route("/api/v1.0/temp/<start>/<end>")
def start_end(start, end):
    #go back to start date and get min/avg/max until the end point
    session=Session(engine)
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    se_query=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(
        Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    se_dict = list(np.ravel(se_query))
    return jsonify(se_dict)

if __name__ =='__main__':
    app.run(debug=True)

