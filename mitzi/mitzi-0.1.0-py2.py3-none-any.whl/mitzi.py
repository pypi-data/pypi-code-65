from PIL import Image, ImageDraw


def check(warp_colour, weft_colour, threadwidth, size):
    warp = Image.new('RGBA', size, warp_colour)
    weft = Image.new('RGBA', size, weft_colour)
    return draw_weave(warp, weft, threadwidth, size)


def houndstooth(colour1, colour2, threadwidth, size):
    warp = Image.new('RGBA', size)
    weft = Image.new('RGBA', size)
    warp_draw = ImageDraw.Draw(warp)
    weft_draw = ImageDraw.Draw(weft)
    threads = [colour1] * threadwidth * 4 + [colour2] * 4 * threadwidth
    total_threads = len(threads)
    for index in range(size[0]):
        warp_draw.line((index, 0, index, size[1]), fill=threads[index % total_threads])
    for index in range(size[1]):
        weft_draw.line((0, index, size[0], index), fill=threads[index % total_threads])
    mask = create_mask(size, [1, 1] * threadwidth + [0, 0] * threadwidth, 1, 1)
    warp.paste(weft, mask=mask)
    return warp


def draw_weave(warp, weft, threadwidth, size):
    """
    Given two images, produce an image representing those two images woven together
    """
    pattern = [0] * threadwidth + [1] * threadwidth
    mask = create_mask(size, pattern, threadwidth, threadwidth)
    warp.paste(weft, mask=mask)
    return warp


def create_mask(size, pattern, step_at, step_by):
    """
    Creates a mask to be used in compositing the warp and weft images into
    one woven image.

    The mask returned is a binary mode image of black and white checkerboard,
    with each check being 1 pixel.

    size is a 2-tuple representing width and height (as used in PIL)
    """
    width, height = size
    mask = Image.new('1', size)
    mask_data = []
    current_pattern = pattern
    pattern_length = len(pattern)
    # PIL image data for putting like this is a 1d array
    for i in range(height):
        if i != 0 and i % step_at == 0:
            current_pattern = rotate(step_by, current_pattern)
        mask_data += (current_pattern * (width//pattern_length)) + current_pattern[:width % pattern_length]
    mask.putdata(mask_data)
    return mask


def rotate(n, pattern):
    return pattern[n:] + pattern[:n]


presets = {
    'check': check,
    'houndstooth': houndstooth
}
