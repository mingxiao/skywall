import unittest
import dummy as dum

class Test(unittest.TestCase):
    def test_fixture_data(self):
##        for i in range(1,89):
##            dum.fixture_data('f{}.csv'.format(i))
        pass

    def test_create_truth(self):
        #dum.create_truth('truth.csv')
        pass

if __name__ == '__main__':
    unittest.main()
