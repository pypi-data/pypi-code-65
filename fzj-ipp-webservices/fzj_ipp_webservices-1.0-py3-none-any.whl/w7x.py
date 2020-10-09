import warnings
import numpy as np
import functools

from . import inputs
from . import w7x_archive
from . import client

module_version = 1

def unstable_api(valid = [module_version]):
	def wrap(f):
		@functools.wraps(f)
		def func(*args, version = None, **kwargs):
			if version is None:
				warnings.warn('The W7-X function ' + f.__name__  + ' has unstable API, and no version argument is specified')
			else:
				assert version in valid, 'The requested API version ({}) can not be provided by the current version ({})'.format(version, module_version)
		
			return f(*args, **kwargs)
		
		return func
	
	return wrap

def stable_api(valid = [module_version]):
	def wrap(f):
		@functools.wraps(f)
		def func(*args, version = None, **kwargs):
			if version is not None:
				assert version in valid, 'The requested API version ({}) can not be provided by the current version ({})'.format(version, module_version)
		
			return f(*args, **kwargs)
		
		return func
	
	return wrap

def internal(f):
	@functools.wraps(f)
	def func(*args, version = None, **kwargs):
		if version is not None:
			assert version == module_version, 'The requested internal function for version ({}) can not be provided by the current version ({})'.format(version, module_version)
	
		return f(*args, **kwargs)
	
	return func

@internal
def _interpolate_configs(grid, key):
	keys = sorted(list(grid))
	
	if key <= keys[0]:
		return grid[keys[0]]
	
	if key >= keys[-1]:
		return grid[keys[-1]]
	
	for i in range(len(keys) - 1):
		k1 = keys[i]
		k2 = keys[i+1]
		
		if k1 <= key and key <= k2:
			l = (k2 - key) / (k2 - k1)
			
			return l * grid[k1] + (1 - l) * grid[k2]	

@internal
def _estimate_b0(i_12345, i_ab):
	contrib_np = np.mean(i_12345) / 15000 * 2.72
	contrib_p  = np.mean(i_ab) / 9166.67 * (2.45 - 12.22222 / 15 * 2.72)
	
	return abs(contrib_np + contrib_p)


coil_conventions = ['coilsdb', '1-AA-R0004.5', 'archive'];

@stable_api()
def process_coil_convention(convention):
	assert convention in coil_conventions,  'Invalid coil convention {}, must be one of {}'.format(convention, coil_conventions);
	
	if convention == 'archive':
		return '1-AA-R0004.5';
	
	return convention;


cartesian_grid = inputs.CartesianGrid(
	x_min = -7, x_max = 7, n_x = 500,
	y_min = -7, y_max = 7, n_y = 500,
	z_min = -1.5, z_max = 1.5, n_z = 100
);

cylindrical_grid = inputs.CylindricalGrid(
	r_min = 4.05, r_max = 6.75, n_r = 181,
	z_min = -1.35, z_max = 1.35, n_z = 181,
	n_sym = 5, n_phi = 96
);

nonsym_grid = inputs.CylindricalGrid(
	r_min = 4.05, r_max = 6.75, n_r = 181,
	z_min = -1.35, z_max = 1.35, n_z = 181,
	n_sym = 1, n_phi = 96
);

@stable_api()
def base_coils(name, coils, i_12345 = [0] * 5, i_ab = [0] * 2, desc = None, grid = cylindrical_grid, convention = '1-AA-R0004.5'):
	if desc is None:
		desc = '{name} - {inp} (nonplanar) - {ip} (planar)'.format(inp = i_12345, ip = i_ab, name = name);
	
	# Multiply by coil windings
	i_12345 = [i * 108 for i in i_12345];
	i_ab    = [i * 36  for i in i_ab];
	
	return inputs.BiotSavartField(
		coilsdb_coils = list(coils),
		coilsdb_currents = i_12345 * 10 + i_ab * 10,
		name = name,
		desc = desc,
		grid = grid
	);

