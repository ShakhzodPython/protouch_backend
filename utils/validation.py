import random

from rest_framework.exceptions import ValidationError


def validate_phone_number(phone_number):
    if len(phone_number) != 12:
        raise ValidationError("Phone number must contain exactly 12 digest")
    if not phone_number.isdigit():
        raise ValidationError("Phone number must consist of only numbers")
    return phone_number


def generate_order_number(length=6):
    return "".join(random.choices("0123456789", k=length))
