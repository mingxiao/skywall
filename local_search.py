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
What is the structure of the configurations? List, dictionary? Probably dictionary
"""
import _mysql
    
host = 'localhost'
user = 'root'
userpass = 'rootiam'
db = 'test'
con = None

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
    con.query('select s%s from F%s_SIM where diml = %s'%(sid,fid,diml))
    result = con.use_result()
    return result.fetch_row()[0][0]

def _least_squares(truth, simul):
    """
    Return the least squares of two list of numbers
    
    @param truth - list of ordered observed sensor readings
    @param simul - list of ordered simulated readings
    """
    assert len(truth) == len(simul)
    
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

def cost(config):
    """
    Returns the cost of configuration config. The cost is the least squares of the simulated
    values from the ground truth
    """
    #get simulated sensor readings for sensor per fixture
    #sum over all fixtures
    #get least squares
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
    pass