@stable_api()
def three_letters(name, field):
	return '{}{:+04d}'.format(name, int(field * 100));

@stable_api()
def cad_coils(i_12345 = [0] * 5, i_ab = [0] * 2, name = 'CAD coils', desc = None, grid = cylindrical_grid, convention = '1-AA-R0004.5'):
	assert len(i_12345) == 5;
	assert len(i_ab) == 2;
	
	convention = process_coil_convention(convention);
	
	def neg(x):
		return [-i for i in x];
		
	# Correct for inconsistent winding of CAD coils
	if convention == '1-AA-R0004.5':
		i_12345 = neg(i_12345);
		i_ab = neg(i_ab);
	
	result = base_coils(
		name,
		range(160,230),
		i_12345 = i_12345,
		i_ab = i_ab,
		desc = desc,
		grid = grid
	);
	
	result.desc += ' (CAD)';
	
	return result

@unstable_api()
def loaded_coils_standard(i_12345 = [0] * 5, i_ab = [0] * 2, name = 'Loaded coils standard', desc = 'Loaded coils standard', grid = nonsym_grid, convention = '1-AA-R0004.5'):
	assert len(i_12345) == 5;
	assert len(i_ab) == 2;
	
	convention = process_coil_convention(convention)
	
	result = base_coils(
		name,
		range(1362, 1432),
		i_12345 = i_12345,
		i_ab = i_ab,
		desc = desc,
		grid = grid
	);
	
	b0 = _estimate_b0(i_12345, i_ab)
	if abs(b0 - 2.5) > 0.1:
		warnings.warn('Loaded coils for standard config. only known for B0 = 2.5T, B0 is {:.2f}T'.format(b0))
	
	result.desc += ' (2.5T)';
	
	return result;

@unstable_api()
def loaded_coils_high_iota(i_12345 = [0] * 5, i_ab = [0] * 2, name = 'Loaded coils high-iota', desc = 'Loaded coils high-iota', grid = nonsym_grid, convention = '1-AA-R0004.5'):
	assert len(i_12345) == 5;
	assert len(i_ab) == 2;
	
	def config(coils, b):
		return base_coils(
			name,
			coils,
			i_12345 = i_12345,
			i_ab = i_ab,
			desc = '{} ({:.1f})T'.format(desc, b),
			grid = grid
		)
	
	config_grid = {
		1.37 : config(range(1642, 1712), 1.37),
		2.02 : config(range(1712, 1782), 2.02),
		2.50 : config(range(1782, 1852), 2.50)
	}
	
	b0 = _estimate_b0(i_12345, i_ab)
	
	if b0 < 1.37:
		warnings.warn('No high-iota loaded coils registered for B0 < 1.37T, B0 is {:.2f}T'.format(b0))
	
	if b0 > 2.50:
		warnings.warn('No high-iota loaded coils registered for B0 > 2.50T, B0 is {:.2f}T'.format(b0))
	
	result = _interpolate_configs(
		config_grid,
		b0
	)
	result.desc = '(' + result.desc + ')'
	
	return result;

@unstable_api()
def loaded_coils_high_mirror(i_12345 = [0] * 5, i_ab = [0] * 2, name = 'Loaded coils high-mirror', desc = 'Loaded coils high-mirror', grid = nonsym_grid, convention = '1-AA-R0004.5'):
	assert len(i_12345) == 5;
	assert len(i_ab) == 2;
	
	def config(coils, b):
		return base_coils(
			name,
			coils,
			i_12345 = i_12345,
			i_ab = i_ab,
			desc = '{} ({:.1f})T'.format(desc, b),
			grid = grid
		)
	
	config_grid = {
		1.12 : config(range(1992, 2062), 1.12),
		1.85 : config(range(1922, 1992), 1.85),
		2.50 : config(range(1852, 1922), 2.50)
	}
	
	b0 = _estimate_b0(i_12345, i_ab)
	
	if b0 < 1.12:
		warnings.warn('No high-mirror loaded coils registered for B0 < 1.12T, B0 is {:.2f}T'.format(b0))
	
	if b0 > 2.50:
		warnings.warn('No high-mirror loaded coils registered for B0 > 2.50T, B0 is {:.2f}T'.format(b0))
	
	result = _interpolate_configs(
		config_grid,
		b0
	)
	result.desc = '(' + result.desc + ')'
	
	return result

