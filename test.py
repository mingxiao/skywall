"""
Unit test script for local_search.py
"""
import unittest
import local_search as ls
import _mysql as sql


class Test(unittest.TestCase):
    def setUp(self):
        #setup database connection
        host = 'localhost'
        user = 'root'
        password = 'rootiam'
        database = 'test'
        ls.connect(host,user,password,database)
        assert ls.con is not None

    def test_initial_guess(self):
        print ls.initial_guess()

    def test_least_squares(self):
        truth = {'s1':3,'s2':5,'s3':3.3}
        sim = {'s1':1,'s2':4,'s3':4}
        print ls._least_squares(truth,sim)

    def test_get_sim_single_fix(self):
        self.assertEqual(ls._get_sim_single_fix(1,0),{1: '3.4', 2: '5.5', 3: '10'})

    def test_get_sim_all_fix(self):
        d = {1:0,2:10}
        ans = ls._get_sim_all_fix(d)
        for key,val in ans.iteritems():
            assert type(val) == dict
            assert type(key) == int

    def test_sum_sensor_readings(self):
        config = {1:{1:10,2:20,3:30},2:{1:3,2:7,3:1}}
        self.assertEqual(ls._sum_sensor_readings(config),{1:13,2:27,3:31})
        
if __name__ == '__main__':
    unittest.main()
