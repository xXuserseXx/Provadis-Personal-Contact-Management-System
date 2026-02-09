from ContactManagement import PersonalContact, EmergencyContact, WorkContact
from ContactManagement import Mail, PhoneNumber, Name
from ContactManagement import ContactManager
from typing import Callable
from time import sleep
from datetime import date, datetime

ADD_CONTACT = "Add contact"
LIST_CONTACTS_DATE = "List contacts (by date)"
LIST_CONTACTS_GROUP = "List contacts (by group)"
EXIT = "Exit"
REMOVE_CONTACTS = "Remove contact"
SEARCH_CONTACT = "Search contact"
SAVE_CONTACTS = "Save contacts"

def user_make_state_choice(state: dict): # The call can decide what to do with the returned dict index
    user_made_valid_choice = False
    if isinstance(state, dict):
        descriptions = list(state.keys())
    else:
        descriptions = state
    while not user_made_valid_choice:
        try:
            response = int(input(">> "))
            return descriptions[response]
        except (TypeError, IndexError, ValueError):
            print(f"The number you gave was not within range")


def ask_for(contact_attribute: str, save_to: dict, checker: Callable[..., any], instructions: str = ""):
    user_gave_valid_response = False # variable is just used to make it more descriptive
    while not user_gave_valid_response:
        try:
            print(f"What is the {contact_attribute.replace('_', ' ').replace('phone', 'phone number')} of the contact?")
            if instructions:
                print(instructions)
            save_to[contact_attribute] = checker(input(">> "))
            break
        except Exception as e:
            print(e)

def check_date(date_string: str) -> date:
    return datetime.strptime(date_string, "%d.%m.%Y").date() #Using the format specifier to ensure DD.MM.YYYY

def ask_for_constructor_data(constructor):
    gathered_data = { # Will be populated in this function. Used for constructor calls via **kwargs.
        "name": None,
        "phone": None,
        "email": None,
        "company": None,
        "job_title": None,
        "birthday": None,
        "priority_level": None
    }
    ask_for(contact_attribute="name", save_to=gathered_data, checker=Name)
    ask_for(contact_attribute="phone", save_to=gathered_data, checker=PhoneNumber)
    ask_for(contact_attribute="email", save_to=gathered_data, checker=Mail)
    if constructor == WorkContact:
        ask_for(contact_attribute="company", save_to=gathered_data, checker=lambda x: x)
        ask_for(contact_attribute="job_title", save_to=gathered_data, checker=lambda x: x)
    elif constructor == PersonalContact:
        ask_for(contact_attribute="birthday", save_to=gathered_data, checker=check_date, instructions="Provide the date in the following format: DD.MM.YYYY .")
    elif constructor == EmergencyContact:
        ask_for(contact_attribute="priority_level", save_to=gathered_data, checker=int)
    # Given the subclass type, some attributes are not needed (still None), we filter them out.
    non_none_values = {k: v for k, v in gathered_data.items() if v is not None}
    return constructor(**non_none_values)

def print_choice(iterable):
    for i, e in enumerate(iterable):
        print(f"[{i}] {e}")

def main():

    contact_manager = ContactManager() # This is a singleton; per program run, we only create one instance
    contact_manager.load_contacts() # We load the contacts from the last session.
    state = {
        ADD_CONTACT: False,
        LIST_CONTACTS_GROUP: False,
        LIST_CONTACTS_DATE: False,
        SEARCH_CONTACT: False,
        REMOVE_CONTACTS: False,
        SAVE_CONTACTS: False,
        EXIT: False,
    }
    while not state[EXIT]:
        if all(v is False for v in state.values()): # User has not made any choice yet
            print("Welcome to the contact management system, what action would you like to take?")
            print_choice(state.keys())
            state[user_make_state_choice(state)] = True
        
        # Execute the choice that the user made
        if state[ADD_CONTACT]:
            contact_types = {
                "personal contact": PersonalContact,
                "emergency contact": EmergencyContact,
                "work contact": WorkContact
            }
            print("What kind of contact would you like to add?")
            print_choice(contact_types.keys())
            contact_constructor = contact_types[user_make_state_choice(contact_types)]
            contact = ask_for_constructor_data(contact_constructor)
            contact_manager.add_contact(contact)
            state[ADD_CONTACT] = False # Job done, reset the state so that we get back to main menu
        
        if state[LIST_CONTACTS_GROUP]:
            groups = contact_manager.group_by_type()
            for t in groups.keys():
                print(f"Your {t.lower().replace('contact', '')} contacts:")
                if not groups[t]:
                    print(f"    Currently, no contacts of this type.")
                else:
                    for contact in list(map(lambda c: c.__str__(), groups[t])):
                        print(contact)
                print('\n')
            state[LIST_CONTACTS_GROUP] = False
        
        if state[REMOVE_CONTACTS]:
            print("Choose the index of the content you would like to remove.")
            print_choice(contact_manager.contacts)
            choice = user_make_state_choice(contact_manager.contacts)
            choice_index = contact_manager.contacts.index(choice)
            del contact_manager.contacts[choice_index] # Delete the contact
            print(contact_manager)
            state[REMOVE_CONTACTS] = False
        
        if state[EXIT]:
            print("Saving your current contacts...")
            contact_manager.save_contacts()
            print("Bye!")
            for thread in ContactManager.threads:
                thread.join()
            exit(0) # Graceful exit.
        
        if state[SEARCH_CONTACT]:
            print("Enter an attribute value of the contact you are searching.")
            response = input(">> ")
            matches = contact_manager.search_contacts(response)
            if not matches:
                print("No matches found.")
            else:
                print(matches)
            state[SEARCH_CONTACT] = False
        
        if state[SAVE_CONTACTS]:
            print("Saving your current contacts in the background...")
            contact_manager.save_contacts()
            state[SAVE_CONTACTS] = False
        
        if state[LIST_CONTACTS_DATE]:
            for contact in contact_manager.contacts:
                print(f"Created at {contact.created_at.strftime('%d.%m.%Y %H:%M:%S')}:")
                print(f"    {str(contact)}")
            state[LIST_CONTACTS_DATE] = False

        # For the display:
        print("-" * 40)

            
            
        


if __name__ == "__main__":
    main()