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
maxid = 169  #max number of configurations

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
    
