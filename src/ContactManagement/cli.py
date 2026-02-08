import argparse
from collections.abc import Callable, Iterable
from ContactManagement import ContactManager
from ContactManagement import EmergencyContact, PersonalContact, WorkContact
from enum import StrEnum
from functools import partial
import sys
from abc import ABC, abstractmethod
import inspect
from functools import wraps
from datetime import date

from datetime import datetime, date

def parse_value(ann, s: str):
    if ann is date:
        try:
            return datetime.strptime(s, "%d.%m.%Y").date()
        except ValueError as e:
            raise ValueError("Expected date in format DD.MM.YYYY") from e
    return ann(s)


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

def gather_parameters(response_validator: Callable[[str], None], func: Callable[..., any]) -> Callable[..., any]: # Gathers parameters via input() to create a partial() that no longer requires arguments
        print(f"You are now prompted to input the fields required to construct {func.__name__}.")
        parameter = inspect.signature(func)
        for p in parameter.parameters.values():
            response_correct = False # We repeat the questions until there is a correct response
            while not response_correct:
                response = None #Initilizing in the outer scope,.
                arg = None # Argument to our Contact constructor
                print(f"Input parameter '{p.name}' of type {p.annotation}")
                response = input(">>>")
                response_validator(response) # Handles possible control flow inputs
                # Try to instantiate the datatype using the anotated datatype:
                # This does all the checking for us...
                try:
                    arg = parse_value(p.annotation, response)
                    response_correct = True
                    func = partial(func, arg) # Reduce the function parameters
                    break
                except Exception as e:
                    print(str(e))
                    continue
        return func
                    

class Component(ABC):
    universal_actions: tuple[Action] = (Action.MAIN_MENU, Action.EXIT) # They are accessible from all components
    actions: dict[Action, any] = {} # From each component only a subset of these will be accessible

    def __init__(self, provides: Action):
        # self is always going to be a child class instance as Component is abstract.
        self.actions[provides] = self # Such that other instances can call the newly registered component.


def call_component_again_on_error(call_operator: Callable[..., any]):
    @wraps(call_operator)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return call_operator(*args, **kwargs)
            except ValueError: # User did not input an int
                print(f"Expected the string of the option or an integer!")
                return call_operator(*args, **kwargs) # Try the same UI component again.
            except IndexError: # look if the index is within range
                print("Your choice is not in the option range!") # If there is an exception, we want to repeat the UI component:
            except KeyError: # Dictionary of the action does not exist in available actions
                print("This action has not be implemented yet!")
    return wrapper

class   UserEnteredControlFlowError(Exception):
    pass

def call_control_flow_on_control_flow_stament(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except UserEnteredControlFlowError as e: # Abort the input sequence
                action = Action(e.args[0])              # convert "exit" -> Action.EXIT
                Component.actions[action]()             # jump to component
                return None
    return wrapper



class   TextInputComponent(Component):
    def __init__(self, provides: Action, effects: Callable[[Callable[[str], None]], any]):
        super().__init__(provides)
        self.available_text_actions: tuple[Actions] = super().universal_actions
        self._effects = effects

    @call_component_again_on_error
    @call_control_flow_on_control_flow_stament
    def __call__(self):
        for effect in self._effects:
            effect(self.validate_user_response)

    def validate_user_response(self, response: str): # A callback as the user can input both control statements like 'exit' as well as data literals like 'Justus' for name.
        actions_strings = list(map(str, self.available_text_actions))
        if response in actions_strings: # User entered control flow statement, an exception interrupts the input field sequence
            raise UserEnteredControlFlowError(response)
        


class   NumberedListComponent(Component):
    def __init__(self, provides: Action, actions_in_list: list[Action]):
        super().__init__(provides)
        actions_in_list[:0] = super().universal_actions
        self.actions_in_list = actions_in_list
        self._effects = None # By default no side effects

    def set_side_effects(self, effects: list[Callable[..., any]]):
        self._effects = effects

    @call_component_again_on_error
    def __call__(self):
        # If the Component has effects, execute them and return to the previous component in the call stack
        if self._effects:
            for effect in self._effects:
                effect()
            return
    
        for i, option in enumerate(self.actions_in_list):
            print(f"[{i}] {option}")

        choice_index = None # Initalizing it in the outer scope
        choice = input(">>")
        string_actions_in_list = list(map(str, self.actions_in_list)) # Need actual strings to compare actions to user input
        if choice in string_actions_in_list:
            choice_index = string_actions_in_list.index(choice)
        else:
            choice_index =  int(choice) # It is also okay if the user inputs the literal number

        next_component = Component.actions[self.actions_in_list[choice_index]]
        next_component()
        # If the next_component just executes a side effect and returns,
        # then we want to be at the same UI component that we came from.
        self()

def my_exit():
    # Join all the threads before exiting the program
    for thread in contact_manager_singleton.threads:
        thread.join()
    exit(0) # Exit code zero as it was a graceful exit


# We are going to implement both CLI (for testing)
# As well as wizzard (input()) driven UX
def main():
    main_menu = NumberedListComponent(provides=Action.MAIN_MENU, actions_in_list=[Action.ADD])

    exit = NumberedListComponent(provides=Action.EXIT, actions_in_list=[])
    exit.set_side_effects([
        my_exit
    ])

    add_contact = NumberedListComponent(provides=Action.ADD, actions_in_list=[Action.ADD_EMERGENCY, Action.ADD_PERSONAL, Action.ADD_WORK])

    add_emergency = TextInputComponent(provides=Action.ADD_EMERGENCY,
    effects=[
        # We use callbacks just like in JavaScript frameworks
        lambda validator: contact_manager_singleton.add_contact(gather_parameters(validator, EmergencyContact))
    ])

    add_personal = TextInputComponent(provides=Action.ADD_PERSONAL,
    effects=[
        # We use callbacks just like in JavaScript frameworks
        lambda validator: contact_manager_singleton.add_contact(gather_parameters(validator, PersonalContact))
    ])

    add_work = TextInputComponent(provides=Action.ADD_WORK,
    effects=[
        # We use callbacks just like in JavaScript frameworks
        lambda validator: contact_manager_singleton.add_contact(gather_parameters(validator, WorkContact))
    ])

    main_menu()

if __name__ == "__main__":
    main()