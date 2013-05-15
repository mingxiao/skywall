import unittest
import solver
import numpy as np
import mdp

class Test(unittest.TestCase):

    def test_pca(self):
        #Create sample data
        var1 = np.random.normal(loc=0., scale=0.5, size=(10,5))
        var2 = np.random.normal(loc=4., scale=1., size=(10,5))
        var = np.concatenate((var1,var2), axis=0)
        pcan = mdp.nodes.PCANode(output_dim=3)
        pcar = pcan.execute(var)

        print var
        print pcar

    def test(self):
        A = np.matrix('1 2; 3 4')
        b = np.matrix('5;6')
        print A
        print b
        x = np.linalg.solve(A,b)
        print x

        #print np.random.random((5,2))
    pass

if __name__ == '__main__':
    unittest.main()
