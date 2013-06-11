"""
We implement local search in matrix form.

We want to solve for Ax =b, where A is our weight matrix, b is our truth, and x is our fixture configuration.

A - 169 x 88 matrix. A(i,j) = how much affect fixture j has on sensor i (at dimming level 1). Matrix A remains constant throughout the iterations.

b - 169 x 1 matrix. Holds the records sensor readings.

x - 88 x 1 matrix. Our fixture configuration

First, use PCA to reduce our A matrix to 88*88, and out b to 88*1.
We can use the mdp module.
"""
import numpy
from matplotlib.mlab import PCA

# s = '.69 .49;-1.31 -1.21; .39 .99; .09 .29; 1.29 1.09; .49 .79; .19 -.31; -.81 -.81;-.31 -.31;-.71 -1.01'
# m = numpy.matrix(s)

# mt = m.transpose()
# mcov = numpy.cov(mt)
# print mcov
 
# eigval,eigvect = numpy.linalg.eig(mcov)
# print eigval
# print eigvect

# print eigvect[:,-1]

def eigenspace(m,d):
    """
    Returns an eigenspace of the d most dominant eigenvectors of m. 
    """
    assert d > 0
    mcov = numpy.cov(m)
    eigenValues,eigenVectors = numpy.linalg.eig(mcov)
    #sort eigenvalues from largest to smallest
    idx = eigenValues.argsort()[::-1]
    eigenValues = eigenValues[idx]
    eigenVectors = eigenVectors[:,idx]
    print eigenVectors
    #select the d most prominent eigenvectors
    return eigenVectors[:,0:d]
