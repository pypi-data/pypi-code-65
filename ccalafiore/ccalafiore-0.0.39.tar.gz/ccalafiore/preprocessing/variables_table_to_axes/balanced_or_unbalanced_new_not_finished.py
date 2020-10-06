import numpy as np
from ...array import samples_in_arr1_are_in_arr2  # , advanced_indexing
from ...combinations import (
    trials_to_conditions, conditions_to_n_conditions, n_conditions_to_combinations, conditions_to_combinations)
from ..axes_to_variables_table import fast_balanced as cc_a2v
from ..reshape import merge_axes, merge_axes_and_add_axes_removing_info_to_axis_receiving


def from_2_arrays(
        array_data_staying,
        array_indexes_removing,
        axis_pooling_input,
        axis_indexes_removing_input,
        axes_inserting_output=None,
        balance=True,
        dtype=None,
        format_and_check=True):

    shape_array_data_staying = np.asarray(array_data_staying.shape)
    n_axes_array_input = shape_array_data_staying.size

    if balance:

        n_indexes_staying = shape_array_data_staying[axis_indexes_removing_input]

        if format_and_check:
            n_axes_array_data_staying = n_axes_array_input

            shape_array_indexes_removing = np.asarray(array_indexes_removing.shape)
            n_axes_array_indexes_removing = shape_array_indexes_removing.size

            # check point 1
            if n_axes_array_data_staying != n_axes_array_indexes_removing:
                raise ValueError('dimension mismatch')

            if axis_indexes_removing_input < 0:
                axis_indexes_removing_input += n_axes_array_input
            if axis_pooling_input < 0:
                axis_pooling_input += n_axes_array_input

            # check point 5
            if axis_pooling_input == axis_indexes_removing_input:
                raise ValueError('axis_pooling_input and axis_indexes_removing_input must be different')

            # check point 2
            indexes_logical = np.arange(n_axes_array_input) != axis_indexes_removing_input
            if np.any(shape_array_data_staying[indexes_logical] !=
                      shape_array_indexes_removing[indexes_logical]):
                raise ValueError('dimension mismatch')

            n_indexes_removing = shape_array_indexes_removing[axis_indexes_removing_input]

            # format axes_inserting_output
            n_axes_inserting_output = n_indexes_removing
            n_axes_array_output = n_axes_array_input + n_axes_inserting_output
            try:
                len(axes_inserting_output)
                axes_inserting_output = np.asarray(axes_inserting_output, dtype=int)
                axes_inserting_output[axes_inserting_output < 0] += n_axes_array_output
                # check point 3
                for a in axes_inserting_output:
                    if np.sum(a == axes_inserting_output) > 1:
                        raise ValueError('axes_inserting_output cannot contain repeated values')
            except TypeError:
                if axes_inserting_output is None:
                    axes_inserting_output = np.arange(n_axes_inserting_output)
                else:
                    if axes_inserting_output < 0:
                        axes_inserting_output += n_axes_array_output
                    axes_inserting_output = np.asarray([axes_inserting_output], dtype=int)

        else:
            n_axes_inserting_output = axes_inserting_output.size
            n_axes_array_output = n_axes_array_input + n_axes_inserting_output

        axes_array_input = np.arange(n_axes_array_input)
        axes_non_axis_indexes_removing_input = axes_array_input[axes_array_input != axis_indexes_removing_input]
        axes_other_array_input = axes_non_axis_indexes_removing_input[
            axes_non_axis_indexes_removing_input != axis_pooling_input]
        n_axes_other_array_input = axes_other_array_input.size

        indexes_array_data_staying = np.empty(n_axes_array_input, dtype=object)
        indexes_array_data_staying[:] = slice(None)

        axis_variables_in_combinations = int(axis_indexes_removing_input > axis_pooling_input)
        axis_combinations_in_combinations = int(not (bool(axis_variables_in_combinations)))

        if n_axes_other_array_input == 0:
            conditions_indexes_removing = trials_to_conditions(
                array_indexes_removing, axis_combinations=axis_combinations_in_combinations)
        elif n_axes_other_array_input > 0:
            indexes_array_indexes_removing = np.copy(indexes_array_data_staying)
            indexes_array_indexes_removing[axes_other_array_input] = 0
            array_indexes_removing_1 = array_indexes_removing[tuple(indexes_array_indexes_removing)]
            conditions_indexes_removing = trials_to_conditions(
                array_indexes_removing_1, axis_combinations=axis_combinations_in_combinations)

        n_conditions_indexes_removing = conditions_to_n_conditions(
            conditions_indexes_removing)
        n_combinations_indexes_removing = int(np.prod(
            n_conditions_indexes_removing))

        combinations_indexes_removing = conditions_to_combinations(
            conditions_indexes_removing,
            axis_combinations=axis_combinations_in_combinations)

        combinations_axes_inserting = n_conditions_to_combinations(
            n_conditions_indexes_removing)

        axis_indexes_removing_output = axis_indexes_removing_input + np.sum(
            axes_inserting_output <= axis_indexes_removing_input)
        axis_pooling_output = axis_pooling_input + np.sum(axes_inserting_output <= axis_pooling_input)
        need_to_check = True
        while need_to_check:
            need_to_check = False
            while axis_indexes_removing_output in axes_inserting_output:
                axis_indexes_removing_output += 1
                need_to_check = True
            while axis_pooling_output in axes_inserting_output:
                axis_pooling_output += 1
                need_to_check = True
            if axis_indexes_removing_output == axis_pooling_output:
                if axis_indexes_removing_input > axis_pooling_input:
                    axis_indexes_removing_output += 1
                elif axis_indexes_removing_input < axis_pooling_input:
                    axis_pooling_output += 1
                need_to_check = True

        axes_array_output = np.arange(n_axes_array_output)
        axes_non_axis_indexes_removing_output = axes_array_output[axes_array_output != axis_indexes_removing_output]
        axes_other_output = axes_non_axis_indexes_removing_output[
            axes_non_axis_indexes_removing_output != axis_pooling_output]
        axes_other_output = axes_other_output[np.logical_not(
            samples_in_arr1_are_in_arr2(axes_other_output, axes_inserting_output))]
        # axes_inserting_output_sorted = np.sort(axes_inserting_output)

        shape_array_output = np.empty(n_axes_array_output, dtype=int)
        shape_array_output[axes_inserting_output] = n_conditions_indexes_removing
        shape_array_output[axis_indexes_removing_output] = n_indexes_staying
        shape_array_output[axis_pooling_output] = (
                shape_array_data_staying[axis_pooling_input] / n_combinations_indexes_removing)
        shape_array_output[axes_other_output] = shape_array_data_staying[axes_other_array_input]
        if dtype is None:
            dtype = array_data_staying.dtype
        array_output = np.empty(shape_array_output, dtype=dtype)

        indexes_output = np.empty(n_axes_array_output, dtype=object)
        indexes_output[:] = slice(None)

        indexes_combinations = np.empty(2, dtype=object)
        indexes_combinations[axis_variables_in_combinations] = slice(None)

        if n_axes_other_array_input == 0:
            for i in range(n_combinations_indexes_removing):
                indexes_output[axes_inserting_output] = combinations_axes_inserting[i]
                indexes_combinations[axis_combinations_in_combinations] = slice(i, i + 1)
                indexes_array_data_staying[axis_pooling_input] = np.all(
                    array_indexes_removing ==
                    combinations_indexes_removing[tuple(indexes_combinations)],
                    axis=axis_variables_in_combinations)
                array_output[tuple(indexes_output)] = array_data_staying[tuple(
                    indexes_array_data_staying)]

        elif n_axes_other_array_input > 0:
            indexes_array_data_staying_j = np.empty(2, dtype=object)
            indexes_array_data_staying_j[axis_variables_in_combinations] = slice(None)

            combinations_axes_other = n_conditions_to_combinations(
                shape_array_data_staying[axes_other_array_input])
            n_combinations_axes_other = combinations_axes_other.shape[0]
            for j in range(n_combinations_axes_other):
                combinations_axes_other_j = combinations_axes_other[j]
                indexes_output[axes_other_output] = combinations_axes_other_j
                indexes_array_data_staying[axes_other_array_input] = combinations_axes_other_j
                indexes_array_indexes_removing[axes_other_array_input] = combinations_axes_other_j
                array_indexes_removing_j = array_indexes_removing[
                    tuple(indexes_array_indexes_removing)]
                array_data_staying_j = array_data_staying[tuple(
                    indexes_array_data_staying)]
                for i in range(n_combinations_indexes_removing):
                    indexes_output[axes_inserting_output] = combinations_axes_inserting[i]
                    indexes_combinations[axis_combinations_in_combinations] = slice(i, i + 1)
                    indexes_array_data_staying_j[axis_combinations_in_combinations] = np.all(
                        array_indexes_removing_j ==
                        combinations_indexes_removing[tuple(indexes_combinations)],
                        axis=axis_variables_in_combinations)
                    array_output[tuple(indexes_output)] = array_data_staying_j[tuple(
                        indexes_array_data_staying_j)]

    else:
        # n_indexes_staying = shape_array_data_staying[axis_indexes_removing_input]

        if format_and_check:
            n_axes_array_data_staying = n_axes_array_input

            shape_array_indexes_removing = np.asarray(array_indexes_removing.shape)
            n_axes_array_indexes_removing = shape_array_indexes_removing.size

            # check point 1
            if n_axes_array_data_staying != n_axes_array_indexes_removing:
                raise ValueError('dimension mismatch')

            if axis_indexes_removing_input < 0:
                axis_indexes_removing_input += n_axes_array_input
            if axis_pooling_input < 0:
                axis_pooling_input += n_axes_array_input

            # check point 5
            if axis_pooling_input == axis_indexes_removing_input:
                raise ValueError('axis_pooling_input and axis_indexes_removing_input must be different')

            # check point 2
            indexes_logical = np.arange(n_axes_array_input) != axis_indexes_removing_input
            if np.any(shape_array_data_staying[indexes_logical] !=
                      shape_array_indexes_removing[indexes_logical]):
                raise ValueError('dimension mismatch')

            n_indexes_removing = shape_array_indexes_removing[axis_indexes_removing_input]

            # format axes_inserting_output
            n_axes_inserting_output = n_indexes_removing
            n_axes_array_output_object = n_axes_inserting_output
            try:
                len(axes_inserting_output)
                axes_inserting_output = np.asarray(axes_inserting_output, dtype=int)
                axes_inserting_output[axes_inserting_output < 0] += n_axes_array_output_object
                # check point 3
                for a in axes_inserting_output:
                    if np.sum(a == axes_inserting_output) > 1:
                        raise ValueError('axes_inserting_output cannot contain repeated values')

            except TypeError:
                if axes_inserting_output is None:
                    axes_inserting_output = np.arange(n_axes_inserting_output)
                else:
                    if axes_inserting_output < 0:
                        axes_inserting_output += n_axes_array_output_object
                    axes_inserting_output = np.asarray([axes_inserting_output], dtype=int)

            if dtype is None:
                dtype = array_data_staying.dtype

        else:
            n_axes_inserting_output = axes_inserting_output.size
            n_axes_array_output_object = n_axes_inserting_output

        axes_array_input = np.arange(n_axes_array_input)
        axes_non_axis_indexes_removing_input = axes_array_input[axes_array_input != axis_indexes_removing_input]
        axes_other_array_input = axes_non_axis_indexes_removing_input[
            axes_non_axis_indexes_removing_input != axis_pooling_input]
        n_axes_other_array_input = axes_other_array_input.size

        axis_variables_in_combinations = int(axis_indexes_removing_input > axis_pooling_input)
        axis_combinations_in_combinations = int(not (bool(axis_variables_in_combinations)))

        if n_axes_other_array_input == 0:
            array_indexes_removing_object = array_indexes_removing
            conditions_indexes_removing_object = trials_to_conditions(
                array_indexes_removing_object, axis_combinations=axis_combinations_in_combinations)
        elif n_axes_other_array_input > 0:

            array_indexes_removing_flat = merge_axes_and_add_axes_removing_info_to_axis_receiving(
                array_indexes_removing,
                axes_other_array_input,
                axis_pooling_input,
                axis_indexes_removing_input,
                indexes_inserting_output=np.arange(n_axes_other_array_input),
                dtype=array_indexes_removing.dtype)

            indexes = np.empty(2, dtype=object)
            indexes[axis_combinations_in_combinations] = slice(0, None, 1)
            indexes[axis_variables_in_combinations] = slice(
                n_axes_other_array_input, n_axes_other_array_input + 2, 1)
            array_indexes_removing_object = array_indexes_removing_flat[tuple(indexes)]

            indexes[axis_variables_in_combinations] = slice(0, n_axes_other_array_input, 1)
            array_indexes_removing_not_object = array_indexes_removing_flat[tuple(indexes)]

            array_data_staying = merge_axes(
                array_data_staying,
                axes_other_array_input,
                axis_pooling_input,
                dtype=dtype)

            conditions_indexes_removing_object = trials_to_conditions(
                array_indexes_removing_object, axis_combinations=axis_combinations_in_combinations)

            conditions_indexes_removing_not_object = trials_to_conditions(
                array_indexes_removing_not_object, axis_combinations=axis_combinations_in_combinations)

            if axis_pooling_input < axis_indexes_removing_input:
                axis_pooling_input = 0
                axis_indexes_removing_input = 1
            elif axis_pooling_input > axis_indexes_removing_input:
                axis_pooling_input = 1
                axis_indexes_removing_input = 0

            # n_conditions_indexes_removing_not_object = shape_array_indexes_removing[
            #     axes_other_array_input]

            # combinations_axes_inserting_not_object = n_conditions_to_combinations(
            #     n_conditions_indexes_removing_not_object)

        n_conditions_indexes_removing_object = conditions_to_n_conditions(
            conditions_indexes_removing_object)
        n_combinations_indexes_removing_object = int(np.prod(
            n_conditions_indexes_removing_object))

        combinations_indexes_removing_object = conditions_to_combinations(
            conditions_indexes_removing_object,
            axis_combinations=axis_combinations_in_combinations)

        combinations_axes_inserting_object = n_conditions_to_combinations(
            n_conditions_indexes_removing_object)

        # axes_array_output_object = np.arange(n_axes_array_output_object)
        shape_array_output_object = np.empty(n_axes_array_output_object, dtype=int)
        shape_array_output_object[axes_inserting_output] = n_conditions_indexes_removing_object
        array_output = np.empty(shape_array_output_object, dtype=object)

        n_axes_array_input = 2
        indexes_array_data_staying = np.empty(n_axes_array_input, dtype=object)
        indexes_array_data_staying[:] = slice(None)

        indexes_output_object = np.empty(n_axes_array_output_object, dtype=object)

        indexes_combinations = np.empty(2, dtype=object)
        indexes_combinations[axis_variables_in_combinations] = slice(None)

        # if n_axes_other_array_input == 0:
        for i in range(n_combinations_indexes_removing_object):
            indexes_output_object[axes_inserting_output] = combinations_axes_inserting_object[i]
            indexes_combinations[axis_combinations_in_combinations] = slice(i, i + 1)
            indexes_array_data_staying[axis_pooling_input] = np.all(
                array_indexes_removing_object ==
                combinations_indexes_removing_object[tuple(indexes_combinations)],
                axis=axis_variables_in_combinations)
            array_output[tuple(indexes_output_object)] = from_2_arrays(
                array_data_staying[tuple(indexes_array_data_staying)],
                array_indexes_removing_not_object[tuple(indexes_array_data_staying)],
                axis_pooling_input,
                axis_indexes_removing_input,
                axes_inserting_output=axes_other_array_input,
                balance=True,
                dtype=dtype,
                format_and_check=False)

        # if n_axes_other_array_input > 0:

        # elif n_axes_other_array_input > 0:
        #
        #     shape_array_output = np.copy(shape_array_data_staying)
        #     shape_array_output[axis_pooling_input] = 0 # (
        #             # shape_array_data_staying[axis_pooling_input] / n_combinations_indexes_removing)
        #
        #     dtype = array_data_staying.dtype
        #     array_output_tmp = np.empty(shape_array_output, dtype=dtype)
        #
        #     for i in range(n_combinations_indexes_removing):
        #         indexes_output_object[axes_inserting_output] = combinations_axes_inserting[i]
        #         array_output[tuple(indexes_output_object)] = np.copy(array_output_tmp)
        #
        #     indexes_output = np.empty(n_axes_array_input, dtype=object)
        #     indexes_output[:] = slice(None)
        #
        #     indexes_array_data_staying_j = np.empty(2, dtype=object)
        #     indexes_array_data_staying_j[axis_variables_in_combinations] = slice(None)
        #
        #     indexes_array_indexes_removing = np.copy(indexes_array_data_staying)
        #
        #     combinations_axes_other = n_conditions_to_combinations(
        #         shape_array_data_staying[axes_other_array_input])
        #     n_combinations_axes_other = combinations_axes_other.shape[0]
        #     for j in range(n_combinations_axes_other):
        #         combinations_axes_other_j = combinations_axes_other[j]
        #         indexes_output[axes_other_array_input] = combinations_axes_other_j
        #         indexes_output_tuple = tuple(indexes_output)
        #         indexes_array_data_staying[axes_other_array_input] = combinations_axes_other_j
        #         indexes_array_indexes_removing[axes_other_array_input] = combinations_axes_other_j
        #         array_indexes_removing_j = array_indexes_removing[
        #             tuple(indexes_array_indexes_removing)]
        #         array_data_staying_j = array_data_staying[tuple(
        #             indexes_array_data_staying)]
        #         for i in range(n_combinations_indexes_removing):
        #             indexes_output_object[axes_inserting_output] = combinations_axes_inserting[i]
        #             indexes_combinations[axis_combinations_in_combinations] = slice(i, i + 1)
        #             indexes_array_data_staying_j[axis_combinations_in_combinations] = np.all(
        #                 array_indexes_removing_j ==
        #                 combinations_indexes_removing[tuple(indexes_combinations)],
        #                 axis=axis_variables_in_combinations)
        #
        #             array_output[tuple(indexes_output_object)][indexes_output_tuple] = np.append(
        #                 array_output[tuple(indexes_output_object)][indexes_output_tuple],
        #                 array_data_staying_j[tuple(indexes_array_data_staying_j)],
        #                 axis=axis_pooling_input)
                    # array_output[tuple(indexes_output_object)][indexes_output_tuple] = array_data_staying_j[
                    #     tuple(indexes_array_data_staying_j)]

    return array_output


