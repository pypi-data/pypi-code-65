def convert_to_8bit(im_data, im_profile):
    # Convert uint16 to uint8 by bitshifting
    im_data = (im_data >> 8).astype('uint8')
    
    im_profile['dtype'] = 'uint8'

    return im_data, im_profile
