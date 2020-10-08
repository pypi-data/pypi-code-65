'''docstring'''
import inp.objects as obj

def zone_cond_unc(inpfile):
    '''returns tuple of conditioned vs unconditioned zones
    (in that order), excluding pl zn'''

    inp = obj.openinp(inpfile)
    zones = obj.get(inp, "ZONE")

    conditioned = obj.filterdictbyvalue(zones, "TYPE", "CONDITIONED")
    unconditioned = obj.filterdictbyvalue(zones, "TYPE", "UNCONDITIONED")
    
    condlist = [x for x in conditioned.keys()]
    
    unclist = [x for x in unconditioned.keys()]
    unclist = [x for x in unclist if "Pl Zn" not in x]
    
    return condlist, unclist


# for testing
#inpfile = 'P:/_Projects/Y150000/Y150248-000/Calculations/Mech/Energy Model/eQuest/11_18 models/Prop/1185 Broadway Prop.inp'
#b = zone_cond_unc(inpfile)
