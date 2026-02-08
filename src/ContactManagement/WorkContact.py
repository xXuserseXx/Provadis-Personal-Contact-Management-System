from ContactManagement.Contact import Contact, JsonFields
from ContactManagement.RegularExpressions import PhoneNumber, Mail, Name

class WorkContact(Contact):
  def __init__(self, name: Name, phone: PhoneNumber, email: Mail, company: str, job_title: str):
    super().__init__(name, phone, email)
    self.company = company
    self.job_title = job_title
    
  def get_contact_type(self):
    return type(self).__name__
  
  def __str__(self):
    return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}, Company: {self.company}, Title: {self.job_title}"
  
  def to_dict(self):
    info = super().to_dict()
    info["company"] = self.company
    info["job_title"] = self.job_title
    info[JsonFields.ARGS] = [self.name, str(self.phone), str(self.email), self.company, self.job_title]
    return info

  def get_contact_type(self)-> str:
    return type(self).__name__
  
  def to_searchable_string(self):
    return f"{self.name}, {self.phone}, {self.email}, {self.company}, {self.job_title}"