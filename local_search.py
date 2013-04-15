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
What is the structure of the configurations? List, dictionary?
Configurations are dictionaries that map from fixtureID --> Dimming Level

We have no guarantee on the numbering of the fixtureID, so we need a non-constrainted
way of getting values.
"""
import _mysql
import math
import random

host = 'localhost'
user = 'root'
userpass = 'rootiam'
db = 'test'
con = None
configType = dict

def _get_sensors():
    """
    returns a list of sensors
    """
    return [1,2,3]

def _get_dimlvl():
    """
    Return a list of valid dimming levels
    """
    return [0,10,20,30]

def connect(host,usr,upass, db):
    global con
    con = _mysql.connect(host,usr,upass,db)

def _get_sim_value(fid, sid, diml):
    global con
    assert con is not None
    assert fid >= 0
    assert sid >= 0
    assert diml >= 0
    """
    Get the SIMULATED sensor value of sensor sid when fixture fid is at dimming level diml

    @param fid - fixture id, int
    @parad sid - sensor id, int
    @param diml - dimming level, int
    """
    try:
        con.query('select s%s from F%s_SIM where diml = %s'%(sid,fid,diml))
        result = con.use_result()
        return result.fetch_row()[0][0]
    except _mysql.ProgrammingError:
        raise _mysql.ProgrammingError, 'Query malformed, check table name'

def _least_squares(truth, simul):
    """    
    Return the least squares of dictionaries mapping from sensorID --> value
    
    @param truth - list of ordered observed sensor readings
    @param simul - list of ordered simulated readings
    """
    assert type(truth) == type(simul)
    assert type(truth) == type({})
    lsq = 0
    for key in truth.iterkeys():
        assert key in simul
        lsq += math.pow(truth[key] - simul[key],2)
    return lsq
    
def initial_guess():
    """
    Returns the inital configuration guess. Do not know the form of the
    configuration yet. Probably a dictionary
    """
    sensors = _get_sensors()
    dim = _get_dimlvl()
    config = {}
    for sen in sensors:
        ridx = random.randint(0,len(dim)-1)
        config[sen] = dim[ridx]
    return config

def within_tol(config,ideal, tol):
    """
    Returns true if _least_squares(config,ideal)<tol

    :config - dictionary
    :ideal -dictionary
    :tol - float
    """
    lsq = _least_squares(config,ideal)
    return lsq <= tol

def neighbors(config):
    """
    Returns the neighbors of configuration config.

    Should make this an iterator, since the list might be larger.
    """
    raise NotImplementedError

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
        sval = 0
        for fixtures in sreadings.iterkeys():
            sval += sreadings[fixtures].get(sensor,0)
        d[sensor] = sval
    return d

def get_truth(fix_level):
    """
    Given a dictionary mapping from fixtureID --> Dimming Level, return the sensor reading
    for each sensor.
    """
    pass

def cost(fix_config,ideal):
    """
    Returns the cost of fixture configuration config, mapping from fixtureID --> dimming level
    The cost is the least squares of the simulated values from the ground truth
    """
    global configType
    assert type(fix_config) == configType
    #get simulated sensor readings for sensor per fixture
    sim_values = _get_sim_all_fix(fix_config)
    #sum over all fixtures, simulated values
    sim_sum = _sum_sensor_readings(sim_values)
    #get the ground truth sensor readings
    #output least squares
    raise NotImplementedError

def best_neighbor(nbors, ideal):
    """
    Returns the best (lowest cost) neighbor from a collection of neighbors nbors
    when compared against ideal
    """
    mcost = 10000000 #min cost, initially some arbitrary high number
    mbor = {} # the best neighbor
    for nbor in nbors:
        cost = cost(nbors,ideal)
        if cost < mcost:
            mcost = cost
            mbor = nbor
    return mbor

if __name__ == '__main__':
    connect(host,user,userpass,db)
    print con
    print _get_sim_value(1,2,0)



