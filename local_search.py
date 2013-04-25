"""
Local search algorithm for skywall

c <- initial configuration guess
while c not within tolerance:
    n <- neighbors of c
    c <- lowest cost neighbor

The configuration cost is something that was computed before-hand thus we
cans simlpy obtain it. Haven't yet decided on the format, but it will most likely
be a database. I elect to use mysql since labview will be using mysql as well.

For testing and development purposes we can setup dummy tables.


TODO:
non-trivial experimental data inputted. now for testing
"""
import _mysql
import math
import random
import sys
import datetime

#host = 'localhost'
#user = 'root'
#userpass = 'rootiam'
#db = 'test'
#db = 'realtest'
con = None
configType = dict

def time_string():
    """
    Returns th current itme as a string in the format
    <YEAR>_<MONTH>_<DAY>_<HOUR>_<MINUTE>_<SECOND>
    """
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def _get_sensors():
    """
    returns a list of sensors
    """
    return ['s{}'.format(i) for i in range(1,14)]
    #return ['s1','s2','s3']

def _get_dimlvl():
    """
    Return a list of valid dimming levels
    """
    return [0,10,20,30,40,50,60,70,80,90]
    #return [0,10,20,30]


def _get_fixtures():
    """
    Returns a list of fixtues.
    """
    #return ['f1','f2','f3']
    return ['f{}'.format(i) for i in range(1,89)]

def _sensor_type():
    return type(_get_sensors()[0])

def _fixture_type():
    return type(_get_fixtures()[0])

def _dimlvl_type():
    return type(_get_dimlvl()[0])

def connect(host,usr,upass, db):
    global con
    con = _mysql.connect(host,usr,upass,db)

def _get_sim_value(fid, sid, diml):
    """
    Get the SIMULATED sensor value of sensor sid when fixture fid is at dimming level diml.
    Returns a float

    @param fid - fixture id, string
    @parad sid - sensor id, string
    @param diml - dimming level, int
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
    tolerance

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
    Returns a dictionary that maps from fix_id --> {sensor_id --> reading}, based
    on the dimming level diml
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
    q = form_query(sid)
    print 'QUERY',q
    con.query(q)
    result = con.use_result()
    ans = result.fetch_row(how=1) #get result as a dictionary
    if len(ans) > 0:
        for key in ans[0]:
            ans[0][key] = float(ans[0][key]) #convert to float, as is expected.
        return ans[0]
    else:
        #no record found
        raise Exception('No record found')

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

    ERROR: in our setup the initial mcost is lower then all the other
    neighbors!
    """
    mcost = float('inf') #min cost, initially some arbitrary high number
    mbor = {} # the best neighbor
    for nbor in nbors:
        #print 'NBOR',nbor,type(nbor)
        tcost = cost(nbor,ideal)
        if tcost < mcost:
            mcost = tcost
            mbor = nbor
    #print 'BEST',mbor
    if mbor == {}:
        raise Exception('No neighbors were less than sys.maxint!')
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

    cid - configuration id , int
    tol - tolerance, int
    stol - neighborhood search tolerance, int
    """
    print 'LS ========='
    fname = 'log_{}.txt'.format(time_string())
    fid = open(fname,'a')
    config = initial_guess()
    truth = get_truth(cid)
    log(fid,'TRUTH, {}, {}'.format(truth,tol))
    tcost = cost(config,truth)
    log(fid,'GUESS, {}, {}'.format(config,tcost))
    assert tcost > 0
    while tcost >= tol:
        print 'CURRENT',config
        neighs = neighbors(config,stol)
        next_config = best_neighbor(neighs,truth)
        nextcost = cost(next_config,truth)
        #check to make sure the next one is better than the current
        print nextcost, tcost
        if nextcost < tcost:
            tcost = nextcost
            config = next_config
            log(fid,'GUESS, {}, {}'.format(config,tcost))
        else:
            print 'Local minima at {}'.format(config)
            log(fid,'MINIMA, {},{}'.format(config,tcost))
            return
        config = next_config
    return config

if __name__ == '__main__':
    #connect(host,user,userpass,db)
    #print con
    #print _get_sim_value(1,2,0)
    pass



