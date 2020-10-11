""" Inspector module """
import inspect
import os
from typing import List


class Container:
    """ Describes a package or module """

    def __init__(self, name_parts: List[str] = None):
        if name_parts is None:
            self._name_parts = []
        else:
            self._name_parts = name_parts

    @property
    def cwd_path(self) -> str:
        """ Returns the full path including CWD """
        output = os.path.join(os.getcwd(), self.path)
        return output

    @property
    def name(self) -> str:
        """ Returns the module name in a.b.c format """
        output = ""
        for name_part in self._name_parts:
            if output != "":
                output += "."
            output += name_part
        return output

    @property
    def path(self) -> str:
        """ Returns the module subpath in a/b/c format """
        output = ""
        for name_part in self._name_parts:
            output = os.path.join(output, name_part)
        return output


class Inspector:
    """ Module inspector class """

    @staticmethod
    def get_modules_in_cwd_container(container: Container,
                                     exclude_prefixes: List[str] = None
                                    ) -> List[str]:
        """ Returns all modules in the given working directory package
        Check get_all_modules_in_path for parameter explanations
        """
        return Inspector.get_modules_in_path(container.cwd_path, exclude_prefixes)

    @staticmethod
    def get_modules_in_path(path: str,
                            exclude_prefixes: List[str] = None
                           ) -> List[str]:
        """ Returns all modules in a directory
        path: Describes the path to be scanned
        exclude_prefixes: Files starting with those prefixes will be excluded
        """
        output = []
        files_in_path = [f for f in os.listdir(path)] # pylint: disable=R1721

        for file_name in files_in_path:
            if not Inspector._is_module_name_valid(file_name, exclude_prefixes):
                continue
            module_name = os.path.splitext(file_name)[0]
            output.append(module_name)
        return output

    @staticmethod
    def get_modules_in_cwd_path(path: str,
                                exclude_prefixes: List[str] = None
                               ) -> List[str]:
        """ Returns all modules in a directory
        path: Describes the path to be scanned
        exclude_prefixes: Files starting with those prefixes will be excluded
        """
        cwd_path = os.path.join(os.getcwd(), path)
        return Inspector.get_modules_in_path(cwd_path, exclude_prefixes)

    @staticmethod
    def get_classes_in_cwd_container(container: Container,
                                     exclude_prefixes: List[str] = None,
                                     exclude_classes: List[str] = None
                                    ) -> []:
        """ Returns object instances of modules in the given package """
        return Inspector._get_classes_in_container_path(
            container.cwd_path,
            container.name,
            exclude_prefixes,
            exclude_classes)

    @staticmethod
    def get_classes_in_container(container: Container,
                                 exclude_prefixes: List[str] = None,
                                 exclude_classes: List[str] = None
                                ) -> []:
        """ Returns object instances of modules in a directory """
        return Inspector._get_classes_in_container_path(
            container.path,
            container.name,
            exclude_prefixes,
            exclude_classes)

    @staticmethod
    def get_classes_in_module(module: str,
                              exclude_classes: List[str] = None
                             ) -> List[tuple]:
        """ Returns name / obj pairs in given module """
        output = []
        module = __import__(module, fromlist=[""])
        for class_name, class_ in inspect.getmembers(module, inspect.isclass):
            if exclude_classes is not None and class_name in exclude_classes:
                continue
            output.append(class_)
        return output

    @staticmethod
    def _get_classes_in_container_path(path: str,
                                       package_prefix: str = "",
                                       exclude_prefixes: List[str] = None,
                                       exclude_classes: List[str] = None
                                      ) -> []:
        """ Returns object instances of modules in a directory """
        output = []
        modules = Inspector.get_modules_in_path(path, exclude_prefixes)

        for module_name in modules:
            if package_prefix == "":
                module_path = module_name
            else:
                module_path = package_prefix + "." + module_name

            module_classes = Inspector.get_classes_in_module(
                module_path,
                exclude_classes=exclude_classes)

            for module_class in module_classes:
                if len(module_class.__module__) < len(package_prefix):
                    continue
                if module_class.__module__[:len(package_prefix)] != package_prefix:
                    continue
                output.append(module_class)

        return output

    @staticmethod
    def _is_module_name_valid(file_name: str,
                              exclude_prefixes: List[str]
                             ) -> bool:
        if file_name[:2] == "__":
            return False

        if exclude_prefixes is not None:
            for prefix in exclude_prefixes:
                if len(file_name) < len(prefix):
                    continue
                if file_name[:len(prefix)] == prefix:
                    return False

        return True
