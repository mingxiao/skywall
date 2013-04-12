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

host = 'localhost'
user = 'root'
userpass = 'rootiam'
db = 'test'
con = None
configType = dict
sensors = [1,2,3] #for testing there are only 3 sensors

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
    TODO: redo this so the inputs are dictionaries!
    
    Return the least squares of two list of numbers
    
    @param truth - list of ordered observed sensor readings
    @param simul - list of ordered simulated readings
    """
    assert len(truth) == len(simul)
    diff = [math.pow(x - y,2) for x,y in zip(truth,simul)]
    return sum(diff)
    
def initial_guess():
    """
    Returns the inital configuration guess. Do not know the form of the
    configuration yet.
    """
    raise NotImplementedError

def with_tol(config):
    """
    Returns true if configuration config is within the tolerance
    """
    raise NotImplementedError

def neighbors(config):
    """
    Returns the neighbors of configuration config
    """
    raise NotImplementedError

def _get_sim_single_fix(fix_id, diml):
    """
    Returns a dictionary that maps from fix_id --> {sensor_id --> reading}, based on the dimming
    level diml
    """
    global sensors
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
    global sensors
    d ={}
    val = 0
    for sensor in sensors:
        sval = 0
        for fixtures in sreadings.iterkeys():
            sval += sreadings[fixtures].get(sensor,0)
        d[sensor] = sval
    return d

def cost(config):
    """
    Returns the cost of configuration config. The cost is the least squares of the simulated
    values from the ground truth
    """
    global configType
    assert type(config) == configType
    #get simulated sensor readings for sensor per fixture
    sim_values = _get_sim_all_fix(config)
    #sum over all fixtures, simulated values
    #get the ground truth sensor readings
    #output least squares
    raise NotImplementedError

def best_neighbor(nbors):
    """
    Returns the best (lowest cost) neighbor from a collection of neighbors nbors
    """
    raise NotImplementedError

if __name__ == '__main__':
    connect(host,user,userpass,db)
    print con
    print _get_sim_value(1,2,0)



