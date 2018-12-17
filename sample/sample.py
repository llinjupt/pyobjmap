# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 17:16:47 2017
@author: Red
"""

sample = 1
sample_str = "sample module"  
sample_list = [1, 2, 3]
sample_dict = {"a" : "b"}
sample_tuple = (1,)

# This is a function of sample
def sample_func(arg0, args1="name", *args, **kwargs):
    """This is a sample module function."""
    f_var = arg0 + 1
    return f_var

class A():
    """Definition for A class."""
    A_var = 10
    def __init__(self, name):
        self.__name = name
    
    @property
    def get_name(self):
        "Returns the name of the instance."
        return self.__name

obj_a = A('A Class instance')
def test():
    pass
obj_a.dynamicfunc = test

# start with #
# star 2
class B(A): # class B
    """B class, inherit A class. """

    # This method is not part of A class.
    def cls_func(self):
        """Anything can be done here."""

    def get_name(self):
        "Overrides method from X"
        return 'B(' + self.__name + ')'

obj_b = B('B Class instance')
