def num_bands(im_data):
    return len(im_data)

def convert_to_rgb(im_data, im_profile):
    # Slice im_data to only include bands 1...bands_to_read
    bands_to_read = range(0, min(num_bands(im_data), 3))
    im_data = im_data[bands_to_read, ]

    im_profile['count'] = len(im_data)

    return im_data, im_profile
