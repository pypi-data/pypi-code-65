import unittest
import math
from randcsv import value_generators as vg


class TestGenerateString(unittest.TestCase):

    def test_output_length(self):
        value = vg.generate_token(4)
        self.assertTrue(str(value))

        with self.assertRaises(ValueError):
            vg.generate_token(-1)


class TestGenerateInteger(unittest.TestCase):

    def test_output_length(self):
        value = vg.generate_integer(4)
        self.assertTrue(int(value))

        with self.assertRaises(ValueError):
            vg.generate_integer(-1)


class TestGenerateFloat(unittest.TestCase):

    def test_output_length(self):
        value = vg.generate_float(4)
        self.assertTrue(float(value))

        with self.assertRaises(ValueError):
            vg.generate_float(-1)


class TestGeneratorFactory(unittest.TestCase):

    def test_factory_returns_correct_generator(self):
        func = vg.generator_factory("token")
        self.assertEqual(func, vg.generate_token)
        func = vg.generator_factory("integer")
        self.assertEqual(func, vg.generate_integer)
        func = vg.generator_factory("float")
        self.assertEqual(func, vg.generate_float)

    def test_factory_raises(self):
        with self.assertRaises(ValueError):
            vg.generator_factory("toke")


class TestGenerateValue(unittest.TestCase):

    def test_generator_correct_value_is_generated(self):
        # 0 = "Regular values",
        # 1 = nan,
        # 2 = None
        all_value_types_sorted = [
            (0, 0.2),
            (1, 0.3),
            (2, 0.5),
        ]
        data_types = ["integer", "float", "token"]
        byte_size = 32

        for _ in range(10):
            reg_count = 0
            nan_count = 0
            empty_count = 0
            for _ in range(10000):
                value = vg.generate_value(all_value_types_sorted, data_types, byte_size)
                if value is None:
                    empty_count += 1
                else:
                    try:
                        if math.isnan(value):
                            nan_count += 1
                        else:
                            reg_count += 1
                    except TypeError:
                        reg_count += 1

            tolerable_error = 0.10
            self.assertLess(abs(reg_count - 2000), 2000 * tolerable_error)
            self.assertLess(abs(nan_count - 3000), 3000 * tolerable_error)
            self.assertLess(abs(empty_count - 5000), 5000 * tolerable_error)

    def test_generator_raised(self):
        all_value_types_sorted = [
            (3, 0.5),
            (4, 0.5),
            (5, 0.5),
        ]
        data_types = ["toke"]
        byte_size = 32

        with self.assertRaises(ValueError):
            vg.generate_value(all_value_types_sorted, data_types, byte_size)
