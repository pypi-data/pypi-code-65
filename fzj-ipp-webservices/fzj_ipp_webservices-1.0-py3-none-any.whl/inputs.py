import osa
import copy
import json
import hashlib
import numpy as np
import scipy.interpolate

class DataObject:
	def __eq__(self, other):
		return vars(self) == vars(other);
	
	def __hash__(self):
		def do_hash(x):
			try:
				return x.__dict__;
			except:
				pass;
			
			h = hashlib.sha1();
			h.update(x);
			return h.hexdigest();
		
		s = json.dumps(
			self,
			default=do_hash, 
            sort_keys=True
		);
		
		return hash(s);

class CylindricalGrid(DataObject):
	def __init__(
		self,
		r_min = 0, r_max = 0, n_r = 0,
		z_min = 0, z_max = 0, n_z = 0,
		n_sym = 5, n_phi = 30
	):
		self.r_min = r_min;
		self.r_max = r_max;
		self.n_r   = n_r;
		
		self.z_min = z_min;
		self.z_max = z_max;
		self.n_z   = n_z;
		
		self.n_sym = n_sym;
		self.n_phi = n_phi;
		
	def interpolate(self, input, points_phi_r_z, axes_phi_r_z = [0, 1, 2]):
		points_phi_r_z = np.asarray(points_phi_r_z);

		points_phi_r_z[0] = points_phi_r_z[0] % (2 * np.pi / self.n_sym);

		ax_phi = np.linspace(0, 2 * np.pi / self.n_sym, self.n_phi, endpoint=False);
		ax_r   = np.linspace(self.r_min, self.r_max, self.n_r);
		ax_z   = np.linspace(self.z_min, self.z_max, self.n_z);

		return scipy.interpolate.interpn(
			(ax_phi, ax_r, ax_z),
			np.moveaxis(input, axes_phi_r_z, [0, 1, 2]),
			np.moveaxis(points_phi_r_z, 0, -1),
			method = 'linear',
			bounds_error = True
		);
	
	def __eq__(self, other):
		return (
			self.r_min == other.r_min and
			self.r_max == other.r_max and
			self.n_r   == other.n_r and
			
			self.z_min == other.z_min and
			self.z_max == other.z_max and
			self.n_z   == other.n_z and
			
			self.n_sym == other.n_sym and
			self.n_phi == other.n_phi
		)

class CartesianGrid(DataObject):
	def __init__(self,
		x_min = 0, x_max = 0, n_x = 0,
		y_min = 0, y_max = 0, n_y = 0,
		z_min = 0, z_max = 0, n_z = 0
	):
		self.x_min = x_min;
		self.x_max = x_max;
		self.n_x = n_x;
		
		self.y_min = y_min;
		self.y_max = y_max;
		self.n_y = n_y;
		
		self.z_min = z_min;
		self.z_max = z_max;
		self.n_z = n_z;
	
