import datetime

from django.core.exceptions import ValidationError


def validator_pub_year(value):
    if value < 1308 or value > datetime.datetime.now().year:
        raise ValidationError(
            '%(value)s is not a correcrt year!',
            params={'value': value},
        )
