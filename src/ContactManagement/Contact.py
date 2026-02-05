from abc import ABC, abstractmethod
from datetime import datetime
from ContactManagement.RegularExpressions import PhoneNumber, Mail


class Contact(ABC):
  
  def __init__(self, name, phone, email):
    self.name = name
    # As all subclasses call super
    # And super checks the regex of phone numbers and mails
    # via the constructorsl, the following is sufficient for
    # all our contacts:
    # The exceptions can then be catched by our decorators.

    self.phone = PhoneNumber(phone)
    self.email = Mail(email)

    # We create a timestamp for the creation time of the Contact.
    # Python sets the timezone automatically, if you don't define an argument.
    # Using Europe/Berlin time is kind of dumb for a Contact Management system:
    # As we got summer and winter time... And the our offset will lead to weird bugs.
    # However, as it is only a toy project, we will leave it with the defaults.
    self.created_at = datetime.now()
    
  def __str__(self):
    return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}"
  
  @abstractmethod
  def get_contact_type(self):
    pass
  
  @abstractmethod
  def to_dict(self):
    return {
        "contact_type": self.get_contact_type(),
        "name": self.name,
        "phone": self.phone,
        "email": self.email,
        "created_at": self.created_at.isoformat()
    }
