import re

mail_pattern = re.compile(r"^[a-zA-Z]+[\._][a-zA-Z]+[0-9]*\@[^\s@]+\.[a-zA-Z]+$")
# What the mail pattern means:
# An Email address starts with one or more alphabetical characters.
# Afterwards, there has to be either a dot or an underscore.
# Again followed by alphabetical charcters.
# Afterwards, optionally a number.
# Then the @ sign.
# Afterwards, a string of arbitrary characters except white spaces or @
# A literal dot.
# A strig of alphabetical charcters.
# End of string.

# Example:
# luis.gaertner@stud-provadis.de

phone_number_pattern = re.compile(r"^(?:(?:\+|00)\d{1,3})?[0-9]*$")
# What the phone number pattern means:
# You can either give a country code or omit it.
# If the country code is given:
# +<country_code> or
# 00<country_code>.
# The country code can be 1 - 3 digits long.
# Afterwards an arbitrary amount of digits.
# We used non-capturing groups for the country code.
# As they are just units for the ? quantifier or the | ("or") to work.

# Examples:
# +49 18257
# 001 897543

# An E-Mail address IS A string
# A phone number IS A string
# Sounds like a good use case for inhertance:

class   Mail(str):
    def __init__(self, mail: str):
        if not isinstance(mail, str):
            raise TypeError(f"Constructor of class Mail expects a string not a {type(mail)}")
        if not re.fullmatch(mail_pattern, mail):
            raise ValueError(f"E mail does not obey the regex pattern")
        super().__init__(mail) # Invokation of string copy constructor


class   PhoneNumber(str):
    def __init__(self, phone_number: str):
        if not isinstance(phone_number, str):
            raise TypeError(f"Constructor of class PhoneNumber expects a string not a {type(phone_number)}")
        if not re.fullmatch(phone_number_pattern, phone_number):
            raise ValueError(f"Phone number does not obey the regex pattern")
        super().__init__(phone_number) # Invokation of string copy constructor
