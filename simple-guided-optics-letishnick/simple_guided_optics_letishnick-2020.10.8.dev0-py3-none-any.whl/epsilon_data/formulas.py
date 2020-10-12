    ## Material library
def get_epsr_value(lam, material):

#TODO there have to be checks that lambda range is in the corresponding formula range

        if material=='si' or material=='silicon':
            lam1 = 1.1071
            eps = 1.165858e1; A = 9.39816e-1; B = 8.10461e-3
            epsr = eps + A/lam**2 + B*lam**2/(lam**2-lam1**2)

        if material=='si-const':
            epsr = np.empty((self._points))
            epsr.fill(3.4757**2)

        if material=='si-li':
            epsilon_Si_data_file = sync_path + \
                                        '/LinOpt/epsilon_datas/Si_Li-293K.csv'
            epsilon_Si = np.genfromtxt(epsilon_Si_data_file,
                                        skip_header=1, delimiter=',')

            lam_Si_data=epsilon_Si[:,0]
            n_Si_data = epsilon_Si[:,1]

            epsr = interp_tonew_x(lam_Si_data, lam, n_Si_data, self._points)**2

        if material=='si-lorentz':
            eps = 7.9874; eps_lorentz = 3.6880; w0 = 3.0328e15; d0 = 0
            epsr = eps + eps_lorentz*w0**2 / \
                   (w0**2 - 2j*d0*2*pi*c_umps/lam - (2*pi*c_umps/lam)**2)

        if material=='si-herzberger':
            A = 3.41906; B = 1.23172e-1; C = 2.65456e-2; D = -2.66511e-8;
            E = 5.45852e-14
            L = 1/(lam**2-0.028)
            epsr = (A + B*L + C*L**2 + D*lam**2 + E*lam**4)**2

        if material=='sio2':
            epsr = 1 + 0.6961663/(1-(0.0684021/lam)**2) + \
                       0.4079426/(1-(0.1162414/lam)**2) + \
                       0.8974794/(1-(9.8961610/lam)**2)

        if material=='sio2-const':
            epsr = 1.444**2 * np.ones((self._points))

        if material=='si3n4':
            epsr = 1 + 3.0249*lam**2/(lam**2-0.1353406**2) + \
                        40314*lam**2/(lam**2-1239.8420**2)

#             if material=='core-manual-epsr':
#                 epsr = self.substrate_epsr
# 
#             if material=='core-manual-n':
#                 epsr = self.substrate_n**2

        return epsr