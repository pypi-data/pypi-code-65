import osa
import numpy as np
import warnings
import netCDF4
from . import inputs
from . import cache

import functools

SERVICE_ADDRESS = 'http://esb.ipp-hgw.mpg.de:8280/services/FieldLineProxy?wsdl';
COMPONENTS_DB_ADDRESS = 'http://esb.ipp-hgw.mpg.de:8280/services/ComponentsDBProxy?wsdl';

boundary = inputs.PartList(parts = [164]);

try:
    client = osa.Client(SERVICE_ADDRESS);
except:
    warnings.warn('Could not connect to the W7-X field-line tracer. A lot of functionality will be unavailable.');
    client = None;

try:
    cdb = osa.Client(COMPONENTS_DB_ADDRESS);
except:
    warnings.warn('Could not connect to Components DB proxy. Some functionality will be unavailable.');
    client = None;

#Perform a tracing operation with the built-in magnetic field and machine geometry
def do_trace(points, task, magnetic_config, part_list, client = client):
    return client.service.trace(
        make_points_3d(points),
        make_magnetic_config(magnetic_config),
        task,
        make_machine_config(part_list)
    );
    
def _do_trace_shaped(points, task, magnetic_config, part_list, client = client):
    assert points.shape[0] == 3;
    
    return points.shape, do_trace(
        np.reshape(points, [3, -1]),
        task,
        magnetic_config,
        part_list,
        client
    );
    
def line_trace(points, num_steps, magnetic_config, part_list, step_size = 1e-3, client = client, free_path = 1e-1, velocity = 1e6, diffusion_coefficient = 0.0):
    """
    Traces magnetic field lines.
    
    Args:
        points: A [3,...] shaped numpy array-like of points in xyz-Format.
        num_steps: Number of steps to trace for the field line.
        magnetic_config: A magnetic configuration
        part_list: A list of parts and assemblies that might obstruct the field line
        step_size: Number of steps
        client: OSA client for web-service, defaults to global singleton
        free_path: Free path to use for convective field-line diffusion, defaults to 0.1
        velocity: Velocity to use for field-line diffusion, defaults to 1e6
        diffusion_coefficient: Diffusion coefficient to use for field-line diffusion, defaults to 0.0 (which means no diffusion)
    
    Returns:
        lines, line_lengths
        line: A numpy array of shape points.shape + [num_steps + 1] holding field line coordinates for all points passed in.
        line_lengths: A numpy array of shape points.shape[1:] holding the number of vertices in each line.
    """
    
    points = np.asarray(points);
    
    task = client.types.Task();
    
    task.step = step_size;
    task.lines = client.types.LineTracing();
    task.lines.numSteps = num_steps;
    
    if diffusion_coefficient != 0.0:
        task.diffusion = client.types.LineDiffusion();
        task.diffusion.diffusionCoeff = diffusion_coefficient;
        task.diffusion.freePath = free_path;
        task.diffusion.velocity = velocity;
    
    in_shape, trace_result = _do_trace_shaped(points, task, magnetic_config, part_list, client = client);
    
    lines = np.full(
        [3, len(trace_result.lines), num_steps + 1], 
        np.nan,
        dtype = np.float64
    );
    
    lengths = np.zeros(
        [len(trace_result.lines)],
        dtype = np.int32
    );
    
    for i_line in range(0, len(trace_result.lines)):
        p3d = trace_result.lines[i_line].vertices;
        n_v = len(p3d.x1);
        
        lines[0, i_line,0:n_v] = np.asarray(p3d.x1);
        lines[1, i_line,0:n_v] = np.asarray(p3d.x2);
        lines[2, i_line,0:n_v] = np.asarray(p3d.x3);
        
        lengths[i_line] = n_v;
    
    return np.reshape(lines, in_shape + (num_steps + 1,)), np.reshape(lengths, in_shape[1:]);
    
