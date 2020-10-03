from shutil import which


class DependencyChecker(object):
    """
    Class for checking system dependencies.
    :param dependencies:
        `str` with single dependency or `list`/`tuple` with multiple dependencies
        list with '~' as leading entry are considered soft requirements
    """

    def __init__(self, dependencies):
        if type(dependencies) is str:
            self.dependencies = [dependencies]
        elif type(dependencies) not in (list, tuple):
            raise TypeError(
                "Type of 'dependencies' must be either `str`, `list` or `tuple`."
            )
        else:
            self.dependencies = dependencies

        self.results = []
        self.installed = []
        self.missing = []
        self.missing_soft = []
        self.missing_hard = []

        self._dependency_check(self.dependencies)

    def _dependency_check(self, dependencies):
        """
        Internal method for looping through given dependencies and checking them.
        :param dependencies:
            list/tuple with single or multiple dependencies
        :returns:
            list of tuples containing lists of given dependencies, installed dependencies,
            missing dependencies and a boolean if dependency (group) is a soft requirement
        """
        results = []

        for dep_obj in dependencies:
            if type(dep_obj) is str:
                dep_list = [dep_obj]
            elif type(dep_obj) in (list, tuple):
                dep_list = list(dep_obj)
            else:
                raise TypeError(
                    "Type of objects in 'dependencies' must be either `str`, `list` or `tuple`."
                )

            soft_dep = False
            installed = []
            missing = []

            if dep_list[0] == "~":
                soft_dep = True
                dep_list.pop(0)
            for dep in dep_list:
                if type(dep) is not str:
                    raise TypeError("Dependency must be type `str`.")
                if which(dep) is not None:
                    installed.append(dep)
                    self.installed.append(dep)
                else:
                    missing.append(dep)
                    self.missing.append(dep)
                    if soft_dep is True:
                        self.missing_soft.append(dep)
                    else:
                        self.missing_hard.append(dep)

            if dep_list:
                results.append((dep_list, installed, missing, soft_dep))

        self.results = results

    @property
    def all_dependencies_installed(self):
        """
        Property containing status of installed dependencies.
        :returns:
            boolean if all given dependencies are installed regardless if soft or hard
            when no check was run returns `None` instead
        """
        if not self.results:
            return None
        if len(self.missing) == 0:
            return True
        return False

    @property
    def requirements_fulfilled(self):
        """
        Property containing status of installed requirements.
        :returns:
            boolean if given requirements are installed (soft requirements ignored)
            when no check was run returns `None` instead
        """
        if not self.results:
            return None
        if len(self.missing) == 0 or len(self.missing) == len(self.missing_soft):
            return True
        return False

    def print_messages(self, soft_also=False):
        """
        Prints results of check
        :param soft_also:
            boolean if missing soft requirements should also be printed.
            defaults to False
        """
        if not self.results:
            print("Nothing to print. No dependencies were checked.")
        elif len(self.missing) == 0:
            print("All dependencies are installed on the system.")
        elif len(self.installed) == 0:
            print("All dependencies are missing on the system.")
        elif len(self.missing) == len(self.missing_soft):
            print("All requirements are fulfilled", end="")
            if soft_also is False:
                print(".")
            else:
                print(
                    f", but the following soft "
                    f"{'dependencies are' if len(self.missing_soft) > 1 else 'dependency is'}"
                    f" missing:\n  {self.missing_soft}"
                )
        else:
            print(f"Following hard dependencies are missing:\n  {self.missing_hard}")
            if soft_also is True:
                print(
                    f"Following soft dependencies are missing:\n  {self.missing_soft}"
                )
