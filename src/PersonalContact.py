import Contact

class PersonalContact(Contact):
  def __init__(self, name, phone, email, birthday):
    super().__init__(name, phone, email)
    self.birthday = birthday
    
  def contact_type(self):
    return "personal"
  
  def __str__(self):
    return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}, Birthday: {self.birthday}"
  
  def to_dict(self):
    info = super().to_dict()
    info["birthday"] = self.birthday
    return info