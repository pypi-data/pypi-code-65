def parse_nrds_id(value):
    
    # evaluate if value is string
    if isinstance(value, str):
        
        # if so, 0-pad value to 9 characters (can produce strs of len 9+)
        nrds_id = str.zfill(value,9)
        
        # verify the resulting str is exactly 9 chars and contains no non-numeric chars
        if len(nrds_id) == 9 and nrds_id.isdigit():
            
            return nrds_id

        # if != 9 chars or contains non-numeric chars, error
        else:
            
            return f'invalid nrds id! input value: {value}'

    # else evaluate if value is integer
    elif isinstance(value, int):
        
        # convert it to a str and 0-pad value to 9 characters (can produce strs of len 9+)
        nrds_id = str.zfill(str(value),9)
        
        # if != 9 chars, error
        if len(nrds_id) != 9:
            
            return f'error: invalid nrds id! input value: {value}'
        
        else:
            return nrds_id
    
    # else value is not str or int, error
    else:
        return f'error: invalid nrds id! iput type - {value}, {type(value)}'
