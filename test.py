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
        guess= ls.initial_guess()

    def test_least_squares(self):
        truth = {'s1':3,'s2':5,'s3':3.3}
        sim = {'s1':1,'s2':4,'s3':4}
        self.assertEqual(ls._least_squares(truth,sim),5.49)

    def test_get_sim_values(self):
        self.assertEqual(ls._get_sim_value('f1','s1',10),4.1)
        self.assertEqual(ls._get_sim_value('f3','s2',0),.001)
        self.assertEqual(ls._get_sim_value('f2','s3',30), 22)

    def test_get_sim_single_fix(self):
        self.assertEqual(ls._get_sim_single_fix('f1',0),{'s1': 3.4, 's2': 5.5, 's3': 10.0})
        self.assertEqual(ls._get_sim_single_fix('f3',10),{'s1': 1.43, 's2': 0.011, 's3': 5})
        
    def test_get_sim_all_fix(self):
        d = {'f1':0,'f2':10,'f3':20}
        ans = ls._get_sim_all_fix(d)
        for key,val in ans.iteritems():
            assert type(val) == dict
            assert type(key) == str
        self.assertEqual(ans['f1'],{'s3': 10.0, 's2': 5.5, 's1': 3.4})
        self.assertEqual(ans['f2'], {'s3': 9.0, 's2': 13.0, 's1': 1.0})
        self.assertEqual(ans['f3'], {'s3': 15.0, 's2': 0.9011, 's1': 5.43})

    def test_sum_sensor_readings(self):
        d = {'f1':0,'f2':10,'f3':20}
        ans = ls._get_sim_all_fix(d)
        #config = {'f1':{'s1':10,'s2':20,'s3':30},'f2':{'s1':3,'s2':7,'s3':1}}
        self.assertEqual(ls._sum_sensor_readings(ans),{'s1':9.83,'s2':19.4011,'s3':34.0})

    def test_within_tol(self):
        sensor_sim = {'s1':2.88, 's2':0.00, 's3':10}
        truth = {'s1':3.5, 's2':1, 's3':7.82}
        assert ls.within_tol(sensor_sim,truth,10)
        assert not ls.within_tol(sensor_sim,truth,2.3)

    def test_form_query(self):
        fix_config = 1
        ans = 'select s1,s2,s3 from truth where id=1;'
        self.assertEqual(ls.form_query(fix_config),ans)

    def test_get_truth(self):
        fix_config = 1
        r = ls.get_truth(fix_config)
        self.assertEqual(r,{'s1':1.34,'s2':5.55,'s3':20.0})
        #self.assertRaises(Exception('No record found'),ls.get_truth(fix_config,90))

    def test_cost(self):
        truth = ls.get_truth(1)
        self.assertEqual(truth,{'s1':1.34,'s2':5.55,'s3':20})
        fconfig = {'f1':10,'f2':20,'f3':0}
        cost = int(ls.cost(fconfig,truth))
        self.assertEqual(cost,427)
        #s = '{}, {}'.format(fconfig,cost)
        # s
 
    def test_neighbors(self):
        config = {'f1':0,'f2':10,'f3':20}
        #print config
        tol = 10
        gener=ls.neighbors(config,tol)
        for t in gener:
            #make sure we are within the tolerance
            for key in t.iterkeys():
                self.assertTrue( abs(t[key] - config[key]) <= tol)

    def test_log(self):
        fid = open('tmp.txt','a')
        ls.log(fid,'hello')
        ls.log(fid,'world')
        pass

    def test_best_neighbor(self):
        config = {'f1':0,'f2':10,'f3':20}
        #print config
        tol = 10
        gener=ls.neighbors(config,tol)
        ideal = {'s1':1.1,'s2':15,'s3':10}
        #print 'BEST',ls.best_neighbor(gener,ideal)

    
    def test_local_search(self):
        ls.local_search(20)
        pass

if __name__ == '__main__':
    unittest.main()
