import numpy as np
import random

# Randomly choose start position to add the overlap_waveform without overlap, and how many mixup operations will happen will happen
def mix_random(base_waveform, overlap_waveform, alpha=0.2, beta=None, n_mixups=2):
    """ High level function that will perform multiple mixups operations on the base_waveform

        If the number of mixups operations chosen is too big, 
        it will perform the maximum number of mixing operations possible

        Args:
            base_waveform {np.ndarray} -- The waveform that will be multiplied by alpha
            overlap_waveform {np.ndarray} -- The waveform that will be multiplied by beta
            alpha {float} -- A weight between 0-1 (default: {0.2})
            beta {float} -- A weight between 0-1 or None (default: {if None, will default to (1 − α)})
            n_mixups {int} -- The maximum number of times that the function will call the mixup method if possible (default: {2})

        Returns:
            np.ndarray -- The resulting waveform
            List of dictionary -- Dictionary with both target labels, the proportion each one kept in the resulting waveform and the start and end frame of all overlaps 
    """
    overlap_waveform_length = len(overlap_waveform)

    available_start_ranges = [
            [0, len(base_waveform)]
        ]

    result_waveform = base_waveform.copy()
    combined_annotations = []
    for i in range(n_mixups):
        # Randomly choose range from available ranges
        range_choice = random.choice(available_start_ranges)

        # Randomly choose start position to add the overlap_waveform into the base. + 1 because the end isnt included in randrange
        base_wave_start = random.randrange(range_choice[0], range_choice[1] - overlap_waveform_length + 1)
        base_wave_stop = base_wave_start + overlap_waveform_length

        # delete availble range used
        del available_start_ranges[available_start_ranges.index(range_choice)]

        # if there is enough remaining space available between range_choice[0] and base_wave_start to mixup a new waveform 
        # create a new avaible start range, which is range_choice[0] to base_wave_start
        if base_wave_start - range_choice[0] >= overlap_waveform_length:
            available_start_ranges.append([range_choice[0], base_wave_start])

        # if there is enough remaining space available between base_wave_stop and range_choice[1] to mixup a new waveform 
        # create a new avaible range
        if range_choice[1] - base_wave_stop >= overlap_waveform_length:
            available_start_ranges.append([base_wave_stop, range_choice[1]])

        wave, annotation = mixup(result_waveform, overlap_waveform, alpha=alpha, beta=beta, base_wave_start=base_wave_start, keep_base_proportion=False)
        result_waveform = wave

        combined_annotations.append(annotation)

        if not available_start_ranges:
            break

    return result_waveform, combined_annotations

