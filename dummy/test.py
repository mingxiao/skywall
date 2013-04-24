import unittest
import dummy as dum

class Test(unittest.TestCase):
    def setUp(self):
        host = 'localhost'
        user = 'root'
        password = 'rootiam'
        db = 'realtest'
        dum.connect(host,user,password,db)
        
    def test_fixture_data(self):
##        for i in range(1,89):
##            dum.fixture_data('f{}.csv'.format(i))
        pass

    def test_create_truth(self):
        #dum.create_truth('truth.csv')
        pass

    def test_make_fixtablequery(self):
        print dum.make_fixtablequery('f1')

    def test_makeftable(self):
        #dum.make_ftable('f1')
        pass

    def test_create_truthtable(self):
        #dum.create_truthtable('truth')
        #dum.insertcsv('/home/ubuntu/Desktop/skywall/dummy/truth.csv','truth')
        pass

##    def test_insertcsv(self):
##        for i in range(1,89):
##            table = 'f{}'.format(i)
##            csv = '/home/ubuntu/Desktop/skywall/dummy/{}.csv'.format(table)
##            dum.make_ftable(table)
##            dum.insertcsv(csv,table)
        

if __name__ == '__main__':
    unittest.main()
