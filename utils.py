#!/usr/bin/env python
# coding: utf-8
import sys, os
import sqlite3
import time

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

def hex2rgb(hexcode):
    h = hexcode.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except ValueError as e:
        raise e

    return conn

def create_table(conn):
    # conn = create_connection('db/led_messages.db')

    #{"elapsed": 20.0, "font": "sm-1", "type": "metric", "body": "moo|loo", "color": "#00f584", "behavior": "number"}#
    conn.execute('''CREATE TABLE LED_MESSAGE
         (
         ID                 INTEGER PRIMARY KEY AUTOINCREMENT,
         ELAPSERED          INT         NOT NULL,
         FONT               CHAR(50)    NOT NULL,
         TYPE               CHAR(50)    NOT NULL,
         BODY               CHAR(50)    NOT NULL,
         COLOR              CHAR(7)     NOT NULL,
         BEHAVIOUR          CHAR(50)        
         );''')

    print("LED_MESSAGE table created")


def select_all_messages(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM LED_MESSAGE")

    rows = cur.fetchall()

    all_m = []
    for row in rows:
        l_m = { 
            "ts": row[0],
            "elapsed": float(row[1]), 
            "font": row[2], 
            "type": row[3], 
            "body": row[4], 
            "color": row[5], 
            "behavior": row[6]
            }
        all_m.append({ "message":{ "payload": l_m }})

    return all_m
        

def delete_all_messages(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM LED_MESSAGE'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def create_message(conn, led_message):
    # print(led_message)
    led_message_t = (int(led_message['elapsed']), 
        led_message['font'], led_message['type'], 
        led_message['body'], led_message['color'], 
        led_message['behavior'])
 
    sql = ''' INSERT INTO LED_MESSAGE(ELAPSERED,FONT,TYPE,BODY,COLOR,BEHAVIOUR)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    # print(led_message_t)
    cur.execute(sql, led_message_t)
    conn.commit()
    return cur.lastrowid

