# Copyright (c) 2020 Dimitrios-Georgios Akestoridis
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import numpy as np


def mtopsis(z_matrix, w_vector, is_benefit_z):
    """Python implementation of the mTOPSIS scoring method.

    For more information, see the following publication:
      * H. Deng, C.-H. Yeh, and R. J. Willis, "Inter-company comparison using
        modified TOPSIS with objective weights," Computers & Operations
        Research, vol. 27, no. 10, pp. 963--973, 2000.
        DOI: 10.1016/S0305-0548(99)00069-6.
    """
    # Make sure that the decision matrix is a float64 NumPy array
    z_matrix = np.array(z_matrix, dtype=np.float64)

    # Make sure that the weight vector is a float64 NumPy array
    w_vector = np.array(w_vector, dtype=np.float64)

    # Sanity checks
    if (np.sum(np.less(z_matrix, 0.0)) > 0
            or np.sum(np.greater(z_matrix, 1.0)) > 0):
        raise ValueError("The decision matrix must be normalized "
                         "in order to apply the mTOPSIS scoring method")
    elif w_vector.shape != (z_matrix.shape[1],):
        raise ValueError("The shape of the weight vector is not "
                         "appropriate for the number of columns in the "
                         "decision matrix")
    elif not np.isclose(np.sum(w_vector), 1.0):
        raise ValueError("The weight vector's elements must sum to 1")
    elif len(is_benefit_z) != z_matrix.shape[1]:
        raise ValueError("The number of variables in the list that "
                         "determines whether each criterion is a benefit "
                         "or a cost criterion does not match the number "
                         "of columns in the decision matrix")

    # mTOPSIS scores should always be sorted in descending order
    desc_order = True

    # Derive the positive and negative ideal solutions
    pos_ideal_sol = np.zeros(z_matrix.shape[1], dtype=np.float64)
    neg_ideal_sol = np.zeros(z_matrix.shape[1], dtype=np.float64)
    for j in range(z_matrix.shape[1]):
        if is_benefit_z[j]:
            pos_ideal_sol[j] = np.amax(z_matrix[:, j])
            neg_ideal_sol[j] = np.amin(z_matrix[:, j])
        else:
            pos_ideal_sol[j] = np.amin(z_matrix[:, j])
            neg_ideal_sol[j] = np.amax(z_matrix[:, j])

    # Compute the score of each alternative
    s_vector = np.zeros(z_matrix.shape[0], dtype=np.float64)
    for i in range(z_matrix.shape[0]):
        pos_ideal_dist = 0.0
        neg_ideal_dist = 0.0
        for j in range(z_matrix.shape[1]):
            pos_ideal_dist += (w_vector[j]
                               * (pos_ideal_sol[j] - z_matrix[i, j])**2)
            neg_ideal_dist += (w_vector[j]
                               * (z_matrix[i, j] - neg_ideal_sol[j])**2)
        pos_ideal_dist = np.sqrt(pos_ideal_dist)
        neg_ideal_dist = np.sqrt(neg_ideal_dist)
        s_vector[i] = neg_ideal_dist / (neg_ideal_dist + pos_ideal_dist)

    return s_vector, desc_order
