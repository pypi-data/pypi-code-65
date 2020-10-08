import inp.objects as obj

def zone_list_to_description(flist, zonelist):
    '''correlates zones to space types'''

    spaces = obj.get(flist, "SPACE")
    zones = obj.get(flist, "ZONE")
    
    zone_correlate_list = []
    
    
    for z in zonelist:
        try:
            currentspc = zones[z]['SPACE'].replace("\"","")
            currentspcactivity = spaces[currentspc]['C-ACTIVITY-DESC']
            zone_correlate_list.append((z, currentspcactivity))
        except:
            pass
    
    return zone_correlate_list

'''sample:

inp = '2330 Broadway Base.inp'

zonelist = [
'17FCore Zn (G.C13)',
'1FMCore Zn (G.C10)',
'3FxCore Zn (G.C20)',
'16FCore Zn (G.C15)',
'14FxCore Zn (G.C15)',
'11FCore Zn (G.C20)',
'13FCore Zn (G.C14)',
'12FCore Zn (G.C20)',
'2FCore Zn (G.C19)',
'3FxCore Zn (G.C16)']
z = zone_list_to_description(inp,zonelist)
'''