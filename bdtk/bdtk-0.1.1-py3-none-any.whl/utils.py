#!/usr/bin/env python
# coding: utf-8

# In[13]:


class Utils:
    def type_check(obj, type_in, throw_error=TypeError, msg=True):
        """ Verifies that the type of OBJ is TYPE_IN. If not, handles based on THROW_ERROR.

        Parameters
        -------------------------------
        obj: anything, 
            An object whose type will be verified.
        type_in: class, list of classes
            If a class, checks that obj is of type type_in.
            If a list, checks that obj is of a type in type_in. 
        throw_error: True, subclass of Exception, default TypeError
            If True, returns whether type is appropriate. 
            If a subclass of Exception, throws that Exception if type is not appropriate.
        msg: str, default=True
            The message to print out if the type check should output an error. 
            Will only be used if the type is not appropriate and throw_error is an Error.
            Default is True, in which case the default message will print.
            Default message: f"object should be of type {type_in}, not type {type(obj)}"


        Returns
        -------------------------------
        If throw_error is True, boolean on whether type is appropriate.
        If throw_error is a subclass of Exception, returns None.

        See Also 
        -------------------------------
        >>> #assert type(obj) == type_in, "error_message_here"

        Examples
        -------------------------------
        >>> type_check("hello!", str, True)
        True
        >>> type_check(12.2, int, True, "age should be an int") # message is only used if throw_error isn't True!
        False
        >>> type_check("hello!", str)
        >>> type_check(12, int)
        """

        assert isinstance(type(type_in), type), "type_in needs to be a class"
        assert throw_error == True or issubclass(throw_error, Exception),             "throw_error needs to be True or a subclass of exception" 
        assert isinstance(msg, str) or msg == True, "msg must be a string or True"

        # put type_in into a list if not -> allows for iteration when type checking below
        if type(type_in) != list:
            type_in = [type_in]
        # create default msg if needed
        if msg == True:
            type_str = str(type_in[0]) 
            for _type in type_in[1:]:
                type_str += ", " + str(_type) 
            msg = f"object should be of {type_str}, not {type(obj)}"

        # main type checking segment 
        # will return True or None, depending on throw_error, if type is appropriate.
        type_appropriate = False
        for _type in type_in:
            if type(obj) == _type:
                type_appropriate = True
                if throw_error == True:
                    return True
                return None

        # if we've reached this point, the type is not appropriate
        if throw_error == True:
            return False
        else:
            raise throw_error(msg)


# In[14]:


# ## TESTING
# # Good calls
# print(type_check("hello!", str))
# print(type_check(12.2, int, True, "age should be an int"))
# print(type_check(12, int, True, "age should be an int"))

# # Erroring calls
# #>>> type_check("hello!", int, ValueError, "greeting should be a string.")
# #TypeError: greeting should be a string
# #>>> # Will use the default TypeError and msg if type not appropriate
# #>>> type_check("Blasphemy!", [int, float]) 
# #TypeError: object should be of <class 'int'>, <class 'float'>, not <class 'str'>
# Utils.type_check


# In[ ]:




