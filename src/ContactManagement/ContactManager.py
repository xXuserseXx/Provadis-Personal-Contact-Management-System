from ContactManagement.Contact import Contact, JsonFields
from ContactManagement.PersonalContact import PersonalContact
from ContactManagement.EmergencyContact import EmergencyContact
from ContactManagement.WorkContact import WorkContact
from ContactManagement.RegularExpressions import PhoneNumber
from pathlib import Path
from platformdirs import user_data_dir
import json
import logging
log = logging.getLogger(__name__)

PACKAGE_NAME = "contact-management" # This is also the name that pip uses to reference our package
# We define it here such that we can later use it to construct the directory in which we save our json.

# This is the directory where we save our json file to:
json_dir: Path = Path(user_data_dir(PACKAGE_NAME))
# We consciously did not nest it into source or the root of the project:
# If we nested it into source, then it would be installed to side packages after running pip install .
# Site-packages is read only for many processes. IT IS NOT THE RIGHT LOCATION TO STORE DATA TO.
# If we put it in the top level of our project, the json would not be installed when running pip install .:
# This would imply that the package is unusable after intstallation.
# As we want to avoid both of these cases, we put it into the user_data_dir, which is OS dependent.
# E.g. for most linux distros it is: ~/.local/share/contact-management.
# We will provide logging to where the json has been created at the OS of the user.


# We can execute the mkdir in the top level scope, as it is a preliminary for using this module:
json_dir.mkdir(parents=True, exist_ok=True)
json_file = json_dir / "contacts.json"


class ContactManager():
  def __init__(self):
    log.info("CONSTRUCTED_CONTACT MANAGER")
    self.contacts = []
  
  def add_contact(self, c):
    self.contacts.append(c)

  def   save_contacts(self):
    # Transform self.contacts into a data structure that json.dumps accepts (dict/list):
    formatted_contacts = list(map(lambda contact: contact.to_dict(), self.contacts))
    json_file.write_text( # This method uses write mode (completely overrides existing entries)
        json.dumps(formatted_contacts, indent=2), # Using indent to make json prettier
        encoding="utf-8"
        )

  def   load_contacts(self):
    # This function updates self.contacts
    # Load the contacts into (list/dict) objects via json.loads:
    payload = json.loads(json_file.read_text(encoding="utf-8"))
    # And then map them onto Contact objects:
    self.contacts = map(
        lambda contact: globals().get(contact[JsonFields.CONTACT_TYPE])( # The globals.get() will resolve to the class used to construct the contacts
            *contact[JsonFields.ARGS] # Every contact saves the fields needed to construct itself.
        ),
        payload # Apply to all contacts in the json...
    )
  
  
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

  def __str__(self):
    return "\n".join(str(contact) for contact in self.contacts)