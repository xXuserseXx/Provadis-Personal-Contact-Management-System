from ContactManagement.Contact import Contact

class EmergencyContact(Contact):
  def __init__(self, name, phone, email, priority_level):
    super().__init__(name, phone, email)
    self.priority_level = priority_level
    
  def get_contact_type(self):
    return "emergency"
    
  def __str__(self):
    return f"level {self.priority_level} Emergency Contact, Name: {self.name}, Phone: {self.phone}, Email: {self.email}"
  
  def to_dict(self):
    info = super().to_dict()
    info["priority_level"] = self.priority_level
    return info