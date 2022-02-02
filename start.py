# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 20:34:36 2022
@author: Samuel Moser
"""
import sqlite3 # library for creating a db in memory hence 'lite'
import flask # webserver library
from flask import Flask, Response, json # more webserver things
import datetime
import requests

## Setup
# Connecting to Database and setting up Webserver
conn = sqlite3.connect('points.db') # connects to database and stores it in a file
c = conn.cursor()
# This table tracks how many points have been spent
c.execute("""CREATE TABLE IF NOT EXISTS points_tracker (
            payer text,
            points integer,
            timestamp text)""")
conn.commit()
conn.close()
conn = sqlite3.connect('points.db') # connects to database and stores it in a file
c = conn.cursor()
# This table tracks all transactions positive and negative
c.execute("""CREATE TABLE IF NOT EXISTS transactions_all (
            payer text,
            points integer,
            timestamp text)""")
conn.commit()
conn.close()

app = flask.Flask(__name__)
## Setup

@app.route("/clear_db", methods=["PUT"])
def clear_db():
    # clears current database
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    c.execute("DELETE FROM points_tracker")
    c.execute("DELETE FROM transactions_all")
    conn.commit()
    conn.close()
    return "Database Cleared"

@app.route("/show_table_tracker", methods=["GET"])
def show_table_tracker():
    # displays the table that tracks points spent
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    c.execute("SELECT * FROM points_tracker")
    db = c.fetchall()
    conn.close()
    return Response(json.dumps(db), mimetype='application/json')

@app.route("/show_table_all", methods=["GET"])
def show_table_all():
    # displays the table that tracks all transactions
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions_all")
    db = c.fetchall()
    conn.close()
    return Response(json.dumps(db), mimetype='application/json')
    
@app.route("/add_transactions", methods=["PUT"]) 
def add_transaction(): 
    # loads db up with transactions
    # accepts .json's with just one or multiple transactions
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    json_data = flask.request.json
    for row in json_data:
        payer = row["payer"]
        points = row["points"]
        timestamp = row["timestamp"]
        c.execute( "INSERT INTO points_tracker VALUES ('{}','{}','{}')".format(payer,points,timestamp))
        c.execute( "INSERT INTO transactions_all VALUES ('{}','{}','{}')".format(payer,points,timestamp))
        conn.commit() # saves database
    ## clean database
    # This section takes negative points in transactions and subtracts them from positive point transactions
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    c.execute("SELECT payer, points,timestamp FROM points_tracker WHERE points<0")
    neg_payer = c.fetchall()
    for row in neg_payer:
        points_spend= -row[1]
        payer = row[0]
        timestamp = row[2]
        c.execute("UPDATE points_tracker SET points =? WHERE timestamp=?",(0,timestamp,))
    c.execute("SELECT payer, points, timestamp FROM points_tracker WHERE points>0 AND payer=? AND timestamp<? ORDER BY timestamp ASC",(payer,timestamp,))
    try:
        payer,points,timestamp = c.fetchone()
        while points_spend>0:
            if points<points_spend:
                        points_spend = points_spend-points
                        c.execute("UPDATE points_tracker SET points =? WHERE timestamp=?",(0,timestamp,))
                        conn.commit()
                        payer,points,timestamp = c.fetchone()
            else:
                    c.execute("UPDATE points_tracker SET points =? WHERE timestamp=?",(points-points_spend,timestamp,))
                    points_spend = 0
                    conn.commit()
        conn.close()
    except:
        return "transactions added. developer note: no negative transactions found"
    return "transactions added. developer note: negative transactions found and cleaned"
    ## clean database
    
@app.route("/spend_points", methods=["PUT"])
def spend_points():
    # Input JSON ex: {"points":5000} to spend 5000 points
    # Returns a JSON of payer, points spent, and timestamp of spending points.
    # We want the oldest points to be spent first (oldest based on transaction timestamp, not the order they’re received)
    # This function will only redeem points from a payer if the sum of the points from all transactions with that payer > 0
    json_spend = flask.request.json
    points_spend = json_spend["points"]
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    z = conn.cursor()
    z.execute("SELECT SUM(points) FROM points_tracker")
    points_sum = z.fetchone()
    if points_sum[0]<points_spend: # We want no payer's points to go negative.
        can_redeem = 0
    else:
          can_redeem= 1 
    if can_redeem == 1:
        c.execute("SELECT payer, points, timestamp FROM points_tracker WHERE points > 0 ORDER BY timestamp ASC")
        # performance/scalability: This could end up creating a really large list if you have a lot of transactions
        # performance/scalbility: Would probably be best to only select payers where the sum of points = the amount to be spent
        payer,points,timestamp = c.fetchone() # start taking in who is going to pay
        points_original = []
        timestamp_original = []
        i=0
        points_spent=[]
        points_spent_time=[]
        while points_spend>0:
                if points<points_spend:
                    # Modularity/legibility: could be better to set a boolean like canRedeem = points < points_spend
                    time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") # iso 8601 time
                    points_spent.append({"payer":payer, "points":points})
                    points_spent_time.append({"payer":payer, "points":-points, "timestamp":time})
                    points_spend = points_spend-points
                    points_original.append(points)
                    timestamp_original.append(timestamp)
                    payer,points,timestamp = c.fetchone()
                else:
                    time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") # iso 8601 time
                    points_spent.append({"payer":payer, "points":points_spend})
                    points_spent_time.append({"payer":payer,"points":-points_spend,"timestamp":time})
                    points_spend = 0
                    points_original.append(points)
                    timestamp_original.append(timestamp)
                i+=1
        j=0
        for row in points_spent_time:
            payer = row["payer"]
            points = row["points"]
            timestamp_current = row["timestamp"]
            points_sum = points_original[j]+points
            c.execute("UPDATE points_tracker SET points =? WHERE timestamp=?",(points_sum,timestamp_original[j],))
            conn.commit() 
            c.execute("INSERT INTO transactions_all VALUES ('{}','{}','{}')".format(payer,points,timestamp_current))
            conn.commit() # saves database
            j+=1
        conn.close()
        return Response(json.dumps(points_spent_time), mimetype='application/json')
    else:
        return("not enough points")
        
@app.route("/show_balance", methods=["GET"])
def show_balance():
    # outputs the sum of each payer's points in a JSON
    conn = sqlite3.connect('points.db')
    c = conn.cursor()    
    c.execute("SELECT payer, points FROM transactions_all")
    payer_points = c.fetchall()
    balance = {}
    for i in range(len(payer_points)):
        payer,points = payer_points[i]
        if payer not in balance:
            balance[payer] = 0
        balance[payer] += points
        if balance[payer] < 0:
            balance[payer] = 0
    return json.dumps(balance)
  
if __name__ == "__main__":
    app.run(debug=True)    