def connection_length(points, magnetic_config, part_list, step_size = 1e-3, return_loads = False, limit = 1e3, client = client, free_path = 1e-1, velocity = 1e6, diffusion_coefficient = 0.0):
    """
    Calculates the connection length for a given number of points.
    
    Args:
        points: A [...,3] shaped numpy array-like of points in xyz-Format.
        num_steps: Number of steps to trace for the field line.
        magnetic_config: A magnetic configuration
        part_list: A list of parts and assemblies that might obstruct the field line
        step_size: Number of steps
        return_loads: Whether the loads on components should also be computed (must be False at the moment)
        limit: The maximum length for the field lines to be traced
        client: OSA client for web-service, defaults to global singleton
        free_path: Free path to use for convective field-line diffusion, defaults to 0.1
        velocity: Velocity to use for field-line diffusion, defaults to 1e6
        diffusion_coefficient: Diffusion coefficient to use for field-line diffusion, defaults to 0.0 (which means no diffusion)
    
    Returns:
        A dict with the following entries:
            p_end: Numpy array of shape points.shape containing the end points of the field lines.
            length: Numpy array of shape points.shape[1:] containing the connection lengths for all points.
            part_id: Numpy array of shape points.shape[1:] containing the ids of the part impacted by the field line.
            element_id: Numpy array of shape points.shape[1:] containing the element number in the part geometry.               
    """
    assert not return_loads, 'Computation of heat loads not yet implemented';
    
    points = np.asarray(points);
    
    task = client.types.Task();
    task.step = step_size;
    
    task.connection = client.types.ConnectionLength();
    task.connection.limit = limit;
    task.connection.returnLoads = return_loads;
    
    if diffusion_coefficient != 0.0:
        task.diffusion = client.types.LineDiffusion();
        task.diffusion.diffusionCoeff = diffusion_coefficient;
        task.diffusion.freePath = free_path;
        task.diffusion.velocity = velocity;
    
    # TODO: Compute LCFS and check which points are inside
    in_shape, trace_result = _do_trace_shaped(points, task, magnetic_config, part_list, client = client);
    
    result = {
        'p_end' : np.reshape(
            np.moveaxis([(r.x, r.y, r.z) for r in trace_result.connection], -1, 0),
            in_shape
        ),
        'length' : np.reshape(
            [r.length for r in trace_result.connection],
            in_shape[1:]
        ),
        'part_id' : np.reshape(
            [(r.part if r.part is not None else np.nan) for r in trace_result.connection],
            in_shape[1:]
        ),
        'element_id' : np.reshape(
            [(r.element if r.element is not None else np.nan) for r in trace_result.connection],
            in_shape[1:]
        )
    };
    
    return result;
    
    
#def line_diffusion(points, magnetic_config, part_list, step_size = 1e-3, num_steps = 1000, client = client, free_path = 1e-1, velocity = 1e6, diffusion_coefficient = 2):
    #"""
    #Calculates the connection length for a given number of points.
    #
    #Args:
    #    points: A [...,3] shaped numpy array of points in xyz-Format.
    #    num_steps: Number of steps to trace for the field line.
    #    magnetic_config: A magnetic configuration
    #    part_list: A list of parts and assemblies that might obstruct the field line
    #    step_size: Number of steps
    #    return_loads: Whether the loads on components should also be computed (must be False at the moment)
    #    limit: The maximum length for the field lines to be traced
    #    client: OSA client for web-service, defaults to global singleton
    #
    #Returns:
    #    A dict with the following entries:
    #        p_end: Numpy array of shape points.shape containing the end points of the field lines.
    #        length: Numpy array of shape points.shape[1:] containing the connection lengths for all points.
    #        part_id: Numpy array of shape points.shape[1:] containing the ids of the part impacted by the field line.
    #        element_id: Numpy array of shape points.shape[1:] containing the element number in the part geometry.               
    #"""
    #task = client.types.Task();
    #task.step = step_size;
    #
    #task.diffusion = client.types.LineDiffusion();
    #task.diffusion.diffusionCoeff = diffusion_coefficient;
    #task.diffusion.freePath = free_path;
    #task.diffusion.velocity = velocity;
    #
    #task.lines = client.types.LineTracing();
    #task.lines.numSteps = num_steps;
    #
    ## TODO: Compute LCFS and check which points are inside
    #in_shape, trace_result = _do_trace_shaped(points, task, magnetic_config, part_list, client = client);
    #
    #lines = np.full(
    #    [3, len(trace_result.lines), num_steps + 1], 
    #    np.nan,
    #    dtype = np.float64
    #);
    #
    #lengths = np.zeros(
    #    [len(trace_result.lines)],
    #    dtype = np.int32
    #);
    #
    #for i_line in range(0, len(trace_result.lines)):
    #    p3d = trace_result.lines[i_line].vertices;
    #    n_v = len(p3d.x1);
    #    
    #    lines[0, i_line,0:n_v] = np.asarray(p3d.x1);
    #    lines[1, i_line,0:n_v] = np.asarray(p3d.x2);
    #    lines[2, i_line,0:n_v] = np.asarray(p3d.x3);
    #    
    #    lengths[i_line] = n_v;
    #
    #return np.reshape(lines, in_shape + (num_steps + 1,)), np.reshape(lengths, in_shape[1:]);
    #
    #result = {
    #   'p_end' : np.reshape(
    #       np.moveaxis([(r.x, r.y, r.z) for r in trace_result.connection], -1, 0),
    #       in_shape
    #   ),
    #   'length' : np.reshape(
    #       [r.length for r in trace_result.connection],
    #       in_shape[1:]
    #   ),
    #   'part_id' : np.reshape(
    #       [(r.part if r.part is not None else np.nan) for r in trace_result.connection],
    #       in_shape[1:]
    #   ),
    #   'element_id' : np.reshape(
    #       [(r.element if r.element is not None else np.nan) for r in trace_result.connection],
    #       in_shape[1:]
    #   )
    #};
    #
    #return result;
    #
    #return trace_result;
    
