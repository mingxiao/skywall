import unittest
import solver
import numpy as np

class Test(unittest.TestCase):

    def test(self):
        A = np.matrix('1 2; 3 4')
        b = np.matrix('5;6')
        print A
        print b
        x = np.linalg.solve(A,b)
        print x
    pass

if __name__ == '__main__':
    unittest.main()
