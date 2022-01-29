# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 22:54:39 2022

@author: smose
"""
import sqlite3
conn = sqlite3.connect('transactions10.db')
c = conn.cursor()
c.execute("DELETE FROM transactions10")
conn.commit()
conn.close()

import sqlite3
conn = sqlite3.connect('transactions10.db')
c = conn.cursor()
c.execute("SELECT * FROM transactions10")
payer_points = c.fetchall()