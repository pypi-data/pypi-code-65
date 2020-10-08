# import numpy as np
# import mccd.auxiliary_fun as mccd_aux
# import mccd
# from astropy.io import fits
#
# # Generate the dataset
# input_pos_path = './../data/sim_inputs/train_positions.npy'
# input_ccd_path = './../data/sim_inputs/train_ccd_list.npy'
# output_path = './../data/mccd_inputs/'
#
# """
# sim_dataset_generator = mccd_aux.GenerateSimDataset(input_pos_path,
#                                                     input_ccd_path,
#                                                     output_path)
#
# sim_dataset_generator.load_data()
# # Posibility to define the simulation parameters
# sim_dataset_generator.generate_train_data()  # Using default parameters
# # Defining the testing grid
# sim_dataset_generator.generate_test_data(x_grid=5, y_grid=10)
# """
#
#
# # Get the dataset paths
# ext = '.fits'
# # catalog_id = sim_dataset_generator.catalog_id
# catalog_id = 2086592
#
# train_cat_path = output_path + 'train_star_selection-' + str(catalog_id) + ext
# test_cat_path = output_path + 'test_star_selection-' + str(catalog_id) + ext
#
#
#
# # Load the data
# train_cat = fits.open(train_cat_path)
#
# # Extract the data from the fits catalog
# positions = np.copy(train_cat[1].data['GLOB_POSITION_IMG_LIST'])
# stars = np.copy(train_cat[1].data['VIGNET_LIST'])
# ccds = np.copy(train_cat[1].data['CCD_ID_LIST']).astype(int)
# ccds_unique = np.unique(np.copy(train_cat[1].data['CCD_ID_LIST'])).astype(int)
# # Generate the masks
# masks = mccd.utils.handle_SExtractor_mask(stars,thresh=-1e5)
#
# # Generate the list format needed by the MCCD package
# pos_list = [positions[ccds == ccd] for ccd in ccds_unique]
# star_list = [mccd.utils.rca_format(stars[ccds == ccd]) for ccd in ccds_unique]
# mask_list = [mccd.utils.rca_format(masks[ccds == ccd]) for ccd in ccds_unique]
# ccd_list = [ccds[ccds == ccd].astype(int) for ccd in ccds_unique]
# ccd_list = [np.unique(_list)[0].astype(int) for _list in ccd_list]
# SNR_weight_list = None  # We wont use any weighting technique as the SNR is constant over the Field of View

#
# # Parameters
#
# # MCCD instance
# n_comp_loc = 8
# d_comp_glob = 3
# filters = None
# ksig_loc = 1.
# ksig_glob = 1.
#
# # MCCD fit
# psf_size = 1.75
# psf_size_type = 'sigma'
# n_eigenvects = 5
# n_iter_rca = 1
# nb_iter_glob = 2
# nb_iter_loc = 2
# nb_subiter_S_loc = 100
# nb_subiter_A_loc = 500
# nb_subiter_S_glob = 30
# nb_subiter_A_glob = 200
# loc_model = 'hybrid'
#
#
# # Build the paramter dictionaries
# mccd_inst_kw = {'n_comp_loc': n_comp_loc, 'd_comp_glob': d_comp_glob,
#                 'filters': filters,       'ksig_loc': ksig_loc,
#                 'ksig_glob':ksig_glob}
#
# mccd_fit_kw = {'psf_size': psf_size,                  'psf_size_type':psf_size_type,
#               'n_eigenvects': n_eigenvects,          'nb_iter':n_iter_rca,
#               'nb_iter_glob':nb_iter_glob,           'nb_iter_loc':nb_iter_loc,
#               'nb_subiter_S_loc':nb_subiter_S_loc,   'nb_subiter_A_loc':nb_subiter_A_loc,
#               'nb_subiter_S_glob':nb_subiter_S_glob, 'nb_subiter_A_glob':nb_subiter_A_glob,
#               'loc_model':loc_model}
#
#
#
# # Instanciate the class
# mccd_instance = mccd.MCCD(**mccd_inst_kw, verbose=True)
# # Launch the training
# S, A_loc, A_glob, alpha, pi = mccd_instance.fit(star_list, pos_list, ccd_list, mask_list,
#                                                 SNR_weight_list, **mccd_fit_kw)
#
# fitted_model_path = output_path + '/fitted_model' + catalog_id
# mccd_instance.quicksave(filefitted_model_pathname)
