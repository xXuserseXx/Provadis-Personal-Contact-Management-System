from abc import ABC, abstractmethod
from datetime import datetime

class Contact(ABC):
  
  def __init__(self, name, phone, email, created_at):
    self.name = name
    self.phone = phone
    self.email = email
    self.created_at = created_at
    
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
