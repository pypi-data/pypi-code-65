"""A SliceVar is bound to a slice of another StringVar.

Synopsis

# In currency trading a "pair" consists of a "base" currency
# represented by three letters followed by a "quote" currency
# represented by three letters. A desire to have related
# StringVars for the base and quote that changed with one
# for the pair was the initial use case for the SliceVar:

pair_var = StringVar()
base_var = SliceVar(pair_var, 0, 2)
quote_currency = SliceVar(pair_var, 3, 5)

pair_var.set("EurUsd")
assert pair_var.get() == "EurUsd"

base_var.set("Aud")
assert pair_var.get() == "AudUsd"

quote_currency.set("Jpy")
assert pair_var.get() == "AudJpy"


CAVEAT:
    * Setting a slice that starts past the end
      of the current value set in the StringVar
      will raise an IndexException.
"""


from tkinter import StringVar


class SliceVar(StringVar):
    """StringVar bound to a section of another StringVar."""

    def __init__(self, parent: StringVar, start_index: int, end_index: int):
        StringVar.__init__(self)
        self.__parent = parent
        self.__start = start_index
        self.__end = end_index
        self.__parent.trace("w", self.__change_parent_callback)
        self.trace("w", self.__change_callback)

    def __change_callback(self, *junk):
        """Change slice in parent to match value of self."""
        value = self.__parent.get()
        chars = list(value)
        chars[self.__start : self.__end] = self.get()
        new_value = "".join(chars)
        if new_value != value:
            # Potential recursive loop between callbacks
            # should be stopped when values agree.
            self.__parent.set(new_value)

    def __change_parent_callback(self, *junk):
        """Change value of self to match slice of parent."""
        value = self.get()
        new_value = self.__parent.get()[self.__start : self.__end]
        if new_value != value:
            # Potential recursive loop between callbacks
            # should be stopped when values agree.
            self.set(new_value)
