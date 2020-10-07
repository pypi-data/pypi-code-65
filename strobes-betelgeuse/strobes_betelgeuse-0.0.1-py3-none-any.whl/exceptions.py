class BuildFailureException(Exception):
    def __str__(self):
        return 'Vulnerabilities have been found in this build'