@unstable_api()
def loaded_coils(i_12345 = [0] * 5, i_ab = [0] * 2, version = None, **kwargs):
	p_np_ratio = np.mean(i_ab) / np.mean(i_12345)
	p_np_hi = -10222.22 / 14814.81
	
	if p_np_ratio >= 0.1:
		warnings.warn('No loaded coil models are known for low-iota type configurations, using standard / high-mirror models')
	
	if p_np_ratio <= p_np_hi - 0.1:
		warnings.warn('No loaded coil models are known for higher iota than FTM, using high-iota models')
	
	# NP = 0 case is interpolation between standard and high-mirror
	def mirror_ratio(i_12345 = i_12345):
		return (np.max(i_12345) - np.min(i_12345)) / np.mean(i_12345)
		
	mratio = mirror_ratio()
	
	hmref = mirror_ratio([14400, 14000, 13333.33, 12666.67, 12266.67])
	mratio /= hmref
	
	if mratio > 1.1:
		warnings.warn('No loaded coil specs are known for higher mirror ratio than KJM')
	
	grid = {
		0 : loaded_coils_standard(i_12345, i_ab, version = module_version, **kwargs),
		1 : loaded_coils_high_mirror(i_12345, i_ab, version = module_version, **kwargs)
	}
	
	center_config = _interpolate_configs(
		grid,
		mratio
	)
	
	# High NP case is high iota
	grid = {
		0 : center_config,
		p_np_hi : loaded_coils_high_iota(i_12345, i_ab, version = module_version, **kwargs)
	}
	
	return _interpolate_configs(
		grid,
		p_np_ratio
	)

@stable_api()
def op12_standard(field = 2.72, coil_pack = cad_coils, grid = cylindrical_grid):
	a = field / 2.72;
	
	return coil_pack(
		i_12345 = [15000 * a] * 5,
		name = three_letters('EIM', field),
		desc = 'OP1.2 Standard',
		grid = grid
	);

@stable_api()
def op12_high_iota(field = 2.72, coil_pack = cad_coils, grid = cylindrical_grid):
	a = field / 2.43;
	
	return coil_pack(
		i_12345 = [14814.81 * a] * 5,
		i_ab    = [-10222.22 * a] * 2,
		name = three_letters('FTM', field),
		desc = 'OP1.2 High-Iota',
		grid = grid
	);

@stable_api()
def op12_low_iota(field = 2.72, coil_pack = cad_coils, grid = cylindrical_grid):
	a = field / 2.45;
	
	return coil_pack(
		i_12345 = [12222.22 * a] * 5,
		i_ab    = [9166.67 * a] * 2,
		name = three_letters('DBM', field),
		desc = 'OP1.2 High-Iota',
		grid = grid
	);

@stable_api()
def op12_high_mirror(field = 2.72, coil_pack = cad_coils, grid = cylindrical_grid):
	a = field / 2.3;
	
	return coil_pack(
		i_12345 = [13000, 13260, 14040, 12090, 10959],
		i_ab    = [0] * 2,
		name = three_letters('KJM001', field),
		desc = 'OP1.2 High-Mirror',
		grid = grid
	);