def mixup(base_waveform, overlap_waveform, alpha=0.2, beta=None, base_wave_start=0, overlap_wave_start=0, overlap_wave_stop=None, keep_base_proportion=False):
    """ The Mixup method generates a new waveform by computing the linear superposition 
        of two input waveforms, including their labels, i.e.

        This is an implementation of the algorithm below:

        x = α * xi + β * xj, where x is the new waveform, and xi, xj are the two waves beeing mixed
        y = α * yi + β * yj, where y is the new label for x, and yi, yj are the labels of the two waves being mixed

        Note that the default algorithm uses (1 − α) instead of a β. We Give a little more freedom in defining both parameters
        If the user chooses not to define, we fall back to (1 − α)

        This implementation accepts waveforms with different lengths. For this purpose, the input vectors are named as base_waveform and overlap_waveform
        where it is assumed that the base_waveform length >= overlap_waveform length. When base_waveform length > overlap_waveform length the linear
        combination will occur only for the correspoding part of the base_waveform. In case the length of both are equal, the process is simply a linear
        combination of both input vectors in their entirety.

        In any case the resulting waveform will have length equal to the length of the base_waveform and
        be a linear combination of both input vectors with target labels of both input vectors.

        This method returns the resulting waveform and a dictionary dataframe containging 2 rows, one for each label, in the following format: 
        Dictionary:
            'label': a target label
            'start_frame': the starting index of the linear combination
            'end_frame': the ending index of the linear combination
            'label_proportion_kept': The proportion of each label kept. Value can range from 0-1 and represent the α and β values 
        

        Here, the label of base_waveform is always 0 and the label of overlap_waveform is always 1.

        Args:
            base_waveform {np.ndarray} -- The waveform that will be multiplied by alpha
            overlap_waveform {np.ndarray} -- The waveform that will be multiplied by beta
            alpha {float} -- A weight between 0-1 (default: {0.2})
            beta {float} -- A weight between 0-1 or None (default: {if None, will default to (1 − α)})
            base_wave_start {int} -- The start position in the base waveform where the linear combination will start (default: {0})
            overlap_wave_start {int} -- The start position of the overlap waveform where the linear combination will start, everything before will be ignored (default: {0})
            overlap_wave_stop {int} -- The end position of the overlap waveform where the linear combination will stop, everything after will be ignored (default: {None})
            keep_base_proportion {bool} -- If false will multiply base waveform by the alpha weight even for the parts where no mixup ocured (default: {False})

        Returns:
            np.ndarray -- The resulting waveform with length equal to that of the base_waveform
            Dictionary -- Dictionary with both target labels, the proportion each one kept in the resulting waveform and the start and end frame where the combination occurs
    
    """

    assert (0 <= alpha <= 1), "Alpha must be between 0-1" 
    
    if beta is None:
        beta = 1 - alpha
    else:
        assert (0 <= beta <= 1), "Beta must be between 0-1" 

    # Defining all dictionary arguments
    label = []
    start_frame = []
    end_frame = []
    label_proportion_kept = []

    # If the end point of the overlap_waveform is not given, default to the full length of it
    if overlap_wave_stop is None:
        overlap_wave_stop = len(overlap_waveform)

    overlap_segment = overlap_waveform[overlap_wave_start:overlap_wave_stop]

    assert len(overlap_segment) <= len(base_waveform[base_wave_start:]), 'The length of the overlap segment \
        ([overlap_wave_start:overlap_wave_stop]) should be <= to length of the base_waveform from base_wave_start'

    # We devide into 3 segments first, middle and last segment. 
    # The first segment is from the start of the base_waveform to the start of the mixup operation
    # The middle segment is the linear superposition, that is, the mixup operation
    # The last segment is from the end of the mixup operation to the end of the base_waveform
     
    first_segment = []
    # Only create the segment if it exists, that is, if the start is not 0.
    if base_wave_start > 0:
        first_segment = base_waveform[0:base_wave_start]

    point_to_split = base_wave_start + len(overlap_segment)
    # If the overlap waveform length is greater than the legnth of the base waveform 
    if point_to_split > len(base_waveform):
        point_to_split = len(base_waveform)

    # The middle segment is where the linear compbination will occur.
    middle_segment = base_waveform[base_wave_start:point_to_split]
    if len(middle_segment) < len(overlap_segment):
        overlap_segment = overlap_segment[:len(middle_segment)]


    #creating dictionary for both labels
    # print(base_wave_start)
    label.append(0)
    start_frame.append(base_wave_start)
    end_frame.append(point_to_split)
    label_proportion_kept.append(alpha)


    label.append(1)
    start_frame.append(base_wave_start)
    end_frame.append(point_to_split)
    label_proportion_kept.append(beta)

    # Last segment is the remainer of the base waveform outside the linear combination range, if any.
    last_segment = base_waveform[point_to_split:]

    if not keep_base_proportion:
        if len(first_segment) > 0:
            first_segment = alpha * first_segment
        if len(last_segment) > 0:
            last_segment = last_segment * alpha

    # mixup
    combined_waveform = alpha * middle_segment + beta * overlap_segment
    # concatenating all segments together 
    combined_waveform = np.concatenate((first_segment, combined_waveform, last_segment))

    annotation = {
        'label': label,
        'start_frame': start_frame,
        'end_frame': end_frame,
        'label_proportion_kept': label_proportion_kept
    }
    return combined_waveform, annotation