#Perform a Poincare plot
def poincare_in_phi_planes(points, phi_values, n_turns, magnetic_config, part_list, step_size = 1e-3, client = client, free_path = 1e-1, velocity = 1e6, diffusion_coefficient = 0.0):
    """
    Calculates the poincare plots for a given number of start points.
    
    Args:
        points: A [3,...] array-like (see numpy) of points in xyz-Format.
        phi_values: Array-like of phi values.
        n_turns: Number of turns to take around the machine for each starting point.
        magnetic_config: Magnetic configuration
        part_list: A list of parts and assemblies that might obstruct the field line
        step_size: Field line step size
        client: OSA client for web-service, defaults to global singleton
        free_path: Free path to use for convective field-line diffusion, defaults to 0.1
        velocity: Velocity to use for field-line diffusion, defaults to 1e6
        diffusion_coefficient: Diffusion coefficient to use for field-line diffusion, defaults to 0.0 (which means no diffusion)
    
    Returns:
        A [3] + phi_values.shape + points.shape[1:] + [n_turns] numpy array containing the xyz-coordinates of all points in the Poincaré-Plots, or NaN.
    """
    points = np.asarray(points);
    phi_values = np.asarray(phi_values);
    
    task = client.types.Task();
    task.step = step_size;
    
    task.poincare = client.types.PoincareInPhiPlane();
    task.poincare.phi0 = phi_values.flatten();
    task.poincare.numPoints = n_turns;
    
    if diffusion_coefficient != 0.0:
        task.diffusion = client.types.LineDiffusion();
        task.diffusion.diffusionCoeff = diffusion_coefficient;
        task.diffusion.freePath = free_path;
        task.diffusion.velocity = velocity;
    
    in_shape, trace_result = _do_trace_shaped(points, task, magnetic_config, part_list, client = client);
    
    # Trace result contains a flat array of surfaces, surfaces indexed by phi, then by start point
    
    result_points = np.full(
        [3, n_turns, phi_values.size * points.size // 3],
        np.nan
    );
    
    for i in range(0, len(trace_result.surfs)):
        surf = trace_result.surfs[i];
        p3d = surf.points;
        
        if p3d.x1 is None:
            continue;

        n_v = len(p3d.x1);
        
        result_points[0, 0:n_v, i] = p3d.x1;
        result_points[1, 0:n_v, i] = p3d.x2;
        result_points[2, 0:n_v, i] = p3d.x3;
    
    # Note: for some reason, the turn no. is the major and phi the minor axis
    result_points = np.reshape(result_points, (3,n_turns) + in_shape[1:] + (phi_values.size,));
    result_points = np.moveaxis(result_points, [1, -1], [-1,1]); # Move the n_turns axis to the end and the phi axis to the second place
    # Reshape the phi axis to match input shape
    result_points = np.reshape(result_points, (3,) + phi_values.shape + in_shape[1:] + (n_turns,));
    
    # Return shape: [3] + phi_values.shape + in_shape[1:] + [n_turns]
    return result_points;
    
def magnetic_field(points, magnetic_config, client = client):
    """
    Calculates the magnetic field for a given number of start points in cartesian coordinates
    
    Args:
        points: A [3,...] array-like (see numpy) of points in xyz-Format.
        magnetic_config: Magnetic configuration
        client: OSA client for web-service, defaults to global singleton
    
    Returns:
        A numpy array with shape points.shape containing the (cartesian) magnetic fields at the specified points.
    """
    points = np.asarray(points);
    assert points.shape[0] == 3;
    in_shape = points.shape;
    
    points = np.reshape(points, [3, -1]);
    
    mf_result = client.service.magneticField(
        make_points_3d(points), 
        make_magnetic_config(magnetic_config)
    );
    
    result = np.asarray(
        [mf_result.field.x1, mf_result.field.x2, mf_result.field.x3]
    );
    
    result = np.reshape(result, in_shape);
    
    return result;

def magnetic_field_rphiz(points, magnetic_config, client = client):
    """
    Calculates the magnetic field for a given number of start points in cylindrical coordinates
    Args:
        points: A [3, ...] numpy array-like of points in xyz-format.
        magnetic_config: Magnetic configuration
        client: OSA client for webservice (defaults to global singleton)
    
    Returns:
        A numpy array with shape points.shape containing the (cylindrical) magnetic field at the given points in r, phi, z order.
    """
    points = np.asarray(points);
    b = magnetic_field(points, magnetic_config, client);
    
    r = np.sqrt(points[0]**2 + points[1]**2);
    
    #B_tor = <e_phi, B> = <(-y, x) / |(x, y)|, B> = (B_y * x - B_x * y) / r;
    b_tor = b[1] * points[0] - b[0] - points[1];
    b_tor = b_tor / r;
    
    b_rad = b[0] * points[0] + b[1] * points[1];
    b_rad = b_rad / r;
    
    return np.stack([b_rad, b_tor, b[2]], axis = 0);
    
@functools.lru_cache(typed=True)
def find_axis(magnetic_config, step_size = 1e-3, accuracy = 1e-4, client = client):
    """
    Calculates the magnetic axis of the given configuration.
    
    Args:
        magnetic_config: Magnetic configuration
        step_size: Step size for the field line tracing.
        client: OSA client for web-service, defaults to global singleton
    
    Returns:
        The effective radius and a numpy array with shape [3, n_points] holding the magnetic axis in cartesian coordinates.
    """
    settings = client.types.AxisSettings()
    settings.axisAccuracy = accuracy
    
    axis_result = client.service.findAxis(
        step_size,
        make_magnetic_config(magnetic_config),
        settings
    );
    
    verts = axis_result.axis.vertices;
    
    axis_points = np.asarray(
        [verts.x1, verts.x2, verts.x3]
    );
    
    return axis_result.reff, axis_points;
    
@functools.lru_cache(typed=True)
def find_lcfs(
    magnetic_config, part_list,
    x_min = 6.1, x_max = 6.35,
    n_points = 40, trace_limit = 1e3, step_size = 1e-3,
    accuracy = 1e-3,
    client = client
):
    """
    Calculates the start point of last closed flux surface near the phi=0, z=0 line.
    
    Args:
        magnetic_config: Magnetic configuration
        part_list: List of parts and assemblies
        x_min: Minimum x value.
        x_max: Maximum x value.
        n_points: How many points to compute for the flux surface per iteration.
        trace_limit: Maximum field-line length for tracing the LCFS.
        step_size: Step size for tracing the magnetic field lines.
        accuracy: Accuracy limit for the LCFS position.
        client: OSA client for web-service, defaults to global singleton
    
    Returns:
        A numpy array with shape [3, n_points] holding the magnetic axis in cartesian coordinates.
    """
    settings = client.types.LCFSSettings();
    settings.LCFSLeftX = x_min;
    settings.LCFSRightX = x_max;
    settings.LCFSNumPoints = n_points;
    settings.LCFSThreshold = trace_limit;
    settings.LCFSAccuracy = accuracy;
    
    lcfs_result = client.service.findLCFS(
        step_size,
        make_magnetic_config(magnetic_config),
        make_machine_config(part_list + boundary),
        settings
    );
    
    return np.asarray([lcfs_result.x, lcfs_result.y, lcfs_result.z]);
    
def axis_current(magnetic_config, current, positive_direction = 'clock-wise', step_size = 1e-3, accuracy = 1e-4, client = client):
    """
    Creates an artificial coil lying on the magnetic axis of the specified configuration.
    
    Args:
        magnetic_config: Magnetic configuration
        current: Current (in A) to be placed on the magnetic axis.
        positive_direction: Direction along which current should be positive. Must be 'clock-wise', 'counter-clock-wise', 'field' or 'against-field'.
        step_size: Step size for the field line tracing of the axis.
        client: OSA client for web-service, defaults to global singleton
    
    Returns:
        A BiotSavartField instance describing a single coil (on the magnetic axis) with the specified current.
    """
    directions = {
        'clock-wise' : 'CW',
        'counter-clock-wise' : 'CCW',
        'field' : 'B',
        'against-field' : '-B'
    };
    assert positive_direction in directions, 'positive_direction must be either \'clock-wise\', \'counter-clock-wise\', \'field\' or \'against-field\'';
    
    _, axis = find_axis(magnetic_config, client = client, step_size = step_size, accuracy = accuracy);
    
    phi = np.arctan2(axis[1], axis[0]);
    
    delta_phi = (phi[1] - phi[0] + 2 * np.pi) % (2 * np.pi);
    
    if delta_phi < np.pi:
        axis_direction = 'counter-clock-wise';
    else:
        axis_direction = 'clock-wise';
    
    if positive_direction == 'field':
        axis_direction = positive_direction;
    
    internal_current = current if axis_direction == positive_direction else -current;
    
    return inputs.BiotSavartField(
        custom_coils = [axis],
        custom_currents = [internal_current],
        name = 'Iax',
        desc = '{}A on axis ({} dir.)'.format(current, directions[positive_direction])
    );
    
def make_magnetic_config(input, client = client):       
    if isinstance(input, inputs.BiotSavartField):
        config = _make_bs_config(input, client = client);
    elif isinstance(input, inputs.PredefinedField):
        config = _make_field_config(input, client = client);
    else:
        assert False;
        
    config.inverseField = input.inverse;
    
    return config;

def symmetrize(p_xyz, symmetry = 1, quasi_mirror_symmetry = False, scatter = True):
    p_xyz = np.asarray(p_xyz);
    
    assert len(p_xyz.shape) == 2;
    assert p_xyz.shape[0] == 3;
    
    p_xyz = np.copy(p_xyz);
    
    # Convert points to r-phi-z representation
    p_rphiz = np.stack([
        np.sqrt(p_xyz[0]**2 + p_xyz[1]**2),
        np.arctan2(p_xyz[1], p_xyz[0]),
        p_xyz[2]
    ]);
    
    # If mirror symmetry is enabled, flip all points to z >= 0
    if quasi_mirror_symmetry:
        for i in range(0, p_rphiz.shape[1]):
            if p_rphiz[2,i] < 0:
                p_rphiz[1:,i] = -p_rphiz[1:,i];
    
    # Limit phi to [0, 2 * pi / symmetry)
    p_rphiz[1] = (p_rphiz[1] + 2 * np.pi) % (2 * np.pi / symmetry);
    
    # Scatter to all possible phi angles
    if scatter:
        p_rphiz = np.concatenate(
            [
                np.stack([p_rphiz[0], p_rphiz[1] + d_phi, p_rphiz[2]])
                for d_phi in np.linspace(0, 2 * np.pi, symmetry, endpoint = False)
            ],
            axis = 1
        );
    
        if quasi_mirror_symmetry:
            p_rphiz = np.concatenate(
                [p_rphiz, np.stack([p_rphiz[0], -p_rphiz[1], -p_rphiz[2]])],
                axis = 1
            );
        
    p_xyz = np.stack([
        p_rphiz[0] * np.cos(p_rphiz[1]),
        p_rphiz[0] * np.sin(p_rphiz[1]),
        p_rphiz[2]
    ]);
    
    return p_xyz;
    
    

def _filter(coils, currents):
    if all(i == 0 for i in currents):
        return ([], []);
        
    return tuple(zip(
        *[
            (c, i)
            for c, i in zip(coils, currents)
            if i != 0
        ]
    ));
    
def _make_bs_config(input, client = client):
    config = client.types.MagneticConfig();
    
    if input.grid is not None:
        config.grid = make_grid(input.grid, client = client);
    
    config.coilsIds, config.coilsIdsCurrents = _filter(
        input.coilsdb_coils,
        input.coilsdb_currents
    );
    
    config.coils, config.coilsCurrents = _filter(
        [_make_coil(c) for c in input.custom_coils],
        input.custom_currents
    );
    
    config.configIds = input.coilsdb_configs;
        
    return config;
    
def _make_field_config(input, client = client):
    config = client.types.MagneticConfig();
    config.grid = make_grid(input.grid, client = client);   
    
    cacheref = cache.maybe_cache_config(input);
    
    if cacheref is None:
        config.grid.gridField = make_points_3d(input.field, client = client);
    else:
        #print('Using cache ref ' + cacheref)
        config.grid.afsFileName = cacheref;
    
    return config;
    
def make_machine_config(part_list, client = client):
    machine = client.types.Machine(1);
    
    grid = part_list.grid;
    assert grid is not None, 'Part list has no geometry grid specified. Please include at least one part list that specifies a grid.';
    
    if grid is not None:
        machine.grid.numX, machine.grid.numY, machine.grid.numZ = grid.n_x, grid.n_y, grid.n_z;
        machine.grid.XMin, machine.grid.XMax = grid.x_min, grid.x_max;
        machine.grid.YMin, machine.grid.YMax = grid.y_min, grid.y_max;
        machine.grid.ZMin, machine.grid.ZMax = grid.z_min, grid.z_max;
    
    machine.meshedModelsIds = part_list.parts;
    machine.assemblyIds     = part_list.assemblies;
    
    return machine;
    
def make_points_3d(input, client = client, xyz_last = False):
    result = client.types.Points3D();
    
    if xyz_last:
        input = np.reshape(input, [-1, 3]);
        
        result.x1 = input[:,0];
        result.x2 = input[:,1];
        result.x3 = input[:,2];
    else:
        input = np.reshape(input, [3, -1]);
        
        result.x1 = input[0];
        result.x2 = input[1];
        result.x3 = input[2];       
    
    return result;
    
def _make_coil(input, client = client):
    try:
        np_in = np.asarray(input);
    except:
        assert isinstance(input, client.types.PolygonFilament);
        return input;
    
    assert len(np_in.shape) == 2;
    assert np_in.shape[0] == 3;
    
    if (np_in[:,-1] != np_in[:,0]).any():
        warnings.warn('Coil passed as numpy array has p_start != p_end');
    
    result = client.types.PolygonFilament();
    result.vertices = make_points_3d(np_in, client = client);
    
    return result;
        
        
def make_grid(input, client = client):
    cyl = client.types.CylindricalGrid();
    
    cyl.RMin = input.r_min;
    cyl.RMax = input.r_max;
    cyl.ZMin = input.z_min;
    cyl.ZMax = input.z_max;
    
    cyl.numR = input.n_r;
    cyl.numZ = input.n_z;
    cyl.numPhi = input.n_phi;
    
    grid               = client.types.Grid();
    grid.fieldSymmetry = input.n_sym;
    grid.cylindrical   = cyl;
    
    return grid;
    
def parts_in_assembly(assembly_id):
    return cdb.service.getAssemblyData(assembly_id)[0].components;

def serialize_part_list(input):
    return input.parts + [
        p
        for assembly in input.assemblies
        for p in parts_in_assembly(assembly)
    ];