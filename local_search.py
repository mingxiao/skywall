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
    """
    Get the SIMULATED sensor value of sensor sid when fixture fid is at dimming level diml
    """
    con.query('select s%s from F%s_SIM where diml = %s'%(sid,fid,diml))
    result = con.use_result()
    return result.fetch_row()[0][0]
        
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
    Returns the cost of configuration config
    """
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



