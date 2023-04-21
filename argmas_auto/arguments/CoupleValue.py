""" 
Implement the CoupleValue class.
"""


class CoupleValue:
    """
    CoupleValue class.
    This class implements a couple value used in argument object.
    attr:
    criterion_name:
    value:
    """

    def __init__(self, criterion_name, value):
        self.__criterion_name = criterion_name
        self.__value = value

    def __str__(self):
        """
        CoupleValue as a string.
        """
        return self.__criterion_name.name + "=" + self.__value.name

    def get_criterion_name(self):
        """
        Return the criterion name.
        """
        return self.__criterion_name

    def get_criterion_value(self):
        """
        Return the criterion's value.
        """
        return self.__value
