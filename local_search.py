"""
Local search algorithm for skywall

c <- initial configuration guess
while c not within tolerance:
    n <- neighbors of c
    c <- lowest cost neighbor

The configuration cost is something that was computed before-hand thus
we cans simlpy obtain it. Haven't yet decided on the format, but it
will most likely be a database. I elect to use mysql since labview
will be using mysql as well.

For testing and development purposes we can setup dummy tables.


TODO:
Dont like how _get_sensors(), _get_fixtures() are hardcoded in, should abstract it out

change local_search() such that if criteria is not met with a given
dimming radius, then expand that radius

implement smarter initial guess using PCA. A better guess will help
the search converge faster

create a form_matrix() that will return a matrix as a string in the form

    e1 e2 e3;
    e4 e5 .......
So we can pass that into numpy
"""
import _mysql
import math
import random
import sys
import datetime
import argparse
import os
#host = 'localhost'
#user = 'root'
#userpass = 'rootiam'
#db = 'test'
#db = 'realtest'
fixtures = None
sensors = None
dimlvls = None
con = None
configType = dict

def time_string():
    """
    Returns th current itme as a string in the format
    <YEAR>_<MONTH>_<DAY>_<HOUR>_<MINUTE>_<SECOND>
    """
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def _get_sensors(sensorfile):
    """
    Reads a list of sensor names from a file, one per line, and returns them as a list of strings.
    """
    global sensors
    assert os.path.exists(sensorfile)
    fid = open(sensorfile,'r')
    slist = []
    for line in fid.readlines():
        line = line.strip()
        if len(line) != 0:
            slist.append(line)
    sensors = slist
    return slist

def _get_dimlvl(dimfile):
    """
    Reads a file containing dimming levels, one per line, and 
    returns a list of ints
    """
    assert os.path.exists(dimfile)
    fid = open(dimfile,'r')
    return [int(x.strip()) for x in fid.readlines() if len(x.strip()) > 0]

def _get_fixtures(fixturefile):
    """
    Returns a list of fixtues.
    """
    global fixtures
    assert os.path.exists(fixturefile)
    fid = open(fixturefile)
    flist = []
    for line in fid.readlines():
        line = line.strip()
        if len(line) > 0: flist.append(line)
    fixtures = flist
    return flist

def _sensor_type():
    global sensors
    return type(sensors[0])

def _fixture_type():
    global fixtures
    return type(fixtures[0])

def _dimlvl_type():
    global dimlvls
    return type(dimlvls[0])

def connect(host,usr,upass, db):
    global con
    con = _mysql.connect(host,usr,upass,db)

def _get_sim_value(fid, sid, diml):
    """
    Get the SIMULATED sensor value of sensor sid when fixture fid is at dimming level diml.
    Returns a float.
    The fid is the name of the table that the record should be stored in.

    @param fid - fixture id, string
    @parad sid - sensor id, string
    @param diml - dimming level, int

    For example, running the following on a mysql server
    mysql> select * from f1; 
    should yield something like:
    
    +------+------+------+------+
    | dim  | s1   | s2   | s3   |
    +------+------+------+------+
    |    0 |  3.4 |  5.5 |   10 |
    |   10 |  4.1 | 10.4 | 11.1 |
    |   20 |  4.4 | 15.2 |   12 |
    |   30 |  4.5 | 25.2 | 12.5 |
    |   40 | NULL | NULL | NULL |

    """
    global con
    assert con is not None
    assert diml >= 0
    assert type(fid) == str
    assert type(sid) == str
    try:
        con.query('select {} from {} where dim = {}'.format(sid,fid,diml))
        result = con.use_result()
        ans = result.fetch_row()
        return float(ans[0][0]) #result should be float
    except _mysql.ProgrammingError:
        raise _mysql.ProgrammingError, 'Query malformed, check table name'
    except IndexError:
        raise Exception("IndexError make sure table {} exists and has values for dimming level {}".format(f1,diml))

