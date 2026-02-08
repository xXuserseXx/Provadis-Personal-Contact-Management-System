from ContactManagement.Contact import Contact, JsonFields
from ContactManagement.RegularExpressions import PhoneNumber, Mail, Name
from datetime import date

class PersonalContact(Contact):
  def __init__(self, name: Name, phone: PhoneNumber, email: Mail, birthday: date | str):
    super().__init__(name, phone, email)
    if isinstance(birthday, str): # In case it is a string, we want to convert it to a date
        try:
            birthday = date.fromisoformat(birthday)
        except ValueError:
            raise ValueError(f"Birthday is supposed to be a string in isoformat, but got {birthday}")
    self.birthday: date = birthday
    
  def get_contact_type(self):
    return type(self).__name__
  
  def __str__(self):
    return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}, Birthday: {self.birthday}"
  
  def to_dict(self):
    info = super().to_dict()
    info["birthday"] =  self.birthday.isoformat()
    info[JsonFields.ARGS] = [self.name, str(self.phone), str(self.email), self.birthday.isoformat()]
    return info

  def get_contact_type(self):
        return type(self).__name__
