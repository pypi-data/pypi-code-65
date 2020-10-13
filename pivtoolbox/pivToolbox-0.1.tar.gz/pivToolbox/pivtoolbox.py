# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 13:56:10 2018

@author: dugj2403


"""

import os
from glob import glob
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def rename_axis(df,axis_in,axis_out):
    """
    Replace axis_in[i] with axis_out[i]
    """
    df=deepcopy(df)
    
    
    for count, column in enumerate(axis_in):
        df.rename(columns={column:axis_out[count]}, inplace=True)
    return df


def get_PIV_files(path,**keyword_parameters):
    """Recursively look in directory specified as path and its subdirectories 
    for PIV .dat files. All '.dat' files are found by looking recursively
    in the path, these are returned in the 'full_list'. The treatment 
    
    Args:
    path      (str): Directory to look in.
    treatment (str): keyword used in file name to identify treatment
    
    Returns:
    treatment_1 (list): containing file paths for treatment 1
    treatment_2 (list): containing file paths for treatment identified by "treatment" keyword
    """
 
    result = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.dat'))]
    return_list=[]

    for i in result:
        if ('treatment' in keyword_parameters):
            treatment=keyword_parameters['treatment']
            if treatment in i:
                return_list.append(i)
        else:
            return_list.append(i)
    return return_list


def load_PIV_dataframes(file_list,plane_labels,shot_labels,fieldNames,fieldKeys,**keyword_parameters):
    
    """Load data contained in .dat into pandas dataframes, neatly organized in a 
       heirachical dictionary. Must contain 'x', 'y' and 'scalar' data. 
       Your scalar field should be exported in DaVis as a Tecplot .dat file. Planes
       are physically different locations of the laser light sheet. Shots are repetitions
       at the same plane. If you only have 1 plane and 1 shot, name your file something
       like 'Plane_1_shot_1' anyway, and then use these to populate the plane_labels 
       and shot_labels lists.
    
    Args:
    file_list    [list]: list from find_PIV_files() containing file paths
    Plane_labels [list]: strings of keywords used in file path to identify 'planes'
    shot_labels  [list]: strings of keywords used in file path to identify 'shots'
    fieldKeys    [list]: strings of keywords used in file path to identify each scalar field (e.g. "B0001" - crappy DaVis output)
    fieldNames   [list]: strings of keywords corresponding to fieldKeys ("B0001" corresponds to 'u')
  
    Returns:
    shot_dic    {dict}: two-level dictionary. shot_labels are outer keys and fieldNames are inner keys.
                        each inner key is attributed a dataframe with corresponding dataframe containing scalar data
    """
    print(shot_labels)
    plane_dic={}
    for file in file_list:
        for plane in plane_labels:
            if plane in file:
                if plane not in plane_dic:
                    plane_dic[plane] = {}
                for shot in shot_labels:
                    
                    if shot in file:
                        if shot not in plane_dic[plane]:
                            plane_dic[plane][shot] = {}
                        for index, fieldKey in enumerate(fieldKeys):
                            if fieldNames[index] not in plane_dic[plane][shot]:
                                plane_dic[plane][shot][fieldNames[index]]={}
                            if fieldKey in file:
                                df=pd.read_table(file,skiprows=[0,1,2],delim_whitespace=True,names=['x','y',fieldNames[index],'valid'])
                                print(shot,fieldKey,index,fieldNames[index])
                                plane_dic[plane][shot][fieldNames[index]]=df

    if ('rename_axis' in keyword_parameters):
        if keyword_parameters['rename_axis']==True:
            axis_in=keyword_parameters['axis_in']
            axis_out=keyword_parameters['axis_out']
            
            for plane in plane_dic:
                for shot in plane_dic[plane]:
                    for frame in plane_dic[plane][shot]:
                        plane_dic[plane][shot][frame]=rename_axis(plane_dic[plane][shot][frame],axis_in,axis_out)        
    
    return plane_dic

def process_piv_dictionary(dictionary,scalar_name,plane_labels,plane_positions,**keyword_parameters):
    
    print("\n")
    print("Processing dictionary containing PIV planes and shots:")
    
    return_dict={}
    
    for counter, plane in enumerate(plane_labels):
        print("\n")
        print("Processing %s" %plane)
        
        if 'average' in keyword_parameters:
            
            if keyword_parameters['average']:
                
                axis=keyword_parameters['axis']
                
                if 'prefix' in keyword_parameters:
                    prefix=keyword_parameters['prefix']
                    df=average_PIV_field(dictionary[plane],axis,scalar_name,prefix=prefix)
                else:
                    df=average_PIV_field(dictionary[plane],axis,scalar_name)
                    
        if 'geoRef' in keyword_parameters:
            if keyword_parameters['geoRef']:
                geoRefCoords=keyword_parameters['geoRefCoords']
                
                #get current geoRefCoord
                geoRefCoord=[0,0,0]
                for i, axis in enumerate(geoRefCoords):
                    
                    if type(axis) is int:
                        geoRefCoord[i]=axis
                        
                    if type(axis) is list:
                        geoRefCoord[i]=axis[counter]
                        
                    if type(axis) is float:
                        geoRefCoord[i]=axis
                        
                print("Georeferencing %s with %s" %(plane,str(geoRefCoord)))
                try:
                    #only if 'average'
                    df=piv.georeference(df,geoRefCoord)
                    
                except NameError:
                    
                    single_shot_ID=list(dictionary[plane].keys())[0]
                    df=georeference(dictionary[plane][single_shot_ID][scalar_name],geoRefCoord)
        
        if 'crop' in keyword_parameters:
            if keyword_parameters['crop']:
                
                try:
                    limits_x=keyword_parameters['limits_x']
                except KeyError:
                    pass
                
                try:
                    limits_y=keyword_parameters['limits_y']
                except KeyError:
                    pass
                
                try:
                    limits_z=keyword_parameters['limits_z']
                except KeyError:
                    pass
                
                if 'limits_x' in keyword_parameters:
                    if 'limits_y' in keyword_parameters:
                        print('Cropping %s along x and y' % plane)
                        df=crop_scalar_field(df,limits_x=limits_x,limits_y=limits_y)
                if 'limits_x' in keyword_parameters:
                    if 'limits_z' in keyword_parameters:
                        print('Cropping %s along x and z' % plane)
                        df=crop_scalar_field(df,limits_x=limits_x,limits_z=limits_z)
                if 'limits_y' in keyword_parameters:
                    if 'limits_z' in keyword_parameters:
                        print('Cropping %s along y and z' % plane)
                        df=crop_scalar_field(df,limits_y=limits_y,limits_z=limits_z)
        return_dict.update({plane : df})
        del df
    del keyword_parameters
    return return_dict

 
def average_PIV_field(dictionary,axis,field, **keyword_parameters):
    """Average 2D scalar values across multiple 'shots', where a 'shot' represents
    a sequence of PIV images lasting a duration of time. Multiple shots make up a PIV 
    measurement of plane. Example, five 20 s shots make a total of 100 s of PIV. This function
    takes the average of each of the five 20 s shots.
    
    Args:
    dictionary      (str): heirachical dictionary containing 'shot_xx' entries as the master key
                     each scalar field for that shot is contained within a subdictionary as 
                     a dataframe that can be accessed with a keyword (e.g. "u" or "TKE")
    field     (str): keyword corresponding to both subdictionary key and header of dataframe


    Returns:
    df (dataframe): containing data from all shots and the averaged scalar field under
                    the header "mean_xx", where xx = field
    """
    df=pd.DataFrame()

    for shot in dictionary:
        print("Including %s for averaging" %shot )
        df[shot+'_'+field]=dictionary[shot][field][field]

    if ('prefix' in keyword_parameters):
        prefix=keyword_parameters['prefix']
        df[prefix+field] = df.mean(axis=1)
        name=prefix+field
    else:
        df[field] = df.mean(axis=1)
        name=field

    df[axis[0]]=dictionary[shot][field][axis[0]]
    df[axis[1]]=dictionary[shot][field][axis[1]]
    
    df=df[[axis[0],axis[1],name]]
    
    if ('output' in keyword_parameters):
        output = keyword_parameters['output']
        if ('path' in keyword_parameters):
            path = keyword_parameters['path']
        if ('prefix' in keyword_parameters):
            prefix = keyword_parameters['prefix']
        if output:
            try:    
                path=path + "\\" + "avg_%s_%s.csv" % (field, prefix)
            except UnboundLocalError:
                path=path + "\\" + "avg_%s.csv" % field  
            df.to_csv(path, columns=[axis[0],axis[1],name],index=False)

    return df

def flip_horizontally(df,axis_name):
    """
    Flips x axis of PIV dataframe to fit within a correct coordinate convention.
    
    Args:
    df      (dataframe): dataframe to be flipped
    axis_name  (string): key of dataframe column to flip
    """
    df=deepcopy(df)
    df[axis_name]=df[axis_name]*(-1)
    return df

def georeference(df,geoRef):
    df=deepcopy(df)
    try:
        df['x'] = df['x']+geoRef[0]
    except KeyError:
        df['x'] = geoRef[0]
        
    try:
        df['y'] = df['y']+geoRef[1]
    except KeyError:
        df['y'] = geoRef[1]
        
    try:  
        df['z'] = df['z']+geoRef[2]
    except KeyError:
        df['z'] = geoRef[2]
    return df


def inverse_scalar(df,scalar):
    df=deepcopy(df)
    df[scalar]=df[scalar]*-1
    return df

def smooth(df,columns,names,period,**keyword_parameters):
    """Smooths out spikey data in a 3D trajectory by running a moving average
    over specified columns of input dataframe. Optionally, the smoothed curve
    can be shifted back close to its originally position by including the shift
    optional argument.
    
    Args:
    df      (dataframe): pandas dataframe
    columns      (list): list of dataframe headers to smooth
    names        (list): names of new columns in same order as columns
    
    Returns:
    dataframe: pandas dataframe containing smoothed and/or shifted columns.
    """
    df=deepcopy(df)
    for i in range(len(columns)):
        df[names[i]]=df[columns[i]].rolling(period).mean()
            
    if ('shift' in keyword_parameters):
        shift = keyword_parameters['shift']
    
    if shift:
        shift_names=keyword_parameters['shift_names']
        shift_period=keyword_parameters['shift_period']
        
        for i in range(len(columns)):
            df[shift_names[i]]=df[names[i]].shift(shift_period)   
    return df

def extractProfile(df,x_axis,y_axis,value):
    
    exactmatch=df[df[x_axis]==value]
    
    if not exactmatch.empty:
        return exactmatch
    else:
        lowerneighbour_ind = df[df[x_axis]<value][x_axis].idxmax()
        upperneighbour_ind = df[df[x_axis]>value][x_axis].idxmin()
        lowValue=df.iloc[lowerneighbour_ind][x_axis]
        highValue=df.iloc[upperneighbour_ind][x_axis]
        print("The closest positions to %f along the specified x_axis are: %f and %f" %(value,lowValue,highValue))
        print("Average values for these positions have been returned at x_axis = %f"  %((lowValue+highValue)/2))
        print("Reminder: 'x_axis' refers to the axis along which you want to extract the profile")
        print("          'y_axis' refers to the plottable values at the specified x_axis position")
        df=df[(df[x_axis] == lowValue)|(df[x_axis] == highValue)]
        df=df.groupby([y_axis]).mean().reset_index()
    return df

def extract_2D_slice(dictionary,axis,position):
    
    dictionary=deepcopy(dictionary)
    slices=[]
    for plane in dictionary:
        dictionary[plane]=dictionary[plane].sort_values(axis,ascending=False).assign(New=(dictionary[plane][axis]-position).abs())
#        dictionary[plane]=dictionary[plane].drop(dictionary[plane][dictionary[plane].New != dictionary[plane].New.min() ].index)
        slices.append(dictionary[plane])
        
    slices=pd.concat(slices).reset_index(drop=True)
    return slices


def crop_scalar_field(df,**keyword_parameters):
	
    """
	 Args:
         
    df              (dataframe): dataframe of scalar field to crop
    limits_x          (keyword): parameters is a list of xmin and xmax
    limits_y          (keyword): parameters is a list of ymin and ymax


    Returns:
    df (dataframe): containing cropped scalar data field
	
	"""
    df=deepcopy(df)
    
    if ('limits_x' in keyword_parameters):
        
        limits_x = keyword_parameters['limits_x']
        df = df.drop(df[df.x < limits_x[0]].index)
        df = df.drop(df[df.x > limits_x[1]].index)
        
    if ('limits_y' in keyword_parameters):
        limits_y = keyword_parameters['limits_y']
        df = df.drop(df[df.y < limits_y[0]].index)
        df = df.drop(df[df.y > limits_y[1]].index)
        
    if ('limits_z' in keyword_parameters):
        limits_z = keyword_parameters['limits_z']
        df = df.drop(df[df.z < limits_z[0]].index)
        df = df.drop(df[df.z > limits_z[1]].index)
    
    return df

def interpolate_to_2D_grid(x,y,s,name,limits,spacings,method, **kwargs):

    """
    Args:
         
    x              (1D np.array float64): x components of mesh grid
    y              (1D np.array float64): y components of mesh grid
    scalar         (1D np.array float64): list of scalar values on grid points

    limits         (list): lenght 4, 0 = xmin, 1 = xmax, 2 = ymin, 3 = ymax
    spacings       (list): length 2, 0 = spacing in x, 1 = spacing in y
    method         (str): choice of 'linear','nearest','cubic'

    fill_value     (float or int): value to fill nan in griddata
    Returns:
    df (dataframe): of interpolated data on specified grid
    """

    xi = np.arange(limits[0],limits[1]+1,spacings[0])
    yi = np.arange(limits[2],limits[3]+1,spacings[1])
    
    xi,yi = np.meshgrid(xi,yi)
    
    if 'fill_value' in kwargs:
        interpol_data = griddata((x,y),s,(xi,yi),method=method,fill_value=kwargs['fill_value'])
    else:
        interpol_data = griddata((x,y),s,(xi,yi),method=method)
    output=[]
    for i in range(interpol_data.shape[0]):
        for j in range(interpol_data.shape[1]):
            add=[i*spacings[1]+limits[2],j*spacings[0]+limits[0],interpol_data[i][j]]
            output.append(add)
    
    output=pd.DataFrame(data=output,columns=['y','x',name])
    #    output = output[np.isfinite(output[name])]
    #    output = output[output[name] != 0]
        
    
    return output

def replace_line_with_another(df,axis,scalar,lines):
    """
    Replace a row or column of float values with another row or column in a 2D 
    (e.g. [x,y,scalar]) pandas dataframe. Useful for replacing 'bad' rows or
    columns with 'good' values in an adjacent row or column from the dataFrame
    returned by interpolate_to_2D_grid().  
    
    df (dataFrame)
    axis     (list)     axis[0] along which to extract data
    scalar (string)     header name of scalar
    lines    (list)     lines[0] line to use as a replacement, lines[1] line to replace
    """
    
    df=deepcopy(df)
    replaceThis=extractProfile(df,axis[0],axis[1],lines[1])
    withThis=extractProfile(df,axis[0],axis[1],lines[0])
    
    newValues=replaceThis[axis].merge(withThis[[axis[1],scalar]],on=axis[1])
    
    df = df.merge(newValues, on=[axis[0], axis[1]], how='left', suffixes=('_',''))
    df[scalar] = df[scalar].fillna(df[scalar+'_']).astype(float)
    df = df.drop(scalar+'_', axis=1)
    
    return df

def scalar_interpolate_to_grid(x,y,scalar,name,xmin,xmax,ymin,ymax,x_spacing,y_spacing,method,plot):
    
    """
    Args:
         
    x              (1D np.array float64): x components of mesh grid
    y              (1D np.array float64): y components of mesh grid
    scalar         (1D np.array float64): list of scalar values on grid points

    xmin           (int): x min limit for grid
    xmax           (int): x max limit for grid
    ymin           (int): y min limit for grid
    ymax           (int): y max limit for grid
    x_spacing      (int): grid spacing in the x
    y_spacing      (int): grid spacing in the y
    method         (str): choice of 'linear','nearest','cubic'
    plot          (bool): True or false to show plot

    Returns:
    df (dataframe): of interpolated data on specified grid
    """

    xi = np.arange(xmin,xmax,x_spacing)
    yi = np.arange(ymin,ymax,y_spacing)
    

    xi,yi = np.meshgrid(xi,yi)
    
    scalar_comp = griddata((x,y),scalar,(xi,yi),method=method)

    if plot:
        plt.subplot(111)
        plt.imshow(scalar_comp, extent=(xmin,xmax,ymin,ymax), origin='lower')
        
    output=[]
    for i in range(scalar_comp.shape[0]):
        for j in range(scalar_comp.shape[1]):
            add=[i*y_spacing+ymin,j*x_spacing+xmin,scalar_comp[i][j]]
            output.append(add)

    output=pd.DataFrame(data=output,columns=['y','x',name])
    output = output[np.isfinite(output[name])]
    output = output[output[name] != 0]
    
    return output,scalar_comp

def export_3D_points_list(xaxis,yaxis,zaxis,exportPath):
    coordinates=[]
    for i in xaxis:
        for j in yaxis:
            for k in zaxis:
                coordinates.append([i,j,k])
    
    
    points=pd.DataFrame(coordinates,columns=['x','y','z'])
    points.to_csv(exportPath,sep=',',index=False)    
    return points     

def combine_2_2D_plots(df_a,df_b,scalar,limitContours,val_min,val_max,**keyword_parameters):
    
    df_a=deepcopy(df_a)
    df_b=deepcopy(df_b)
    df_a['position']='a'
    df_b['position']='b'
    
    together=pd.concat([df_a,df_b])
    
    f, ax = plt.subplots(1,1, sharex=True, sharey=True)
    ax.set_aspect('equal')
    scalarKey=together[scalar]
    if limitContours:
        ax.tripcolor(together.x,together.y,scalarKey,cmap='seismic',shading='gouraud',vmin=val_min,vmax=val_max)
    else:
        ax.tripcolor(together.x,together.y,scalarKey,cmap='seismic',shading='gouraud')
    

    mappable = ax.collections[0]
    f.colorbar(mappable=mappable)


    if ('add_shapes' in keyword_parameters):
        shapes_file = keyword_parameters['add_shapes'] 
        exec(open(shapes_file).read())

    """
    This code was used for blocking regions in the Sed-PIV article, I left here
    just in case. Which is hopefully not the case.
    """

    
#    f.colorbar(on_mappable_changed(ax))
#    ax.add_patch(
#        patches.Rectangle((0, -5), 400, 5,facecolor='black'))
#    ax.add_patch(
#        patches.Rectangle((0, 0), 400, 2,facecolor='lightgray',hatch='//')) 
#
#    ax.add_patch(
#        patches.Rectangle((0, 185), 400, 15,facecolor='lightgray',hatch='//'))
#    ax.add_patch(
#        patches.Rectangle((0, 0), 40, 205,facecolor='lightgray',hatch='//'))
#    ax.add_patch(
#        patches.Rectangle((40, 105), 27, 100,facecolor='lightgray',hatch='//')) 
#    ax.add_patch(patches.Polygon([[39,80],[67,105],[40,105]], facecolor='lightgray',hatch='//')) 
##    ax.add_patch(
##        patches.Rectangle((-14, 24), 14, 2,facecolor='lightgray',hatch='//'))   
##    ax.add_patch(
##        patches.Rectangle((-150, 0), 136, 2,facecolor='lightgray',hatch='//'))   
##    
###    ax.add_patch(
###        patches.Rectangle((-150, -2), 300, 2,facecolor='gray')) 
##    ax.add_patch(
##        patches.Rectangle((-150, 85), 300, 5,facecolor='lightgray',hatch='//')) 
###    ax.add_patch(
###        patches.Rectangle((-150, 90), 300, 2,facecolor='gray')) 
##    ax.set_yticks([0,15,30,45,60,75,90])
##    ax.set_yticklabels(['0','15','30','45','60','75','90'])
#    ax.set_xlim((0, 400))
#    ax.set_ylim((-5, 205)) 

    f.savefig(r'C:\Users\Jason\Dropbox\PIV_exports\test.png', format='png', dpi=900)

#    f.colorbar(on_mappable_changed(ax))
#    ax.add_patch(
#        patches.Rectangle((0, 0), 12, 24,facecolor='black'))
#    ax.add_patch(
#        patches.Rectangle((12, 0), 2, 26,facecolor='lightgray',hatch='//')) 
#    ax.add_patch(
#        patches.Rectangle((0, 24), 14, 2,facecolor='lightgray',hatch='//'))   
#    ax.add_patch(
#        patches.Rectangle((14, 0), 136, 2,facecolor='lightgray',hatch='//'))   
#    
#    ax.add_patch(
#        patches.Rectangle((0, 0), -12, 24,facecolor='black'))
#    ax.add_patch(
#        patches.Rectangle((-14, 0), 2, 26,facecolor='lightgray',hatch='//')) 
#    ax.add_patch(
#        patches.Rectangle((-14, 24), 14, 2,facecolor='lightgray',hatch='//'))   
#    ax.add_patch(
#        patches.Rectangle((-150, 0), 136, 2,facecolor='lightgray',hatch='//'))   
#    
##    ax.add_patch(
##        patches.Rectangle((-150, -2), 300, 2,facecolor='gray')) 
#    ax.add_patch(
#        patches.Rectangle((-150, 85), 300, 5,facecolor='lightgray',hatch='//')) 
##    ax.add_patch(
##        patches.Rectangle((-150, 90), 300, 2,facecolor='gray')) 
#    ax.set_yticks([0,15,30,45,60,75,90])
#    ax.set_yticklabels(['0','15','30','45','60','75','90'])
#    ax.set_xlim((-150, 150))
#    ax.set_ylim((0, 90)) 

#    f.savefig(r'C:\Users\Jason\Dropbox\PIV_exports\test.png', format='png', dpi=900)
    return together

def check_plots(dictionary,key,vmin,vmax):
    for shot in dictionary:
        cplotter(dictionary[shot][key],key,vmin,vmax)

def cplotter(df,key,x,y,vmin,vmax,**keyword_parameters):

    df=deepcopy(df)
    df = df[[x,y,key]]
    df = df.drop(df[df[key] ==0].index)
    dfMesh = df.pivot(y,x,key)

    fig, ax = plt.subplots()
    conts = ax.contourf(dfMesh.columns.values, dfMesh.index.values, dfMesh.values,100,cmap='seismic',vmin=vmin,vmax=vmax)

    ax.set_aspect('equal')
    
    if ('title' in keyword_parameters):
        title = keyword_parameters['title']
        ax.set_title(title)
        
    if ('xlabel' in keyword_parameters):
        xlabel = keyword_parameters['xlabel']
        ax.set_title(xlabel)

    if ('ylabel' in keyword_parameters):
        ylabel = keyword_parameters['ylabel']
        ax.set_title(ylabel)
        
    v = np.linspace(-.2, 0.2, 9, endpoint=True)

#    ticks=[-0.15,-0.10,-0.05,0,0.05,0.10,0.15]
    fig.colorbar(conts,ax=ax,ticks=v,extend='both')
    
    plt.show()
    return ax


def scalar_3D_plotter(x,y,z,scalar,limits,pane_gray,title):
    
    """plot 3D scatter with associated scalar values all within scalar pandas dataframe
    
    Args:
    df               [dataframe]: containing 3D scatter data to plot
    columns                 list: ['x','y','z','scalar_name']
    limits                  list: [xlow,xhigh,ylow,yhigh,zlow,zhigh]
    pane_gray            booelan: makes pane backgrounds gray for better constrast
    title                 string: title of plot

    Returns:
        plot the 3D scatter
    """
    
    fig = plt.figure()
    ax=fig.gca(projection='3d')
    ax.set_aspect('equal')
    
    if pane_gray:
        ax.w_xaxis.set_pane_color((0, 0, 0, 0.2))
        ax.w_yaxis.set_pane_color((0, 0, 0, 0.2))
        ax.w_zaxis.set_pane_color((0, 0, 0, 0.2))  
        
    if limits:
        ax.set_xlim(limits[0],limits[1])
        ax.set_ylim(limits[2],limits[3])
        ax.set_zlim(limits[4],limits[5])

    if title:
        ax.set_title(title)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    sc=ax.scatter(x, y, z, c=scalar, cmap='seismic')
    plt.colorbar(sc)
    plt.show()
        
    

