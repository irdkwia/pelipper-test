from structure.models import *
from random import randrange
import sqlite3
from sqlite3 import OperationalError
from hashlib import md5
import time

class Connection:

    @staticmethod
    def connect():
        return sqlite3.connect("database/pelipper.db")
    
    @staticmethod
    def update_elements(elist, conditions=None):
        con = Connection.connect()
        cur = con.cursor()
        for element in elist:
            keys = element.__class__.key
            d = {k if not k.startswith("_") else k[1:]: v for k, v in element.__dict__.items()}
            d["udate"] = int(time.time())
            
            query = "UPDATE %s SET %s" % (element.__class__.__name__, ",".join("%s=:%s" % (k, k) for k in d))
            if conditions is None:
                conditions = dict()
            query += " WHERE %s" % (" AND ".join(["%s=:%s"%(k, k) for k in keys]+["%s=:_%s" % (k, k) for k in conditions]))
            d.update({"_"+k: v for k, v in conditions.items()})
            cur.execute(query, d)
        con.commit()
        cur.execute("SELECT total_changes()")
        nbupdates = cur.fetchone()[0]
        con.close()
        return nbupdates
    
    @staticmethod
    def increment_count(elist, counters, conditions=None):
        con = Connection.connect()
        cur = con.cursor()
        for element in elist:
            keys = element.__class__.key
            
            query = "UPDATE %s SET %s" % (element.__class__.__name__, ",".join("%s=%s+1" % (k, k) for k in counters))
            if conditions is None:
                conditions = dict()
            query += " WHERE %s" % (" AND ".join(["%s=:%s"%(k, k) for k in keys]+["%s=:_%s" % (k, k) for k in conditions]))
            d = {k: getattr(element, k) for k in keys}
            d.update({"_"+k: v for k, v in conditions.items()})
            cur.execute(query, d)
        con.commit()
        cur.execute("SELECT total_changes()")
        nbupdates = cur.fetchone()[0]
        con.close()
        return nbupdates
    
    @staticmethod
    def insert_elements(elist):
        con = Connection.connect()
        cur = con.cursor()
        for element in elist:
            d = {k if not k.startswith("_") else k[1:]: v for k, v in element.__dict__.items()}
            d["udate"] = int(time.time())
            query = "INSERT INTO %s (%s) VALUES (%s)" % (element.__class__.__name__, ",".join(d), ",".join(":"+k for k in d))
            cur.execute(query, d)
        con.commit()
        cur.execute("SELECT total_changes()")
        nbupdates = cur.fetchone()[0]
        con.close()
        return nbupdates
    
    @staticmethod
    def get_elements(cls, conditions=None, ordering=None, limit=None):
        con = Connection.connect()
        cur = con.cursor()
        query = "SELECT * FROM %s" % (cls.__name__)
        if conditions is not None:
            query += " WHERE %s" % (" AND ".join("%s=:%s" % (k, k) for k in conditions))
        if ordering is not None:
            query += " ORDER BY %s" % (",".join(ordering))
        if limit is not None:
            query += " LIMIT %d" % (limit)
        if conditions:
            cur.execute(query, conditions)
        else:
            cur.execute(query)
        desc = list(map(lambda x: x[0], cur.description))
        lst = []
        for gps in cur.fetchall():
            gprofile = cls()
            for i, e in enumerate(desc):
                if e in gprofile.__dict__:
                    setattr(gprofile, e, gps[i])
                elif "_"+e in gprofile.__dict__:
                    setattr(gprofile, "_"+e, gps[i])
            lst.append(gprofile)
        con.close()
        return lst
    
    @staticmethod
    def delete_elements(cls, conditions):
        con = Connection.connect()
        cur = con.cursor()
        query = "DELETE FROM %s" % (cls.__name__)
        if conditions is not None:
            query += " WHERE %s" % (",".join("%s=:%s" % (k, k) for k in conditions))
        cur.execute(query, conditions)
        con.commit()
        cur.execute("SELECT total_changes()")
        nbupdates = cur.fetchone()[0]
        con.close()
        return nbupdates