def _least_squares(truth, simul):
    """    
    Return the least squares of dictionaries mapping from sensorID --> value
    
    @param truth - list of ordered observed sensor readings
    @param simul - list of ordered simulated readings
    """
    assert type(truth) == type(simul)
    assert type(truth) == type({})
    lsq = 0.0
    for key in truth.iterkeys():
        assert key in simul
        assert type(truth[key] == float) or type(truth[key] == int)
        assert type(simul[key] == float) or type(simul[key] == int)
        lsq =lsq + math.pow(float(truth[key]) - float(simul[key]),2)
    return lsq
    
def initial_guess():
    """
    Returns the inital fixture configuration, mapping from fixtureID --> dimming level
    """
    fixtures = _get_fixtures()
    dim = _get_dimlvl()
    config = {}
    for fix in fixtures:
        ridx = random.randint(0,len(dim)-1)
        config[fix] = dim[ridx]
    return config

def within_tol(config,ideal, tol):
    """
    Returns true if _least_squares(config,ideal)<tol

    :config - dictionary
    :ideal -dictionary
    :tol - float
    """
    assert type(config) == type(ideal)
    lsq = _least_squares(config,ideal)
    return lsq <= tol

def neighbors(config,tol=20):
    """
    Returns a generator containing neighbors of configuration config, that are within a certain
    tolerance.

    Should make this an iterator, since the list might be larger.
    config: dictionary (string --> float)
    tol: float
    """
    fixtures = _get_fixtures()
    dimlvls = _get_dimlvl()
    #for each fixture we iterate through all the setting that are within the
    #tolerance of the current fixture level
    for f in fixtures:
        for d in dimlvls:
            try:
                if config[f] != d:
                    if abs(config[f]-d)<=tol:
                        tmp = config.copy()
                        tmp[f] = d
                        yield tmp
            except Exception, e:
                print config,e
                raise Exception('key error! What?')
        

def _get_sim_single_fix(fix_id, diml):
    """
    Returns a dictionary that maps from fix_id --> {sensor_id -->
    reading}, based on the dimming level diml. When fixture fix_id is
    on dimming level diml, how much are the sensors affected?
    """
    sensors = _get_sensors()
    d = {}
    for s in sensors:
        val = _get_sim_value(fix_id,s, diml)
        d[s] = val
    return d

def _get_sim_all_fix(config):
    """
    Given a dictinary of fixtureID --> dimming levels, return a dictionary within a dictionary
    that maps from fixtureID --> {sensorID --> reading}  (based on that fixure's dimming level)
    """
    global configType
    assert type(config) == configType
    d = {}
    for fixture in config.keys():
        val = _get_sim_single_fix(fixture,config[fixture])
        d[fixture] = val
    return d

def _sum_sensor_readings(sreadings):
    """
    sreadings is a dictionary of dictionaries mapping from fixtureID --> {sensorID --> reading}

    Sum all the readings according to sensorID and return a dictionary mapping from
    sensorID --> sum of reading values
    """
    sensors = _get_sensors()
    d ={}
    val = 0
    for sensor in sensors:
        sval = 0.0
        for fixtures in sreadings.iterkeys():
            sval += float(sreadings[fixtures].get(sensor,0))
        d[sensor] = sval
    return d

def form_query(sid, tablename='truth'):
    """
    Given the fixture configuration we will form the query
    Select <all sensor readings> from tablename where <f1,f2,...,fn> matches fix_config and
    angle == this.angle
    """
    query = 'select '
    for sensor in _get_sensors():
        query += '%s,'%sensor
    query = query[:-1] #remove ending comma
    query += ' from %s where id=%s;'%(tablename,sid)
    return query

def get_truth(sid):
    """
    Given the id of our ground truth, we return a dictionary
    consisting of sensor readings

    We assume that configuration is in our truth table! We have to have this assumption, that's
    what we are solving for!
    Assume we have one global truth table. (might have to split up later)
    
    ID (primary)| s1| s2| ...| sn| angle| timestamp

    Using our current test database, we have
    
    | id | s1   | s2   | s3   | angle | time                |
    +----+------+------+------+-------+---------------------+
    |  1 | 1.34 | 5.55 |   20 |    60 | 2013-04-15 14:16:57 |

    get_truth(1) --> {'s1':1.34, 's2':5.55, 's3':20.0,}
    """
    global con
    assert con is not None
    q = form_query(sid)
    con.query(q)
    result = con.use_result()
    ans = result.fetch_row(how=1) #get result as a dictionary
    if len(ans) > 0:
        for key in ans[0]:
            ans[0][key] = float(ans[0][key]) #convert to float, as is expected.
        return ans[0]
    else:
        #no record found
        raise Exception('Ground truth no found for ID {}. Check that table/record exists and its in the rigth database'.format(sid))

