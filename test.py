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
        self.assertEqual(ls._get_sim_single_fix('f1',0),{'s1': '3.4', 's2': '5.5', 's3': '10'})

    def test_get_sim_all_fix(self):
        d = {'f1':0,'f2':10}
        ans = ls._get_sim_all_fix(d)
        for key,val in ans.iteritems():
            assert type(val) == dict
            assert type(key) == str

    def test_sum_sensor_readings(self):
        config = {'f1':{'s1':10,'s2':20,'s3':30},'f2':{'s1':3,'s2':7,'s3':1}}
        self.assertEqual(ls._sum_sensor_readings(config),{'s1':13,'s2':27,'s3':31})

    def test_within_tol(self):
        sensor_sim = {'s1':2.88, 's2':0.00, 's3':10}
        truth = {'s1':3.5, 's2':1, 's3':7.82}
        #print ls._least_squares(sensor_sim,truth)
        assert ls.within_tol(sensor_sim,truth,10)
        assert not ls.within_tol(sensor_sim,truth,2.3)

    def test_form_query(self):
        fix_config = {'f1':10,'f2':20,'f3':0}
        angle = 60
        ans = 'select s1,s2,s3 from global_truth where f1=10 and f2=20 and f3=0 and angle=60;'
        self.assertEqual(ls.form_query(fix_config,angle),ans)

    def test_get_truth(self):
        fix_config = {'f1':10,'f2':20,'f3':0}
        angle = 60
        r = ls.get_truth(fix_config,angle)
        self.assertEqual(r,{'s1':'1.34','s2':'5.55','s3':'20'})
        #self.assertRaises(Exception('No record found'),ls.get_truth(fix_config,90))

if __name__ == '__main__':
    unittest.main()
