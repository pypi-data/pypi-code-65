import abc


class InterfaceFa(abc.ABC):
    @abc.abstractmethod
    def dictionary(self):
        pass

    @abc.abstractmethod
    def read(self, world: str):
        pass

    @abc.abstractmethod
    def automaton(self):
        pass

    @abc.abstractmethod
    def states(self):
        pass

    @abc.abstractmethod
    def alphabet(self):
        pass
