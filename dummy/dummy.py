"""
Dummy file to generate test data, and insert it into
our test database
"""

import random
import _mysql

dimlevels = [0,10,20,30,40,50,60,70,80,90]
angles = [(180/13)*i for i in range(13)]
sensors = ['s{}'.format(i) for i in range(1,14)]
smin = 0 #min sensor reading
smax = 10000 #max sensor reading
maxid = 169  #max number of configurations()

host = 'localhost'
user = 'root'
password = 'rootiam'
db = 'realtest'
con = None

def connect(host,usr,upass,db):
    global con
    con = _mysql.connect(host,usr,upass,db)

def make_fixtablequery(name):
    """
    create table <name> (int dim primary key, s1 float,...,s13 float);
    """
    var = 'dim int primary key,'
    for s in sensors:
        var += '{} float,'.format(s)
    var = var[:-1]
    query = 'CREATE TABLE {} ({});'.format(name,var)
    return query
    pass

def create_truthtable(truth):
    var = 'id int primary key,'
    for s in sensors:
        var += '{} float,'.format(s)
    var += 'angle float'
    q = 'create table if not exists {} ({});'.format(truth,var)
    global con
    con.query(q)

def insertcsv(csv,tablename):
    q= "load data local infile '{}' into table {} fields terminated by ',';".format(csv,
                                                                                   tablename)
    print q
    global con
    con.query(q)
    
def make_ftable(name):
    global con
    q = make_fixtablequery(name)
    con.query(q)

def fixture_data(fname):
    fid = open(fname,'w')
    for i in dimlevels:
        out = '{},'.format(i)
        for s in sensors:
            r = random.uniform(smin,smax)
            out += '{:.2f},'.format(r)
        fid.write('{}\n'.format(out))
    fid.flush()
    fid.close()
    pass


def create_truth(fname):
    fid = open(fname,'w')
    for i in range(1,maxid+1):
        out = '{},'.format(i)
        for s in sensors:
            r = random.uniform(smin,smax)
            out += '{:.2f},'.format(r)
        out += str(random.choice(angles))
        fid.write('{}\n'.format(out))
    fid.flush()
    fid.close()
    
