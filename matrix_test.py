import unittest
import matrix_ls as mls
import numpy

class Test(unittest.TestCase):
    
    def test_eigenspace(self):
        m = numpy.random.randn(5,3)
        d = 2
        print mls.eigenspace(m,d)


if __name__ == '__main__':
    unittest.main()
