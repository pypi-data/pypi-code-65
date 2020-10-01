DEFAULT_SETTINGS = {
    'CHROME_PATH': None,
    'CHROMEDRIVER_PATH': None,
    'CHROMEDRIVER_DOWNLOADS': True,
    # also, PDF_KWARGS, but it's handled differently
}


def get_chromepdf_settings_dict():
    """
    Return a Django's settings.CHROMEPDF dict. Return empty dict if not found or Django not installed.
    For our sanity, this should be the ONLY place within the chromepdf app that we import from Django.
    This way, the library should work even if Django is not installed (except with its settings ignored).
    """
    try:
        from django.conf import settings
        return getattr(settings, 'CHROMEPDF', {})
    except (ImportError, ModuleNotFoundError):
        return {}


def parse_settings(**overrides):
    """
    Return a dict of lowercased DEFAULT_SETTINGS based on combination of defaults, Django settings, and overrides.
    Priority: keyword overrides > Django settings > DEFAULT_SETTINGS
    """

    output = {}
    chromepdf_settings = get_chromepdf_settings_dict()

    # iterate over expected setting names
    for k, defaultval in DEFAULT_SETTINGS.items():
        k_lower = k.lower()
        if k_lower in overrides:
            output[k_lower] = overrides[k_lower]  # get kwarg
        else:
            output[k_lower] = chromepdf_settings.get(k, defaultval)  # get Django setting, OR default value

        # convert falsey values to more appropriate ones.
        if k == 'CHROMEDRIVER_DOWNLOADS':  # boolean settings
            if output[k_lower] is None:
                output[k_lower] = False
        else:  # path settings
            if output[k_lower] == '':
                output[k_lower] = None

    return output