def from_2_arrays_advanced(
        array_data_staying,
        array_indexes_removing,
        axis_pooling_input,
        axis_indexes_removing_input,
        indexes_removing=None,
        axes_inserting_output=None,
        indexes_staying=None,
        balance=True,
        dtype=None,
        format_and_check=True):

    # Notes:
    # 1) uses the efficient function slice for indexes;
    # 2) it splits the array in two arrays first: array_indexes_removing and array_data_staying.
    #    Then, it makes the array output from those two arrays;
    # 3) it assumes that the numbers of samples (or trials) in the axis_pooling_input for all combinations
    #    of indexes_removing are equal;
    # 4) it does not assumes that the order of samples (or trials) in the axis_pooling_input are is the same
    #    in each combination of variables' axes. The order is based on the order of the combinations
    #    of variables' conditions in axis_indexes_removing_input. In other words, the samples can be in random order
    #    (or in different order) in each combinations of variables axes/conditions.

    # Input requirements:
    # 1) the numbers of axes of the two arrays must be equal;
    # 2) the shapes of the 2 arrays must be equal, except for the axis_variable_table,
    #    i.e. the axis that contains the variables of the tables;
    # 3) axes_inserting_output cannot contain repeated values;
    # 4) indexes_removing cannot contain repeated values;
    # 5) shapes of axes_inserting_output and indexes_removing must be equal
    # 6) axis_pooling_input != axis_indexes_removing_input
    # 7) the numbers of samples (or trials) in the axis_pooling_input for all combinations
    #    of indexes_removing are equal

    # Import requirements:
    # 1) import numpy as np
    # 2) from ccalafiore.combinations import n_conditions_to_combinations
    # 3) from ccalafiore.combinations import trials_to_conditions
    # 4) from ccalafiore.combinations import conditions_to_n_conditions
    # 5) from ccalafiore.combinations import conditions_to_combinations
    # 6) from ccalafiore.array import samples_in_arr1_are_in_arr2

    # from ccalafiore.combinations import \
    #     trials_to_conditions, conditions_to_n_conditions, n_conditions_to_combinations, conditions_to_combinations
    # from ccalafiore.array import samples_in_arr1_are_in_arr2

    shape_array_data_staying = np.asarray(array_data_staying.shape)
    n_axes_array_data_staying = shape_array_data_staying.size
    n_variables_table_in_array_data_staying = shape_array_data_staying[axis_indexes_removing_input]
    variables_table_in_array_data_staying = np.arange(n_variables_table_in_array_data_staying)

    shape_array_indexes_removing = np.asarray(array_indexes_removing.shape)
    n_axes_array_indexes_removing = shape_array_indexes_removing.size
    n_variables_table_in_array_indexes_removing = shape_array_indexes_removing[axis_indexes_removing_input]
    variables_table_in_array_indexes_removing = np.arange(n_variables_table_in_array_indexes_removing)

    if format_and_check:
        # check point 1
        if n_axes_array_data_staying != n_axes_array_indexes_removing:
            raise ValueError('dimension mismatch')
        else:
            n_axes_array_input = n_axes_array_data_staying

        if axis_indexes_removing_input < 0:
            axis_indexes_removing_input += n_axes_array_input
        if axis_pooling_input < 0:
            axis_pooling_input += n_axes_array_input

        # check point 6
        if axis_pooling_input == axis_indexes_removing_input:
            raise ValueError('axis_pooling_input and axis_indexes_removing_input must be different')

        # check point 2
        indexes_logical = np.arange(n_axes_array_input) != axis_indexes_removing_input
        if np.any(shape_array_data_staying[indexes_logical] != shape_array_indexes_removing[indexes_logical]):
            raise ValueError('dimension mismatch')

        n_variables_table_in_array_data_staying = shape_array_data_staying[axis_indexes_removing_input]
        variables_table_in_array_data_staying = np.arange(n_variables_table_in_array_data_staying)

        n_variables_table_in_array_indexes_removing = shape_array_indexes_removing[axis_indexes_removing_input]
        variables_table_in_array_indexes_removing = np.arange(n_variables_table_in_array_indexes_removing)

        # format indexes_removing
        try:
            n_indexes_removing = len(indexes_removing)
            indexes_removing = np.asarray(indexes_removing, dtype=int)
            indexes_removing[indexes_removing < 0] += \
                n_variables_table_in_array_indexes_removing
            # check point 4
            if np.sum(indexes_removing[0] == indexes_removing) > 1:
                raise ValueError('indexes_removing cannot contain repeated values')
        except TypeError:
            if indexes_removing is None:
                indexes_removing = np.arange(n_variables_table_in_array_indexes_removing)
                n_indexes_removing = n_variables_table_in_array_indexes_removing
            else:
                if indexes_removing < 0:
                    indexes_removing += n_variables_table_in_array_indexes_removing
                indexes_removing = np.asarray([indexes_removing], dtype=int)
                n_indexes_removing = 1

        # format indexes_staying
        try:
            n_indexes_staying = len(indexes_staying)
            indexes_staying = np.asarray(indexes_staying, dtype=int)
            indexes_staying[indexes_staying < 0] += n_variables_table_in_array_data_staying
        except TypeError:
            if indexes_staying is None:
                indexes_staying = np.arange(n_variables_table_in_array_data_staying)
                n_indexes_staying = n_variables_table_in_array_data_staying
            else:
                if indexes_staying < 0:
                    indexes_staying += n_variables_table_in_array_data_staying
                indexes_staying = np.asarray([indexes_staying], dtype=int)
                n_indexes_staying = 1

        # format axes_inserting_output
        n_axes_inserting_output = n_indexes_removing
        if balance:
            n_axes_array_output = n_axes_array_input + n_axes_inserting_output
        else:
            n_axes_array_output = n_axes_inserting_output
        try:
            n_axes_inserting_output = len(axes_inserting_output)
            axes_inserting_output = np.asarray(axes_inserting_output, dtype=int)
            axes_inserting_output[axes_inserting_output < 0] += n_axes_array_output
            # check point 3
            if np.sum(axes_inserting_output[0] == axes_inserting_output) > 1:
                raise ValueError('axes_inserting_output cannot contain repeated values')
            # check point 5
            if n_indexes_removing != n_axes_inserting_output:
                raise ValueError('Shapes of axes_inserting_output and indexes_removing must be equal')
        except TypeError:
            if axes_inserting_output is None:
                axes_inserting_output = np.arange(n_axes_inserting_output)
            else:
                if axes_inserting_output < 0:
                    axes_inserting_output += n_axes_array_output
                axes_inserting_output = np.asarray([axes_inserting_output], dtype=int)
                n_axes_inserting_output = 1
                # check point 5
                if n_indexes_removing != n_axes_inserting_output:
                    raise ValueError('Shapes of axes_inserting_output and indexes_removing must be equal')
    else:
        n_indexes_staying = indexes_staying.size
        n_indexes_removing = indexes_removing.size

    indexes = None
    if ((n_indexes_staying != n_variables_table_in_array_data_staying) or
            np.any(indexes_staying != variables_table_in_array_data_staying)):

        indexes = np.empty(n_axes_array_data_staying, dtype=object)
        indexes[:] = slice(None)
        indexes[axis_indexes_removing_input] = indexes_staying
        array_data_staying = array_data_staying[tuple(indexes)]

    if ((n_indexes_removing != n_variables_table_in_array_indexes_removing) or
            np.any(indexes_removing != variables_table_in_array_indexes_removing)):

        if indexes is None:
            indexes = np.empty(n_axes_array_indexes_removing, dtype=object)
            indexes[:] = slice(None)
        indexes[axis_indexes_removing_input] = indexes_removing
        array_indexes_removing = array_indexes_removing[tuple(indexes)]

    array_output = from_2_arrays(
        array_data_staying,
        array_indexes_removing,
        axis_pooling_input,
        axis_indexes_removing_input,
        axes_inserting_output=axes_inserting_output,
        balance=balance,
        dtype=dtype,
        format_and_check=False)

    return array_output


