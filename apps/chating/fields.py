from rest_framework.fields import Field

class DateTimeDictField(Field):

    def to_representation(self, value):
        time_dict = {
            'year': value.strftime('%Y'),
            'month': value.strftime('%m'),
            'day': value.strftime('%d'),
            'hour': value.strftime('%H'),
            'minute': value.strftime('%M'),
            'second': value.strftime('%S'),
            'miliseconds': value.strftime('%f'),
            'utc': value.strftime('%z')
        }
        return time_dict

    def to_internal_value(self, data):
        return data