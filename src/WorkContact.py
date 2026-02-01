import Contact

class WorkContact(Contact):
  def __init__(self, name, phone, email, company, job_title):
    super().__init__(name, phone, email)
    self.company = company
    self.job_title = job_title
    
  def contact_type(self):
    return "personal"
  
  def __str__(self):
    return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}, Company: {self.company}, Title: {self.job_title}"
  
  def to_dict(self):
    info = super().to_dict()
    info["company"] = self.company
    info["job_title"] = self.job_title
    return info