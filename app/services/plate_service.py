import re

REGEX_BR_PLATE = re.compile('[A-Z]{3}[0-9][0-9A-Z][0-9]{2}')

def is_valid_plate_format(plate):
    is_valid = False
    plate = plate.replace(" ", "")

    if REGEX_BR_PLATE.match(plate):
        is_valid = True

    return is_valid

