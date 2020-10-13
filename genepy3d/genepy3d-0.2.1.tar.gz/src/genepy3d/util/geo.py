# -*- coding: utf-8 -*-

import numpy as np

def l2(p1, p2):
    """L2 distance between two points p1, p2.
    """
    return np.sqrt(np.sum((p1-p2)**2))

def norm(p):
    """Norm of points.
    
    Args:
        p (array of float): list of 3D points.
        
    Returns:
        array of float.
    
    """
    
    if len(p.shape)==2: # list of points
        return np.sqrt(np.sum(p**2,axis=1))
    elif len(p.shape)==1: # only one point
        return np.sqrt(np.sum(p**2))
    else:
        raise ValueError('Accept only vector or array of vectors.')

def vector2points(a,b,normalize=True):
    """Compute vector from point a to point b with/without normalization.
    """
    
    v = b - a
    if((normalize==True)&(norm(v)!=0)):
        return v/norm(v)
    else:
        return v
    
def vector_axes_angles(v):
    """Return angles between vector v and three axes x, y and z.
    """
    
    if norm(v)!=0:
        vx = np.array([1.,0.,0.])
        vy = np.array([0.,1.,0.])
        vz = np.array([0.,0.,1.])
        
        thetax = np.arccos(np.dot(v,vx)/(norm(v)*norm(vx)))
        thetay = np.arccos(np.dot(v,vy)/(norm(v)*norm(vy)))
        thetaz = np.arccos(np.dot(v,vz)/(norm(v)*norm(vz)))
        
        return (thetax, thetay, thetaz)
    
    else:
        return (0,0,0)

def vector_spherical_angles(v):
    """Spherical angles of vector.
        
    Returns:
        [theta, phi] spherical angles.
       
    """
    
    orientations=[]
    # Here spherical coordianates are specified by
    # theta azimuthal angle, between the orthogonal projection(on Oxy plan) and Ox axis
    # phi polar angle, between the component and Oz axis
    if np.abs(v[0])<0.1 :
        if np.abs(v[1])<0.1 :
            phi=0
            # if phi equals to zero then the component is collinear to Oz axis and
            # theta has no numerical value
            theta='theta'
        else :
            theta=np.pi/2
            phi=np.arccos(v[2])
    else :
        phi=np.arccos(v[2])
        theta=np.arctan(v[1]/v[0])
    orientations.append([theta,phi])
    return orientations

def angle2vectors(a,b):
    """Return angle between two vectors a and b.
    """
    return np.arccos(np.dot(a,b)/(norm(a)*norm(b)))

def angle3points(a,b,c):
    """Return angle between three points where b is the center point.
    
    Args:
        a (array of float): points in 3D.
        b (array of float): points in 3D.
        c (array of float): points in 3D.
        
    Returns:
        float.
    
    """
    ab = b - a
    bc = c - b
    cosine_angle = np.dot(ab, bc) / (np.linalg.norm(ab) * np.linalg.norm(bc))
    return np.arccos(cosine_angle)

def geo_len(P):
    """Return geodesic length from a set of (ordered) points P in nD (n=2 or 3).
    
    Args:
        P (array of float): list of points in nD (n=2 or 3).
        
    Returns:
        float.    
    
    """
    n = P.shape[0]
    s = 0
    for i in range(n-1):
        p1, p2 = P[i], P[i+1]
        s = s + np.sqrt(np.sum((p1-p2)**2))
    return s

