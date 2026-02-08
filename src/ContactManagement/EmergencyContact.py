from ContactManagement.Contact import Contact, JsonFields
from ContactManagement.RegularExpressions import PhoneNumber, Mail, Name

class EmergencyContact(Contact):
  def __init__(self, name: Name, phone: PhoneNumber, email: Mail, priority_level: int):
    super().__init__(name, phone, email)
    self.priority_level = priority_level
    
  def get_contact_type(self):
    return type(self).__name__
    
  def __str__(self):
    return f"Emergency Contact, Name: {self.name}, Phone: {self.phone}, Email: {self.email}, priority level: {self.priority_level}"
  
  def to_dict(self):
    info = super().to_dict()
    info["priority_level"] = self.priority_level
    info[JsonFields.ARGS] = [self.name, str(self.phone), str(self.email), self.priority_level]
    return info
  
  def to_searchable_string(self):
    return f"{self.name}, {self.phone}, {self.email}, {self.priority_level}"