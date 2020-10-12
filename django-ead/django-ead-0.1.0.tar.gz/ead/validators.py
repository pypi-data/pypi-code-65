from django.core.exceptions import ValidationError


def validate_date_time(value):
    """Raise ValidationError if `value` does not constitute an ISO 8601
    pattern.

    The valid patterns are:

    * YYYY-MM-DD
    * YYYY-MM
    * YYYY
    * YYYY-MM-DDThh:mm:ss
    * YYYY-MM-DDThh:mm:ss[+|-]hh:mm
    * YYYY-MM-DDThh:mm:ssZ

    """
    pass


def validate_id(value):

    """Raise ValidationError if `value` does not consitute an ID.

    An ID must begin with an alpha, not numeric, character, either
    upper or lowercase, and may contain a . (period), : (colon), -
    (hyphen), or _ (underscore), but not a blank space.

    """
    pass


def validate_nmtoken(value):
    """Raise ValidationError if `value` does not constitute a name token.

    A name token can consists of any alpha or numeric character, as
    well as a . (period), : (colon), - (hyphen), or _ (underscore),
    but not a blank space.

    """
    pass


def validate_token(value):
    """Raise ValidationError if `value` does not constitute a token.

    A token is a type of string that may not contain carriage return,
    line feed or tab characters, leading or trailing spaces, nor any
    internal sequence of two or more spaces.

    """
    pass
