from __future__ import annotations
import Contact
from datetime import date

class PersonalContact(Contact):
  def __init__(self, name: str, phone: str, email: str, birthday: date):
    # Before we even construct the parent some input validation:
    for param, value, expected in ( # This is basically just type checking
        ("name", name, str),
        ("phone", phone, str), # Unfortunately, you can not access variable names during runtime
        ("email", email, str), # Therefor we need this triplet for all of them
        ("birthday", birthday, date),
    ):
        if not isinstance(value, expected): # used this instead of type() ==, as it is inhertance proof
            raise TypeError(
                f"{type(self).__qualname__}.__init__: '{param}' must be "
                f"{expected.__name__}, got {type(value).__name__} ({value!r})"
            )

    super().__init__(name, phone, email)
    self.birthday: date = birthday
    
  def contact_type(self):
    return "personal"
  
  def __str__(self):
    return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}, Birthday: {self.birthday}"
  
  def to_dict(self):
    info = super().to_dict()
    info["birthday"] = self.birthday
    return info