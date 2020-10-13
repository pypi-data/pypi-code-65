import unittest
from .text import Chevrons


class TestChevronize(unittest.TestCase):

    def test_chevronize_regular_quoted_string(self):
        """
        Testing on regular string with single
        substring with double quotes around

        """
        original_string = 'This is "quoted"'
        self.assertEqual(
            'This is «quoted»', Chevrons(original_string).apply()
        )

    def test_simple_string(self):
        """
        Testing on simple string without
        quotes

        """
        original_string = 'No quotes here'
        self.assertEqual(
            'No quotes here', Chevrons(original_string).apply()
        )

    def test_chevronize_two_quotes(self):
        """
        Testing on regular string with two
        substrings with double quotes around

        """
        original_string = 'These are "first" and "second" quotes'
        self.assertEqual(
            'These are «first» and «second» quotes', Chevrons(original_string).apply()
        )

    def test_chevronize_regular_string_with_single_quotes(self):
        """
        Testing on regular string with single
        substring with single quotes around

        """
        original_string = "This is 'quoted'"
        self.assertEqual(
            "This is «quoted»", Chevrons(original_string).apply()
        )

    def test_chevronize_two_quotes_with_single_quotes(self):
        """
        Testing on regular string with two
        substrings with single quotes around

        """
        original_string = "These are 'first' and 'second' quotes"
        self.assertEqual(
            "These are «first» and «second» quotes", Chevrons(original_string).apply()
        )

    def test_unquote_regular_string_with_single_quote_unpaired(self):
        """
        Testing on regular string with single
        substring with unpaired single quote

        """
        original_string = "This is 'quoted"
        self.assertEqual(
            "This is quoted", Chevrons(original_string).apply()
        )

    def test_unquote_regular_string_with_double_quote_unpaired(self):
        """
        Testing on regular string with single
        substring with unpaired double quote

        """
        original_string = 'This is "quoted'
        self.assertEqual(
            "This is quoted", Chevrons(original_string).apply()
        )

    def test_unquote_and_chevronize_mixed_string(self):
        """
        Testing on regular string with a
        substring with double quotes around
        and another substring with unpaired double
        quote

        """
        original_string = 'This is "quoted" and "unpaired'
        self.assertEqual(
            'This is «quoted» and unpaired', Chevrons(original_string).apply()
        )

    def test_unquote_and_chevronize_another_mixed_string(self):
        """
        Testing on regular string with a
        substring with single quotes around
        and another single substring with unpaired single
        quote

        """
        original_string = "This is 'quoted' and 'unpaired"
        self.assertEqual(
            'This is «quoted» and unpaired', Chevrons(original_string).apply()
        )


if __name__ == '__main__':
    unittest.main()
