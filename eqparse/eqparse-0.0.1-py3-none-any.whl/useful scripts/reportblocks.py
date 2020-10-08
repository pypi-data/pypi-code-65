def write_blocks(varname, varnum):
    blockname = varname + "_varnum_" + "_blk"
    blocktext = '''
    "{0}" = REPORT-BLOCK    
   VARIABLE-TYPE    = "{1}"
   VARIABLE-LIST    = ( {2} )
   ..
    '''.format(blockname, varname, varnum)
    print (blocktext)
    return blocktext
    
    
def assign_blocks(objlist):
    start_text = 'REPORT-BLOCK    = ('    
    middle_text = ''
    for obj in objlist:
        blockname = obj + "_varnum_" + "_blk"
        middle_text  += '"' + blockname + '"' + ", \n"

    middle_text = middle_text[0:-3] + " )"
    end_text = '\n ..'
    
    print (start_text + middle_text + end_text)
        
        
        
