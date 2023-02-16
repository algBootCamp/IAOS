##
#@if english
#Temporal type - Month
#@endif
class month(object):
    def __init__(self, year=None, month = None):
        self.__year = year
        self.__month = month
    def __str__(self):
        if self.__month > 9:
            return str(self.__year) + '-' + str(self.__month) + 'M'
        return str(self.__year) + '-0' + str(self.__month) + 'M'