def from_1_array(
        array_input,
        axis_pooling_input,
        axis_indexes_removing_input,
        indexes_removing,
        axes_inserting_output=None,
        indexes_staying=None,
        balance=True,
        dtype=None,
        format_and_check=True):

    # Notes:
    # 1) uses the efficient function slice for indexes;
    # 2) it splits the array in two arrays first: array_indexes_removing and array_data_staying.
    #    Then, it makes the array output from those two arrays;
    # 3) the numbers of samples (or trials) in the axis_pooling_input for all combinations
    #    of indexes_removing have to be equal;
    # 4) it does not assumes that the order of samples (or trials) in the axis_pooling_input are is the same
    #    in each combination of variables' axes. The order is based on the order of the combinations
    #    of variables' conditions in axis_indexes_removing_input. In other words, the samples can be in random order
    #    (or in different order) in each combinations of variables axes/conditions.

    # Input requirements:
    # 1) axes_inserting_output cannot contain repeated values;
    # 2) indexes_removing cannot contain repeated values;
    # 3) shapes of axes_inserting_output and indexes_removing must be equal
    # 4) axis_pooling_input != axis_indexes_removing_input
    # 5) the numbers of samples (or trials) in the axis_pooling_input for all combinations
    #    of indexes_removing are equal

    # Import requirements:
    # 1) import numpy as np
    # 2) from ccalafiore.combinations import n_conditions_to_combinations
    # 3) from ccalafiore.combinations import trials_to_conditions
    # 4) from ccalafiore.combinations import conditions_to_n_conditions
    # 5) from ccalafiore.combinations import conditions_to_combinations
    # 6) from ccalafiore.array import samples_in_arr1_are_in_arr2

    # from ccalafiore.combinations import \
    #     trials_to_conditions, conditions_to_n_conditions, n_conditions_to_combinations, conditions_to_combinations
    # from ccalafiore.array import samples_in_arr1_are_in_arr2

    shape_array_input = np.asarray(array_input.shape)
    n_axes_array_input = shape_array_input.size
    n_variables_table_input = shape_array_input[axis_indexes_removing_input]
    variables_table_input = np.arange(n_variables_table_input)

    if format_and_check:
        if axis_indexes_removing_input < 0:
            axis_indexes_removing_input += n_axes_array_input
        if axis_pooling_input < 0:
            axis_pooling_input += n_axes_array_input

        # check point 4
        if axis_pooling_input == axis_indexes_removing_input:
            raise ValueError('axis_pooling_input and axis_indexes_removing_input must be different')

        # format indexes_removing
        try:
            n_indexes_removing = len(indexes_removing)
            indexes_removing = np.asarray(indexes_removing, dtype=int)
            indexes_removing[indexes_removing < 0] += n_variables_table_input
            # check point 2
            if np.sum(indexes_removing[0] == indexes_removing) > 1:
                raise ValueError('indexes_removing cannot contain repeated values')
        except TypeError:
            if indexes_removing < 0:
                indexes_removing += n_variables_table_input
            indexes_removing = np.asarray([indexes_removing], dtype=int)
            n_indexes_removing = 1

        # format indexes_staying
        try:
            n_indexes_staying = len(indexes_staying)
            indexes_staying = np.asarray(indexes_staying, dtype=int)
            indexes_staying[indexes_staying < 0] += n_variables_table_input
        except TypeError:
            if indexes_staying is None:
                indexes_staying = variables_table_input[np.logical_not(
                    samples_in_arr1_are_in_arr2(variables_table_input, indexes_removing))]
                n_indexes_staying = indexes_staying.size
            else:
                if indexes_staying < 0:
                    indexes_staying += n_variables_table_input
                indexes_staying = np.asarray([indexes_staying], dtype=int)
                n_indexes_staying = 1

        # format axes_inserting_output
        n_axes_inserting_output = n_indexes_removing
        if balance:
            n_axes_array_output = n_axes_array_input + n_axes_inserting_output
        else:
            n_axes_array_output = n_axes_inserting_output
        try:
            n_axes_inserting_output = len(axes_inserting_output)
            axes_inserting_output = np.asarray(axes_inserting_output, dtype=int)
            axes_inserting_output[axes_inserting_output < 0] += n_axes_array_output
            # check point 1
            if np.sum(axes_inserting_output[0] == axes_inserting_output) > 1:
                raise ValueError('axes_inserting_output cannot contain repeated values')
            # check point 3
            if n_indexes_removing != n_axes_inserting_output:
                raise ValueError('Shapes of axes_inserting_output and indexes_removing must be equal')
        except TypeError:
            if axes_inserting_output is None:
                axes_inserting_output = np.arange(n_axes_inserting_output)
            else:
                if axes_inserting_output < 0:
                    axes_inserting_output += n_axes_array_output
                axes_inserting_output = np.asarray([axes_inserting_output], dtype=int)
                n_axes_inserting_output = 1
                # check point 3
                if n_indexes_removing != n_axes_inserting_output:
                    raise ValueError('Shapes of axes_inserting_output and indexes_removing must be equal')
    else:
        n_indexes_staying = indexes_staying.size
        n_indexes_removing = indexes_removing.size

    indexes = np.empty(n_axes_array_input, dtype=object)
    indexes[:] = slice(None)
    if ((n_indexes_staying != n_variables_table_input) or
            np.any(indexes_staying != variables_table_input)):
        indexes[axis_indexes_removing_input] = indexes_staying
    array_data_staying = array_input[tuple(indexes)]

    if ((n_indexes_removing != n_variables_table_input) or
            np.any(indexes_removing != variables_table_input)):
        indexes[axis_indexes_removing_input] = indexes_removing
    else:
        indexes[axis_indexes_removing_input] = slice(None)
    array_indexes_removing = array_input[tuple(indexes)]
    del array_input

    array_output = from_2_arrays(
        array_data_staying,
        array_indexes_removing,
        axis_pooling_input,
        axis_indexes_removing_input,
        axes_inserting_output=axes_inserting_output,
        balance=balance,
        dtype=dtype,
        format_and_check=False)

    return array_output
