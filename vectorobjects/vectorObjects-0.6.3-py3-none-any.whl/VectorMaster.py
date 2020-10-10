import numpy as np
import operator
import math
import sys


class VectorMaster:
    def _load(self, args):
        """
        All args will be submitted in a tuple format, but we may not be expecting it. Load will check to see what the
        first element is, and use that to determine the load operation
        """
        try:
            # If its a numeric, then it is the expect tuple and we should just return the args
            if isinstance(args[0], (int, float, np.intc, np.float32, np.float64)):
                return args

            # If its a list or tuple then we need to return the first element rather than the tuple containing it
            elif isinstance(args[0], (list, tuple)):
                return args[0]

            # Catch unexpected types
            else:
                sys.exit(f"Found unexpected type {type(args[0])}")

        # If no args supplied, just initialise all values to 0 for each slot
        except IndexError:
            return [0 for _ in range(len(self.__slots__))]

    def _mathematical_operator(self, current_inst, other_inst, operation, rounding=14):
        """
        Update the attributes of the current instance of this class by other instance, either of the same class, a
        constant, or a list/tuple of the same length of the attributes of the current instance.

        :param current_inst: The current class instance
        :param other_inst: Another class instance of the same type as current, an int/float, or a tuple/list of equal
            length to the number of attributes in the current inst
        :param operation: The operator function you wish to perform
        :return: A tuple of the current attributes of the current instance of a class
        :rtype: tuple
        """

        # modify current instances attributes by another vector arrays of the same type
        if isinstance(other_inst, type(current_inst)):
            [setattr(current_inst, current,
                     round(operation(getattr(current_inst, current), getattr(other_inst, other)), rounding))
             for current, other in zip(current_inst.__slots__, other_inst.__slots__)]

        # modify current instances attributes by a constant
        elif isinstance(other_inst, (float, int)):
            [setattr(current_inst, current, round(operation(getattr(current_inst, current), other_inst), rounding))
             for current in current_inst.__slots__]

        # Modify current instances attributes by a value from a list of tuple of equal length of attributes
        elif isinstance(other_inst, (list, tuple)):
            if len(other_inst) == len(current_inst.__slots__):
                [setattr(current_inst, attr, round(operation(getattr(current_inst, attr), v), rounding))
                 for attr, v in zip(current_inst.__slots__, other_inst)]
            else:
                raise ValueError("A list/tuple must be of the same length as the number of attributes of the vector\n"
                                 f"Length of input: {len(other_inst)}\n"
                                 f"Length of attributes: {len(current_inst.__slots__)}")

        return self._return_tuple(current_inst)

    def _negative(self, instance):
        """
        Set all attributes of the current class instance to be the negative
        """
        [setattr(instance, attr, operator.neg(getattr(instance, attr))) for attr in instance.__slots__]
        return self._return_tuple(instance)

    @staticmethod
    def _return_tuple(instance):
        """
        Return a tuple of all the current instances attribute values
        """
        return (getattr(instance, attr) for attr in instance.__slots__)

    @staticmethod
    def _return_list(instance):
        """
        Return a list of all the current instances attribute values
        """
        return [getattr(instance, attr) for attr in instance.__slots__]

    @staticmethod
    def _return_dot_product(current_inst, other_inst):
        """
        Calculate the dot product of two instances of the same class object
        """
        if isinstance(other_inst, type(current_inst)):
            return sum([getattr(current_inst, current) * getattr(other_inst, other)
                        for current, other in zip(current_inst.__slots__, other_inst.__slots__)])
        else:
            raise TypeError(f"Dot product expects two instances of the same class object but found: "
                            f"{type(current_inst)}, {type(other_inst)}")

    def _return_cross_product(self, current_inst, other_inst, rounding=14):
        """
        Calculate the cross product via numpy.cross, round to deal with floating point errors, then update the current
        class's attributes as the cross product
        """
        if isinstance(other_inst, type(current_inst)):
            cross = np.cross(np.array(self._return_list(current_inst)), np.array(self._return_list(other_inst)))
            cross = [round(cp, rounding) for cp in cross]
            [setattr(current_inst, attr, value) for attr, value in zip(current_inst.__slots__, cross)]
            return self._return_tuple(current_inst)
        else:
            raise TypeError(f"Cross product expects two instances of the same class object but found: "
                            f"{type(current_inst)}, {type(other_inst)}")

    def _normalise_attributes(self, instance):
        """
        Normalise the attributes of the class instance
        """
        scale_factor = 1.0 / math.sqrt(sum([getattr(instance, attr) * getattr(instance, attr)
                                            for attr in instance.__slots__]))
        [setattr(instance, attr, getattr(instance, attr) * scale_factor) for attr in instance.__slots__]
        return self._return_tuple(instance)

    def _equality(self, current_inst, other_inst):
        """
        Check if two class instances are equal
        """
        if isinstance(other_inst, type(current_inst)):
            if (np.array(self._return_list(current_inst)) == np.array(self._return_list(other_inst))).all():
                return True
            else:
                return False
        else:
            raise TypeError(f"Equality expects two instances of the same class object but found: "
                            f"{type(current_inst)}, {type(other_inst)}")
