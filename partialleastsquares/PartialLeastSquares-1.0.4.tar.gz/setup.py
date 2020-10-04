#!/usr/bin/env python

## setup.py

from setuptools import setup, find_packages
import sys, os

setup(name='PartialLeastSquares',
      version='1.0.4',
      author='Avinash Kak',
      author_email='kak@purdue.edu',
      maintainer='Avinash Kak',
      maintainer_email='kak@purdue.edu',
      url='https://engineering.purdue.edu/kak/distPLS/PartialLeastSquares-1.0.4.html',
      download_url='https://engineering.purdue.edu/kak/distPLS/PartialLeastSquares-1.0.4.tar.gz',
      description='A Python module for regression and classification with the Partial Least Squares algorithm',
      long_description=''' 

Consult the module API page at

    https://engineering.purdue.edu/kak/distPLS/PartialLeastSquares-1.0.4.html

for all information related to this module, including that related to the
latest changes to the code.  The page at the URL shown above lists all of the
module functionality you can invoke in your own code.

You may need this module if (1) you are trying to make multidimensional
predictions from multidimensional observations; (2) the dimensionality of
the observation space is large; and (3) the data you have available for
constructing a prediction model is rather limited.  The more traditional
multiple linear regression (MLR) algorithms are likely to become
numerically unstable under these conditions.

In addition to presenting an implementation of the main Partial Least
Squares (PLS) algorithm that can be used to make a multidimensional
prediction from a multidimensional observation, this module also includes
what is known as the PLS1 algorithm for the case when the predicted entity
is just one-dimensional (as in, say, face recognition in computer vision).

Typical usage syntax:

::

        In the notation that is typically used for describing PLS, X
        denotes the matrix formed by multidimensional observations, with
        each row of X standing for the values taken by all the predictor
        variables.  And Y denotes the matrix formed by the values for the
        predicted variables. Each row of Y corresponds to the prediction
        that can be made on the basis of the corresponding row of X.  Let's
        say that you have some previously collected data for the X and Y
        matrices in the form of CSV records in disk files. Given these X
        and Y, you would want to calculate the matrix B of regression
        coefficients with this module.  Toward that end, you can make the
        following calls in your script:

            import PartialLeastSquares as PLS

            XMatrix_file = "X_data.csv"
            YMatrix_file = "Y_data.csv"

            pls = PLS.PartialLeastSquares(
                    XMatrix_file =  XMatrix_file,
                    YMatrix_file =  YMatrix_file,
                    epsilon      = 0.0001,
                  )
           pls.get_XMatrix_from_csv()
           pls.get_YMatrix_from_csv()
           B = pls.PLS()

        The object B returned by the last call will be a numpy matrix
        consisting of the calculated regression coefficients.  Let's say
        that you now have a matrix Xtest of new data for the predictor
        variables.  All you have to do to calculate the values for the
        predicted variables is

           Ytest  =  (Xtest - pls.mean0X) * B  +  pls.mean0Y

        where pls.mean0X is the column-wise mean of the X matrix and
        pls.mean0Y the same for the Y matrix.  

          ''',

      license='Python Software Foundation License',
      keywords='classification, regression, data dimensionality reduction',
      platforms='All platforms',
      classifiers=['Topic :: Scientific/Engineering :: Information Analysis', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.8'],
      packages=['PartialLeastSquares']
)
