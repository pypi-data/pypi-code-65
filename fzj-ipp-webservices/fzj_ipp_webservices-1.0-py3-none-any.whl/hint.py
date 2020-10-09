from . import inputs
import netCDF4
import numpy as np
import warnings
import scipy.io

def from_hint_netcdf(filename, name = 'HINT', desc = None):
	with netCDF4.Dataset(filename) as f:
		m_tor = f.variables['mtor'][...].item();
		rminb = f.variables['rminb'][...].item();
		rmaxb = f.variables['rmaxb'][...].item();
		zminb = f.variables['zminb'][...].item();
		zmaxb = f.variables['zmaxb'][...].item();
		
		if 'Bv_phi' in f.variables:
			warnings.warn('Loading vacuum file, v and p will be set to zero')
		
			b_field = np.stack(
				[
					f.variables['Bv_phi'][...],
					f.variables['Bv_Z'][...],
					f.variables['Bv_R'][...]
				],
				axis = 0
			);
			
			v_field = np.zeros(b_field   .shape, dtype = np.float32)
			p_field = np.zeros(b_field[0].shape, dtype = np.float32)
			
		else:
			b_field = np.stack(
				[
					f.variables['B_phi'][...],
					f.variables['B_Z'][...],
					f.variables['B_R'][...]
				],
				axis = 0
			);
			
			v_field = np.stack(
				[
					f.variables['v_phi'][...],
					f.variables['v_Z'][...],
					f.variables['v_R'][...]
				],
				axis = 0
			);
			
			p_field = f.variables['P'][...];
		
		return from_hint(
			name,
			b_field, p_field, v_field,
			rminb, rmaxb, zminb, zmaxb,
			m_tor,
			*(p_field.shape)
		);

def from_hint_snapfile(filename, name = 'HINT', desc = None, big_endian = True, real_bytes = 8):
	warnings.warn('Loading of HINT snapfiles has not been tested');
	
	# Define types
	if big_endian:
		int_type = '>i4';
		real_type = '>f{}'.format(real_bytes);
		header_type = '>u4';
	else:
		int_type = 'i4';
		real_type = 'f{}'.format(real_bytes);
		header_type = 'u4';

	# Read data from fortran file
	f = scipy.io.FortranFile(filename, 'r', header_dtype = header_type);

	kstep = f.read_ints(int_type);
	time  = f.read_reals(real_type);
	n_r, n_z, n_p, m_tor = f.read_ints(int_type);
	r_min, z_min, r_max, z_max = f.read_reals(real_type);

	b_field = f.read_reals(real_type);
	b_field = b_field.reshape([n_p, n_z, n_r, 3]);
	b_field = b_field.transpose([3, 0, 1, 2]);

	v_field = f.read_reals(real_type);
	v_field = v_field.reshape([n_p, n_z, n_r, 3]);
	v_field = v_field.transpose([3, 0, 1, 2]);

	p_field = f.read_reals(real_type);
	p_field = p_field.reshape([n_p, n_z, n_r]);
	
	# Convert from r, phi, z to phi, z, r component order
	b_field = b_field[[1, 2, 0]];
	v_field = v_field[[1, 2, 0]];

	f.close();
	
	return from_hint(
		name,
		b_field, p_field, v_field,
		r_min, r_max, z_min, z_max,
		m_tor,
		n_p, n_z, n_r
	);

def from_hint(name, b_field, p_field, v_field, r_min, r_max, z_min, z_max, m_tor, n_phi, n_z, n_r, desc = None):
	assert b_field.shape == (3, n_phi, n_z, n_r);
	assert p_field.shape == (   n_phi, n_z, n_r);
	
	mu_0 = 4e-7 * np.pi;
	
	grid = inputs.CylindricalGrid(
		r_min = r_min,
		r_max = r_max,
		z_min = z_min,
		z_max = z_max,
		n_sym = m_tor,
		n_r = n_r,
		n_phi = n_phi,
		n_z = n_z
	);
	
	# Magnetic fields have to be transposed from (Phi, z, r) indexing (HINT) to (Phi, r, z) (Webservice)
	b_field = np.transpose(b_field, [0, 1, 3, 2]);
	p_field = np.transpose(p_field, [0, 2, 1]);
	v_field = np.transpose(v_field, [0, 1, 3, 2]);
	
	b_field = b_field[[0, 2, 1]];
	p_field = p_field * (1 / mu_0); # Divide p 
	
	beta = p_field / (np.linalg.norm(b_field, axis = 0)**2 / (2 * mu_0));
	
	if desc is None:
		desc = 'HINT equilibrium with beta={:02.2%}'.format(np.amax(beta));
	
	b_field = np.ascontiguousarray(b_field);
	p_field = np.ascontiguousarray(p_field);
	v_field = np.ascontiguousarray(v_field);
	
	return inputs.PredefinedField(
		grid,
		b_field,
		name,
		desc
	), p_field, v_field;