def active_brownian_2d(n,v=1e-6,omega=0.,p0=[0,0],dt=1e-3,R=1e-6,T=300.,eta=1e-3,seed_point=None):
    """Generate an active Brownian motion in 2D.
    
    Args:
        n (int): number of times of motion.
        p0 (array of float): init position.
        v (float): translation speed.
        omega (float): rotation speed.
        dt (float): time step.
        R (float): particle radius.
        T (float): environment temperature.
        eta (float): fluid viscocity.
    
    Returns:
        A tuple containing
            - P (array of float): list of 2D positions.
            - t (array of float): corresponding times.
        
    """
    if seed_point is not None:
        np.random.seed(seed_point)
    
    kB = 1.38e-23 # Boltzmann constant [J/K]
    gamma = 6*np.pi*R*eta # friction coefficient [Ns/m]
    DT = (kB*T)/gamma # translational diffusion coefficient [m^2/s]
    DR = (6*DT)/(8*R**2) # rotational diffusion coefficient [rad^2/s]
    
    P = np.zeros((n,2))
    P[0] = p0 # init point
    
    theta = 0 # init angle
    
    for i in range(n-1):
        # translational diffusion step
        P[i+1] = P[i] + np.sqrt(2*DT*dt)*np.random.randn(1,2)
    
        # rotational diffusion step
        theta = theta + np.sqrt(2*DR*dt)*np.random.randn(1,1)[0,0]
        
        # torque step
        theta = theta + dt*omega

        # drift step
        P[i+1] = P[i+1] + dt*v*np.array([np.cos(theta), np.sin(theta)])
    
    t = np.arange(0,n*dt,dt)
    
    return (P,t)

def active_brownian_3d(n,v=1e-6,omega=0.,p0=[0,0,0],dt=1e-3,R=1e-6,T=300.,eta=1e-3,seed_point=None):
    """Generate an active Brownian motion in 3D.
    
    Args:
        n (int): number of times of motion.
        p0 (array of float): init position.
        v (float): translation speed.
        omega (float): rotation speed.
        dt (float): time step.
        R (float): particle radius.
        T (float): environment temperature.
        eta (float): fluid viscocity.
    
    Returns:
        A tuple containing
            - P (array of float): list of 3D positions.
            - t (array of float): corresponding times.
        
    """
    
    if seed_point is not None:
        np.random.seed(seed_point)
    
    kB = 1.38e-23 # Boltzmann constant [J/K]
    DT = (kB*T)/(6*np.pi*eta*R) # translational diffusion coefficient [m^2/s]
    DR = (kB*T)/(8*np.pi*eta*R**3) # rotational diffusion coefficient [rad^2/s]
    
    P = np.zeros((n,3))
    P[0] = p0 # init point
    
    theta = 0 # init angle
    phi = 0 # init angle
    
    for i in range(n-1):
        # translational diffusion step
        P[i+1] = P[i] + np.sqrt(2*DT*dt)*np.random.randn(1,3)
    
        # rotational diffusion step
        theta = theta + np.sqrt(2*DR*dt)*np.random.randn(1,1)[0,0]
        phi = phi + np.sqrt(2*DR*dt)*np.random.randn(1,1)[0,0]
        
        # torque step
        if omega != 0:
            theta = theta + dt*np.sin(omega)
            phi = phi + dt*np.cos(omega)

        # drift step
        P[i+1] = P[i+1] + dt*v*np.array([np.cos(theta)*np.sin(phi), np.sin(theta)*np.sin(phi), np.cos(phi)])
    
    t = np.arange(0,n*dt,dt)
    
    return (P,t)

def emd(X,Y,return_flows=False):
    """Compute Earth Mover's Distance (EMD) between two nD points X and Y.
    
    Args:
        X (nD array): nD points.
        Y (nD array): nD points.
        return_flows (bool): if True return matching flows between X and Y.
        
    Returns:
        if return_flows is False, then only distance value else a tuple of distance and array of flows.
    
    """
    from emd import emd as emddev
    
    return emddev(X,Y,return_flows=return_flows)


def rotation_matrix(u,theta):
    """Give the rotation matrix relative to a direction and an angle.

    Args:
        u (1d numpy array) : 3d vector for rotation direction.
        theta (float) : rotation angle in radians.

    Returns:
        (2d numpy array of shape (3,3)) : rotation matrix.


    """
    P=np.kron(u,u).reshape(3,3)
    Q=np.diag([u[1]],k=2)+np.diag([-u[2],-u[0]],k=1)+np.diag([u[2],u[0]],k=-1)+np.diag([-u[1]],k=-2)
    return P+np.cos(theta)*(np.eye(3)-P)+np.sin(theta)*Q