@stable_api()
def trim_coils(
	currents = [0] * 5,
	coil_list = [350, 241, 351, 352, 353],
	winding_numbers = [48, 72, 48, 48, 48],
	convention = '1-AA-R0004.5'
):
	convention = process_coil_convention(convention);
	
	currents = np.asarray(currents) * winding_numbers;
	
	return inputs.BiotSavartField(
		coilsdb_coils = coil_list,
		coilsdb_currents = list(currents),
		name = 'TC',
		desc = 'TC'
	);

@stable_api()
def control_coils(
	currents = [0] * 10,
	coil_list = list(range(230, 240)),
	winding_numbers = [8] * 10,
	convention = '1-AA-R0004.5'
):
	convention = process_coil_convention(convention);
	
	currents = np.asarray(currents) * winding_numbers;
	
	if convention == '1-AA-R0004.5':
		# In the archive, all control coil currents are counter-clock-wise, when viewed from outside
		# In 1-AA-R0004.5, the lower coils are clock-wise (the upper ones are counter-clockwise)
		# The odd indices (231, 233, ...) correspond to the lower coils and have to be inverted
		currents = currents * np.asarray([1, -1] * 5);
	
	return inputs.BiotSavartField(
		coilsdb_coils = coil_list,
		coilsdb_currents = list(currents),
		name = 'CC',
		desc = 'CC'
	);

@unstable_api()
def config_from_program(program_id, coil_pack = None, iota_correct = False, plasma_current = False, **kwargs):
	if plasma_current:
		warnings.warn('Currently plasma_current = True uses the average plasma current, which makes little sense. Consider adding the wanted axis current manually')
	
	if coil_pack is None:
		coil_pack = cad_coils if iota_correct else loaded_coils
		
	currents = w7x_archive.getCoilCurrents(program_id)
	
	if iota_correct:
		ic_currents = w7x_archive.getIotaCorrectedCoilCurrents(program_id)
		
		for k in ic_currents:
			currents[k] = ic_currents[k]
	
	i_12345 = [
		currents['nonplanar {}'.format(i)]
		for i in [1, 2, 3, 4, 5]
	]
	
	i_ab = [
		currents['planar {}'.format(i)]
		for i in ['A', 'B']
	]
	
	i_trim = [
		currents['trim {}'.format(i)]
		for i in [1, 2, 3, 4, 5]
	]
	
	i_control = [
		currents['sweep {}'.format(i)]
		for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	]
		
	base_config = coil_pack(i_12345, i_ab) + trim_coils(i_trim) + control_coils(i_control)
	
	if plasma_current:
		base_config += client.axis_current(base_config, currents['I plasma'])
	
	return base_config
	

calculation_boundary = inputs.PartList(parts = [164], name = 'Boundary', grid = cartesian_grid);
op12_divertor        = inputs.PartList(parts = range(165, 170), name = 'OP1.2 TDU');
op12_baffles         = inputs.PartList(parts = range(320, 325), name = 'Baffles');
op12_covers          = inputs.PartList(parts = range(325, 330), name = 'Baffle Covers');
op12_heat_shield     = inputs.PartList(parts = range(330, 335), name = 'Heat Shield');

op12_pump_slit       = inputs.PartList(parts = range(450, 455), name = 'Pump Slit');

steel_panels         = inputs.PartList(assemblies = [8], name = 'Steel Panels');
plasma_vessel        = inputs.PartList(assemblies = [9], name = 'Plasma Vessel');

op11_divertor_cover  = inputs.PartList(assemblies = [13], name = 'OP1.1 TDU Cover');
op11_hs_sygraflex    = inputs.PartList(assemblies = [14], name = 'OP1.1 Heat Shield Sygraflex');
op11_limiter         = inputs.PartList(assemblies = [21], name = 'OP1.1 Limiter');

parts_op12 = calculation_boundary + op12_divertor + op12_baffles + op12_covers + op12_heat_shield + op12_pump_slit + plasma_vessel + steel_panels;
parts_op11 = calculation_boundary + op11_divertor_cover + op11_hs_sygraflex + op11_limiter + plasma_vessel + steel_panels;