class BiotSavartField(DataObject):
	def __init__(self,
		coilsdb_coils = [],
		coilsdb_currents = [],
		coilsdb_configs = [],
		custom_coils = [],
		custom_currents = [],
		inverse = False,
		grid = None,
		name = None,
		desc = ''
	):
		assert grid is None or isinstance(grid, CylindricalGrid);
		
		self.coilsdb_coils = coilsdb_coils;
		self.coilsdb_currents = coilsdb_currents;
		self.coilsdb_configs  = coilsdb_configs;
		self.custom_coils = custom_coils;
		self.custom_currents = custom_currents;
		self.inverse = inverse;
		self.grid = grid;
		self.name = name;
		self.desc = desc;
	
	def _flip(self):
		"""
		Creates logically equivalent field with inverse and current signs flipped
		"""
		assert not self.coilsdb_configs, 'Can not flip field with pre-defined config';
		
		def neg(a):
			return [-x for x in a]
		
		return BiotSavartField(
			self.coilsdb_coils,
			neg(self.coilsdb_currents),
			[],
			self.custom_coils,
			neg(self.custom_currents),
			not self.inverse,
			self.grid,
			self.name,
			self.desc
		);
		
	def __add__(self, other):
		new_grid = self.grid if self.grid is not None else other.grid;
		new_name = self.name if self.name is not None else other.name;
		
		if self.inverse != other.inverse:
			assert not (self.coilsdb_configs and other.coilsdb_configs), 'Can not add an inverted and a non-inverted configuration that both contain CoilsDB configs'
			
			if other.coilsdb_configs:
				return other + self
			
			other = other._flip();
		
		return BiotSavartField(
			self.coilsdb_coils + other.coilsdb_coils,
			self.coilsdb_currents + other.coilsdb_currents,
			self.coilsdb_configs + other.coilsdb_configs,
			self.custom_coils + other.custom_coils,
			self.custom_currents + other.custom_currents,
			self.inverse,
			new_grid,
			new_name,
			self.desc + ' + ' + other.desc
		);
	
	def __iadd__(self, other):
		self.grid = self.grid if self.grid is not None else other.grid;
		self.name = self.name if self.name is not None else other.name;
		
		if self.inverse != other.inverse:
			other = other._flip();
		
		self.coilsdb_coils = self.coilsdb_coils + other.coilsdb_coils;
		self.coilsdb_currents = self.coilsdb_currents + other.coilsdb_currents;
		self.coilsdb_configs = self.coilsdb_configs + other.coilsdb_configs;
		self.custom_coils = self.custom_coils + other.custom_coils;
		self.custom_currents = self.custom_currents + other.custom_currents;
		self.desc = self.desc + ' + ' + other.desc;
		
		return self;
	
	def __neg__(self):
		return BiotSavartField(
			self.coilsdb_coils,
			self.coilsdb_currents,
			self.coilsdb_configs,
			self.custom_coils,
			self.custom_currents,
			not self.inverse,
			self.grid,
			self.name,
			self.desc + ', reversed'
		);
	
	def __mul__(self, other):		
		assert not self.coilsdb_configs, 'Can not scale field with pre-defined config';
		
		return BiotSavartField(
			self.coilsdb_coils,
			[c * other for c in self.coilsdb_currents],
			self.coilsdb_configs,
			self.custom_coils,
			[c * other for c in self.custom_currents],
			self.inverse,
			self.grid,
			self.name,
			self.desc + ' * ' + str(other)
		);
	
	def __rmul__(self, other):
		return self.__mul__(other)
	
	def __imul__(self, other):
		assert not self.coilsdb_configs, 'Can not scale field with pre-defined config';
		
		self.coilsdb_currents = [
			c * other for c in self.coilsdb_currents
		]

		self.custom_currents = [
			c * other for c in self.custom_currents
		]
		
		return self
		
class PredefinedField(DataObject):
	def __init__(self,
		grid,
		field,
		name = '',
		desc = '',
		inverse = False
	):
		"""
		
		Args:
			field: [3, grid.n_phi, grid.n_r, grid.n_z] numpy array-like with field in (Phi, r, z) components.
		"""
		self.grid = grid;
		self.field = field;
		self.name = name;
		self.desc = desc;
		self.inverse = inverse;
	
	def __neg__(self):
		return PredefinedField(
			self.grid,
			self.field,
			self.name,
			self.desc + ', reversed',
			not self.inverse
		);
	
	def __eq__(self, other):
		if not isinstance(other, PredefinedField):
			return False;
		
		if self.grid != other.grid:
			return False;
		
		if self.inverse != other.inverse:
			return False;
		
		if self.name != other.name:
			return False;
		
		if self.desc != other.desc:
			return False;
		
		if (self.field != other.field).any():
			return False;
		
		return True;
	
	def __hash__(self):
		def do_hash(x):
			try:
				return x.__dict__;
			except:
				pass;
			
			h = hashlib.sha1();
			h.update(x);
			return h.hexdigest();
		
		s = json.dumps(
			self,
			default=do_hash, 
            sort_keys=True
		);
		
		return hash(s);
	
	def __add__(self, other):
		assert self.grid == other.grid
		
		ofield = other.field if self.inverse == other.inverse else -other.field
		
		return PredefinedField(
			self.grid,
			self.field + ofield,
			self.name,
			self.desc + ' + ' + other.desc
		)
	
	def __mul__(self, other):
		return PredefinedField(
			self.grid,
			self.field * other,
			self.name,
			self.desc + ' * ' + str(other)
		)
	
	def __rmul__(self, other):
		return PredefinedField(
			self.grid,
			other * self.field,
			self.name,
			str(other) + ' * ' + self.desc
		)

class PartList(DataObject):
	def __init__(self,
		parts = [],
		assemblies = [],
		name = '',
		grid = None
	):
		self.parts = list(parts);
		self.assemblies = list(assemblies);
		self.name = name;
		self.grid = grid;
	
	def __add__(self, other):
		return PartList(
			self.parts + other.parts,
			self.assemblies + other.assemblies,
			self.name + ' + ' + other.name,
			self.grid if self.grid is not None else other.grid
		);