import pandas as pd
import inp.objects as objects
import inp.polygon_areas as polygon_areas

def space_zone_rpts(inpfile, csvout):
    '''
    returns csv of unconditioned zones vs conditioned zones and
    their areas and multipliers. a simplified replacement for 
    some reasons to use spaceloads.csv that has a better handle on
    unconditioned zones. can also add to this or refactor; 
    it's pretty hacky right now.
    '''

    flist = objects.openinp(inpfile)
    #get some objects
    spaces = objects.get(flist, "SPACE")
    zones = objects.get(flist, "ZONE")
    polygons = objects.get(flist, "POLYGON")
    floors = objects.get(flist, "FLOOR")
    

    #make a bunch of tuples you want to filter by
    tup_zn_type = objects.objectvaluetuple(zones, "TYPE")
    tup_zn_spc = objects.objectvaluetuple(zones, "SPACE")
    tup_spc_type = objects.objectvaluetuple(spaces, "C-ACTIVITY-DESC")
    tup_spc_spcmult = objects.objectvaluetuple(spaces, "MULTIPLIER", 1)

    tup_spc_flmult = objects.objectvaluetuple(dictname=spaces, 
                                              innervalue="MULTIPLIER",
                                              nullval=1,
                                              fromparent=True,
                                              parentdict=floors)
                                            
    tup_spc_area = list(polygon_areas.area_spc_dict(spaces, polygon_areas.getpolyarea(polygons)).items())

    plen_zn_types = []
    for f in tup_zn_type:
        first = f[0]
        second = f[1]
        if "Pl Zn" in f[0]:
            second = "PLENUM"
        plen_zn_types.append((first, second))

    #make dfs
    df_zn_type = pd.DataFrame(plen_zn_types, columns=["ZoneName", "ConditionedStatus"])
    df_zn_spc = pd.DataFrame(tup_zn_spc, columns=["ZoneName", "SpaceName"])
    df_spc_type = pd.DataFrame(tup_spc_type, columns=["SpaceName", "SpaceType"])
    df_spc_spcmult = pd.DataFrame(tup_spc_spcmult, columns=["SpaceName", "SpaceMultiplier"])
    df_spc_flmult = pd.DataFrame(tup_spc_flmult, columns=["SpaceName", "FloorMultiplier"])
    df_spc_area = pd.DataFrame(tup_spc_area, columns=["SpaceName", "SpaceArea"])
    
    #make merged df
    spacedf = pd.concat(
        [df_spc_type, 
         df_spc_area, 
         df_spc_spcmult, 
         df_spc_flmult],
        join='inner', 
        axis=1)
    
    spacedf = spacedf.loc[:, ~spacedf.columns.duplicated()]
    zonedf = pd.concat(
        [df_zn_spc, 
         df_zn_type], 
        join='inner', 
        axis=1)
    
    zonedf = zonedf.loc[:, ~zonedf.columns.duplicated()]
    concatdf = pd.merge(spacedf, zonedf, how='inner', on='SpaceName')
    
    with open(csvout, 'w') as f:
        concatdf.to_csv(f, index=False)

    return concatdf