def cost(fix_config,truth):
    """
    Returns the cost of fixture configuration config, mapping from fixtureID --> dimming level
    The cost is the least squares of the simulated values from the ground truth

    :fix_config - dictionary mapping from str --> {str --> float}
    :truth - dictionary mapping from str --> float
    """
    global configType
    assert type(fix_config) == configType
    #get simulated sensor readings for sensor per fixture
    sim_values = _get_sim_all_fix(fix_config)
    #sum over all fixtures, simulated values
    sim_sum = _sum_sensor_readings(sim_values)
    return _least_squares(sim_sum, truth)

def best_neighbor(nbors, ideal):
    """
    Returns the best (lowest cost) neighbor from a collection of neighbors nbors
    when compared against ideal
    """
    mcost = float('inf') #min cost, initially some arbitrary high number
    mbor = {} # the best neighbor
    for nbor in nbors:
        tcost = cost(nbor,ideal)
        if tcost < mcost:
            mcost = tcost
            mbor = nbor
    if mbor == {}:
        raise Exception('No neighbors were less than float(inf)!')
    return mbor

def log(fid,output):
    """
    Given a file descriptor, fid, write output to it appended with a new line.
    """
    fid.write("{}\n".format(output))
    fid.flush()

def local_search(cid = 1,tol = 200, stol = 20):
    """
    Full local search algorithm

    cid - configuration id of desired ground truth , int
    tol - tolerance, int
    stol - neighborhood search tolerance, int
    """
    print 'LS ========='
    fname = 'log_{}.txt'.format(time_string())
    fpath = os.path.join(os.getcwd(),'log',fname)
    fid = open(fpath,'a')
    config = initial_guess()
    truth = get_truth(cid)
    log(fid,'TRUTH | {} | {}'.format(truth,tol))
    tcost = cost(config,truth)
    log(fid,'GUESS | {} | {}'.format(config,tcost))
    assert tcost > 0
    while tcost >= tol:
        neighs = neighbors(config,stol)
        next_config = best_neighbor(neighs,truth)
        nextcost = cost(next_config,truth)
        #check to make sure the next one is better than the current
        if nextcost < tcost:
            tcost = nextcost
            config = next_config
            log(fid,'GUESS | {} | {}'.format(config,tcost))
        else:
            print 'Local minima at {}'.format(config)
            log(fid,'MINIMA | {} | {}'.format(config,tcost))
            return config
        config = next_config
    return config
#host = 'localhost'
#user = 'root'
#userpass = 'rootiam'
#db = 'test'
#db = 'realtest'
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--host',help='Host machine of database',default='localhost',required=True)
    parser.add_argument('-d','--database',help='Name of database to use',required=True)
    parser.add_argument('-u','--username',help='username to login to database',required=True,action='store')
    parser.add_argument('-p','--password',help='login password',required=True,action='store')
    parser.add_argument('-g','--ground',help='The id of the ground truth',required=True,type=int)
    parser.add_argument('-t','--tolerance',help='Tolerance for local search, once we get below the tolerance, local search ends',type=float,default=200)
    parser.add_argument('-r','--radius',help='Radius of neighborhood to consider',type=float,default=200)
    parser.add_argument('-f','--fixturefile',help='File containing fixtures, one per line',default='fixtures.txt')
    parser.add_argument('-s','--sensorfile',help='File containing sensors, oen per line',default='sensors.txt')
    parser.add_argument('-l','--dimfile',help='File containing dimming levels, one per line',default='dimlevels.txt')
    args = parser.parse_args()
    if args.host and args.database and args.username and args.password:
        #connect to the database
        connect(args.host, args.username, args.password,args.database)
        #if database connection succeeds, then we proceed to doing local search
        local_search(args.ground,args.tolerance, args.radius)
        parser.exit(message= "Connection done\n")
    #connect(host,user,userpass,db)
    pass



