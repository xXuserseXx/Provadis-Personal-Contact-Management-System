import Contact

class ContactManager():
  def __init__(self):
    self.contacts = []
  
  def add_contact(self, c):
    self.contacts.append(c)
  
  
  #for simplicity purposes we will assume that each name is unique, and working as a primary key
  def remove_contact(self, name):
    for c in self.contacts:
      if c.get_name() == name:
        self.contacts.remove(c)
        return True
    return False
  
  def search_contacts(self, s_key):
    r_list = []
    keyword = s_key.strip().lower()
    
    for c in self.contacts:
      if keyword in c.to_searchable_string().lower():
        r_list.append(c)
    
    return r_list
  
  def list_contacts(self):
    return self.contacts
  
  def group_by_type(self):
    r_dict = {}
    
    for c in self.contacts:
      contact_type = c.contact_type
      
      if contact_type not in r_dict:
        r_dict[contact_type] = []
        
      r_dict[contact_type].append(c)
      
    return r_dict
     