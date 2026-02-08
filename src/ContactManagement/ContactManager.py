from ContactManagement.Contact import Contact, JsonFields
from ContactManagement.PersonalContact import PersonalContact
from ContactManagement.EmergencyContact import EmergencyContact
from ContactManagement.WorkContact import WorkContact
from ContactManagement.RegularExpressions import PhoneNumber
from pathlib import Path
from platformdirs import user_data_dir
from CustomLogging import *
import json
import threading
log = make_logger()

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
# Creating a global lock for file write operations:
file_write_lock = threading.Lock()
# Create a global lock to ensure that contacts remain in the exact state
# they are in when calling ContactManager.save_contacts().
# This is crucial, as the alternative: "Makeing a deep copy of contacts" takes time
# within which contacts could already be altered by the main thread.
contacts_state_lock = threading.Lock()

# This is a decorator for handling FileNotFoundError uniformly.
# All methods that do file IO should be decorated with it.
def create_file_on_not_found(method):
    def wrapper(*args, **kwargs):
        # try to do execute the method doing the file IO
        try:
            return method(*args, **kwargs)
        except FileNotFoundError as e:
            log(f"The File was not found, creating file {e.filename}", "WARNING")
            # Just create the file...
            Path(e.filename).touch(exist_ok=True)
            log(f"{e.filename} was created succesfully, proceding", "INFO")
    return wrapper

# All methods that do file IO should be decorated with it.
def log_on_permission_denied(method):
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except PermissionError as e:
            log("You don't have the permission to open this file", "CRITICAL")
            # Unfortunately, there is no way our program can fix a PermissionError.
            # The only thing we can do is log it, and keep our program from crashing.
    return wrapper


class ContactManager():
  def __init__(self):
    self.contacts = []
    # We have a list of threads as an attribute.
    # That is important as one method creates threads (save_contacts)
    # But an entirely different method needs to join them (load_contacts).
    # If we joined the threads instead in the function that created them (save_contacts),
    # our multithreading architecture would be inefficent.
    self.threads = []
  
  @log_calls(log)
  def add_contact(self, c):
    with contacts_state_lock: # append alters state, there for needs to aquire lock 
        self.contacts.append(c)
        
  @log_on_permission_denied
  @create_file_on_not_found
  def   save_contacts(self):
    def worker(): # Has all it needs from the closure. Needed because thread requires callable.
        with contacts_state_lock:
            # Transform self.contacts into a data structure that json.dumps accepts (dict/list):
            formatted_contacts = list(map(lambda contact: contact.to_dict(), self.contacts))
        # As we no longer need our self.contacts, we release the lock right after creating our list.
        with file_write_lock: # Writing file access needs to lock
            json_file.write_text( # This method uses write mode (completely overrides existing entries)
                json.dumps(formatted_contacts, indent=2), # Using indent to make json prettier
                encoding="utf-8"
                )
    self.threads.append(threading.Thread(target=worker))
    # Start the last thread in the list (the one just appended)
    self.threads[-1].start()


  @log_on_permission_denied
  @create_file_on_not_found
  def   load_contacts(self):
    """This function updates self.contacts"""
    # Before loading any contacts, first join all threads that might currently save newer versions:
    for thread in self.threads:
        thread.join()
    self.threads.clear() # Now that all threads are joined, clear the list
    # First of all, try reading the text from the file (the decorators handle exceptions):
    text: str = json_file.read_text(encoding="utf=8")
    # Then try to parse the json:
    try:
        # Load the contacts into (list/dict) objects via json.loads:
        payload = json.loads(text)
    except json.JSONDecoreError:
        log("JSON File was corrupted", "WARNING")
        # We opt for just deleting the contents of the corrupted file
        # There is no automated general way of fixing corrupted json.
        # And if we don't clear its contents, the program won't work!
        with file_write_lock:
            json_file.write_text("", "utf-8")
        return
    # Map items of payload onto Contact objects:
    # Try to instantiate the Contact objects.
    # If the class name does not exist in globals(),
    # globals().get(<name>) will return NoneType
    # Hence the resulting exception we need to handle is: TypeError: 'NoneType' object is not callable
    try:
        with contacts_state_lock: # Reassignment of self.contacts needs to be locked. As the worker is actually using self to access self.contacts via the closure.
            self.contacts = list(map(
                lambda contact: globals().get(contact[JsonFields.CONTACT_TYPE])( # The globals.get() will resolve to the class used to construct the contacts
                    *contact[JsonFields.ARGS] # Every contact saves the fields needed to construct itself.
                ),
                payload # Apply to all contacts in the json...
            ))
    except TypeError: # NoneType not callable (Unknown Contact Type)
        # To get back to a working state of the json,
        # we filter out all json objects containing an unknown contact type.
        self.save_contacts(filter(
            lambda contact: globals().get(contact[JsonFields.CONTACT_TYPE]) is not None,
            self.contacts
        ))
    
  
  #for simplicity purposes we will assume that each name is unique, and working as a primary key
  @log_calls(log)
  def remove_contact(self, name):
    with contacts_state_lock: # Removal alters state of contacts
        for c in self.contacts:
            if c.get_name() == name:
                self.contacts.remove(c)
                return True
    return False
  
  #TODO: Search Contacts
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
      contact_type = c.get_contact_type()
      
      if contact_type not in r_dict:
        r_dict[contact_type] = []
        
      r_dict[contact_type].append(c)
      
    return r_dict

  def __str__(self):
    return "\n".join(str(contact) for contact in self.contacts)