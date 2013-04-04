"""
Local search algorithm for skywall

c <- initial configuration guess
while c not within tolerance:
    n <- neighbors of c
    c <- lowest cost neighbor

The configuration cost is something that was computed before-hand thus we
cans simlpy obtain it. Haven't yet decided on the format, but it will most likely
be a database. I elect to use sqlite as the database since python has a builtin
sqlite3 module.
"""

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
    pass



