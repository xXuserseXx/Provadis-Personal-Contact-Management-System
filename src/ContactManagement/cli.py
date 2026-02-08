import argparse
from collections.abc import Callable, Iterable
from ContactManagement import ContactManager
from ContactManagement import EmergencyContact, PersonalContact, WorkContact
from enum import StrEnum
from functools import partial
import sys
import inspect

# We just want a single contact manager instance for the UI
# And we can instantiate it right away in the global scope.
contact_manager_singleton = ContactManager()

class   Action(StrEnum):
    MAIN_MENU = "main menu"
    EXIT = "exit"
    ADD = "add contact"
    RM = "remove contact"
    ADD_EMERGENCY = "emergency contact"
    ADD_PERSONAL = "personal contact"
    ADD_WORK = "work contact"
    GATHER_PARAMETERS = "gather parameters"

def gather_parameters(func: Callable[..., any]) -> Callable[..., any]: # Gathers parameters via input() to create a partial() no longer requires arguments
        print(f"You are now prompted to input the fields required to construct {type(func)}.")
        parameter = inspect.signature(func)
        for p in parameter.parameters.values():
            response_correct = False # We repeat the questions until there is a correct response
            while not response_correct:
                print(f"Input parameter '{p.name}' of type {p.annotation}")
                response = input(">>>")
                if response == str(Action.EXIT): # Admitively, this is not a pretty solution, but the alternative requires me to extend my framework into parent class and multiple child classes. This complexity is not feasible.
                    my_exit() # It'd be better if we used the exit UIComponent to be consistent...
                # Try to instantiate the datatype using the anotated datatype:
                # This does all the checking for us...
                try:
                    arg = p.annotation(response)
                    response_correct = True
                    func = partial(func, arg) # Reduce the function parameters
                    break
                except Exception as e:
                    print(str(e))
                    continue
        return func
                    

    

class   UIComponent:
    available_actions: dict[Action, any] = {} # A class attribute, shared among instances
    def __init__(self, provides: Action, options: list[Action]):
        options.extend([Action.MAIN_MENU, Action.EXIT])
        self.options = options
        UIComponent.available_actions[provides] = self # Such that other instances can call the newly registered component.
        self._effects = None # By default no side effects

    def set_side_effects(self, effects: list[Callable[..., any]]):
        self._effects = effects

    def __call__(self):
        # If the Component has effects, execute them and return to the previous component in the call stack
        if self._effects:
            for effect in self._effects:
                effect()
            return
    
        for i, option in enumerate(self.options):
            print(f"[{i}] {option}")
        try: # Try to get the choice index
            choice_index = None # Initalizing it in the outer scope
            choice = input(">>")
            string_options = list(map(str, self.options)) # Need actual strings to compare options to user input
            if choice in string_options:
                choice_index = string_options.index(choice)
            else:
                choice_index =  int(choice) # It is also okay if the user inputs the literal number
        except ValueError: # User did not input an int
            print(f"Expected the string of the option or an integer!")
            return self() # Try the same UI component again.
        try: # look if the index is within range
            chosen_action = self.options[choice_index]
            next_component = UIComponent.available_actions[chosen_action]
            if next_component is None:
                print("Action not implemented yet")
                return self() # Repeat the current action
            next_component()
            # If the next_component just executes a side effect and returns,
            # then we want to be at the same UI component that we came from.
            self() 
            
        except IndexError:
            print("Your choice is not in the option range!")
            # If there is an exception, we want to repeat the UI component:
            self()
        except KeyError:
            print("This action has not be implemented yet!")
            self()

def my_exit():
    # Join all the threads before exiting the program
    for thread in contact_manager_singleton.threads:
        thread.join()
    exit(0) # Exit code zero as it was a graceful exit


# We are going to implement both CLI (for testing)
# As well as wizzard (input()) driven UX
def main():
    main_menu = UIComponent(provides=Action.MAIN_MENU, options=[Action.ADD])
    exit = UIComponent(provides=Action.EXIT, options=[])
    exit.set_side_effects([
        my_exit
    ])
    add_contact = UIComponent(provides=Action.ADD, options=[Action.ADD_EMERGENCY, Action.ADD_PERSONAL, Action.ADD_WORK])
    add_emergency = UIComponent(provides=Action.ADD_EMERGENCY, options=[])
    add_emergency.set_side_effects([
        # We use callbacks just like in JavaScript frameworks
        lambda: contact_manager_singleton.add_contact(gather_parameters(EmergencyContact))
    ])
    add_personal = UIComponent(provides=Action.ADD_PERSONAL, options=[]) 
    add_personal.set_side_effects([
        lambda: contact_manager_singleton.add_contact(gather_parameters(PersonalContact))
    ])
    add_work = UIComponent(provides=Action.ADD_WORK, options=[])
    add_work.set_side_effects([
        lambda: contact_manager_singleton.add_contact(gather_parameters(WorkContact))
    ])
    main_menu()

if __name__ == "__main__":
    main()