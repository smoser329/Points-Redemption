# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 20:34:36 2022

@author: Samuel Moser
"""
import sqlite3 # library for creating a db in memory hence 'lite'
import flask # webserver library
from flask import Flask, Response, json # more webserver things
import datetime

app = flask.Flask(__name__)

def create_table():
    conn = sqlite3.connect('transactions10.db') # connects to database and stores it in a file
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS transactions10 (
                payer text,
                points integer,
                timestamp text)""")
    conn.commit()
    conn.close()
    return 'table made'

@app.route("/clear_db", methods=["PUT"])
def clear_db():
    #clears current database
    conn = sqlite3.connect('transactions10.db')
    c = conn.cursor()
    c.execute("DELETE FROM transactions10")
    conn.commit()
    conn.close()
    return "Database Cleared"

@app.route("/show_db", methods=["GET"])
def show_db():
    #displays current database
    conn = sqlite3.connect('transactions10.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions10")
    db = c.fetchall()
    conn.close()
    return Response(json.dumps(db), mimetype='application/json')
    
@app.route("/add_transactions", methods=["PUT"]) 
def add_transaction(): 
    #loads db up with transactions
    #accepts .json's with just one or multiple transactions
    conn = sqlite3.connect('transactions10.db')
    c = conn.cursor()
    json_data = flask.request.json
    for row in json_data:
        payer = row["payer"]
        points = row["points"]
        timestamp = row["timestamp"]
        c.execute( "INSERT INTO transactions10 VALUES ('{}','{}','{}')".format(payer,points,timestamp))
        conn.commit() # saves database
    conn.close()
    return "transactions added"

@app.route("/spend_points", methods=["PUT"])
def spend_points():
    # We want the oldest points to be spent first (oldest based on transaction timestamp, not the order they’re received)
    # This function will only redeem points from a payer if the sum of the points from all transactions with that payer > 0
    json_spend = flask.request.json
    points_spend = json_spend["points"]
    conn = sqlite3.connect('transactions10.db')
    c = conn.cursor()
    z = conn.cursor()
    z.execute("SELECT SUM(points) FROM transactions10")
    points_sum = z.fetchone()
    if points_sum[0]<points_spend: # We want no payer's points to go negative.
        can_redeem = 0
    else:
          can_redeem= 1 
    if can_redeem == 1:
        c.execute("SELECT payer, points, timestamp FROM transactions10 WHERE points > 0 ORDER BY timestamp ASC")
        payer,points,timestamp = c.fetchone()
        points_original = []
        timestamp_original = []
        i=0
        points_spent=[]
        points_spent_time=[]
        while points_spend>0:
                if points<points_spend:
                    time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") #iso 8601 time
                    points_spent.append({"payer":payer, "points":points})
                    points_spent_time.append({"payer":payer, "points":points, "timestamp":time})
                    points_spend = points_spend-points
                    points_original.append(points)
                    timestamp_original.append(timestamp)
                    
                    payer,points,timestamp = c.fetchone()
                else:
                    time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") #iso 8601 time
                    points_spent.append({"payer":payer, "points":points_spend})
                    points_spent_time.append({"payer":payer,"points":points_spend,"timestamp":time})
                    points_spend = 0
                    points_original.append(points)
                    timestamp_original.append(timestamp)
                i+=1
        j=0
        for row in points_spent_time:
            payer = row["payer"]
            points = -row["points"]
            timestamp_current = row["timestamp"]
            points_sum=points_original[j]+points
            c.execute("UPDATE transactions10 SET points =? WHERE timestamp=?",(points_sum,timestamp_original[j],))
            conn.commit() 
            c.execute( "INSERT INTO transactions10 VALUES ('{}','{}','{}')".format(payer,points,timestamp_current))
            conn.commit() # saves database
            j+=1
        conn.close()
        return Response(json.dumps(points_spent_time), mimetype='application/json')
    else:
        return("not enough points")
        
@app.route("/show_balance", methods=["GET"])
def show_balance(): # provides the sum of each payer's points
    conn = sqlite3.connect('transactions10.db')
    c = conn.cursor()    
    c.execute("SELECT payer, points FROM transactions10")
    payer_points = c.fetchall()
    payer = []
    points = []
    balance = {}
    for i in range(len(payer_points)):
        payer,points = payer_points[i]
        if payer not in balance:
            balance[payer] = 0
        balance[payer] += points
        if balance[payer] <0:
            balance[payer] = 0
    return balance
  
if __name__ == "__main__":
    app.run(debug=True)    
    create_table()