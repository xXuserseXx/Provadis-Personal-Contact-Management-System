from __future__ import annotations

from datetime import date, datetime
import importlib

import pytest

from ContactManagement import (
    ContactManager,
    EmergencyContact,
    Mail,
    Name,
    PersonalContact,
    PhoneNumber,
    WorkContact,
)


@pytest.fixture()
def temp_contact_storage(tmp_path, monkeypatch):
    """Redirect ContactManager's JSON storage to a temp file for isolated tests."""
    contact_manager_module = importlib.import_module("ContactManagement.ContactManager")
    temp_file = tmp_path / "contacts.json"
    monkeypatch.setattr(contact_manager_module, "json_file", temp_file)
    return temp_file


def test_contact_subclasses_build_search_strings_and_serialize():
    """Each contact subclass should expose its data in readable and serializable form."""
    birthday = date(1999, 12, 30)

    # Build one of each contact subclass so we can validate shared behavior.
    personal = PersonalContact("Justus", "+49 151 234 567", "gg.jr@example.de", birthday)
    work = WorkContact(
        "Justus",
        "0049-151-234-567",
        "gg.jr@example.de",
        "FleischbergBrothers",
        "dr.rer.med",
    )
    emergency = EmergencyContact("Justus", "+1 415 555 0101", "gg.jr@example.de", 7)

    # Each contact should include its core data in a search string.
    assert "Justus" in personal.to_searchable_string()
    assert "FleischbergBrothers" in work.to_searchable_string()
    assert "7" in emergency.to_searchable_string()

    # Every contact should provide a dict with ISO timestamps and constructor args.
    personal_payload = personal.to_dict()
    assert personal_payload["contact_type"] == "PersonalContact"
    assert personal_payload["name"] == "Justus"
    assert personal_payload["phone"] == "+49 151 234 567"
    assert personal_payload["email"] == "gg.jr@example.de"
    assert personal_payload["birthday"] == birthday.isoformat()
    assert personal_payload["args"] == [
        "Justus",
        "+49 151 234 567",
        "gg.jr@example.de",
        birthday.isoformat(),
    ]
    # The created_at timestamp should be in ISO format and parseable.
    datetime.fromisoformat(personal_payload["created_at"])


def test_regular_expression_value_objects_validate_inputs():
    """Mail, PhoneNumber, and Name should reject invalid inputs with clear errors."""
    # Valid cases are accepted.
    assert Mail("luis.gaertner@stud-provadis.de") == "luis.gaertner@stud-provadis.de"
    assert PhoneNumber("+49 151 234 567") == "+49 151 234 567"
    assert Name("Justus Max-Redlin") == "Justus Max-Redlin"

    # Invalid formats should raise a ValueError.
    with pytest.raises(ValueError):
        Mail("bad@address@invalid")
    with pytest.raises(ValueError):
        PhoneNumber("not-a-number")
    with pytest.raises(ValueError):
        Name("Justus  Redlin")

    # Invalid types should raise a TypeError.
    with pytest.raises(TypeError):
        Mail(123)
    with pytest.raises(TypeError):
        PhoneNumber(123)
    with pytest.raises(TypeError):
        Name(123)


def test_contact_manager_add_search_group_remove():
    """ContactManager should manage the contact list as expected."""
    manager = ContactManager()
    personal = PersonalContact("Justus", "+49 151 234 567", "gg.jr@example.de", date(1999, 12, 30))
    work = WorkContact("Nadine", "0049-151-123-456", "nadine@example.com", "Acme", "Engineer")

    # Adding contacts should make them visible in the list.
    manager.add_contact(personal)
    manager.add_contact(work)
    assert manager.list_contacts() == [personal, work]

    # Search should find contacts by any searchable field.
    search_results = manager.search_contacts("acme")
    assert search_results == [work]

    # Grouping should bucket by contact type.
    grouped = manager.group_by_type()
    assert grouped["PersonalContact"] == [personal]
    assert grouped["WorkContact"] == [work]

    # Removing by name should return a boolean and update the list.
    assert manager.remove_contact("Justus") is True
    assert manager.list_contacts() == [work]
    assert manager.remove_contact("Missing") is False


def test_contact_manager_saves_and_loads_round_trip(temp_contact_storage):
    """Saving and loading should preserve the contact data and types."""
    manager = ContactManager()
    personal = PersonalContact("Justus", "+49 151 234 567", "gg.jr@example.de", date(1999, 12, 30))
    emergency = EmergencyContact("Nora", "+1 415 555 0101", "nora@example.com", 3)
    manager.add_contact(personal)
    manager.add_contact(emergency)

    # Save contacts to the temporary file and wait for the save thread to finish.
    manager.save_contacts()
    for thread in manager.threads:
        thread.join()

    # Load the contacts into a new manager and confirm types/fields.
    reloaded_manager = ContactManager()
    reloaded_manager.load_contacts()
    reloaded_contacts = reloaded_manager.list_contacts()

    assert len(reloaded_contacts) == 2
    assert any(isinstance(contact, PersonalContact) for contact in reloaded_contacts)
    assert any(isinstance(contact, EmergencyContact) for contact in reloaded_contacts)

    # Verify that the data survived the round-trip.
    names = {contact.name for contact in reloaded_contacts}
    assert names == {"Justus", "Nora"}
