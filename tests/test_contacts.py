from ContactManagement import Contact, ContactManager, EmergencyContact, PersonalContact, WorkContact
from datetime import date
import logging
log = logging.getLogger(__name__)

def test_construction_contact_classes():
    ContactManager()
    EmergencyContact(name="Justus", phone="187", email="gg.jr@187.de", priority_level=1)
    PersonalContact(name="Justus", phone="187", email="gg.jr@187.de", birthday=date(1999, 12, 30)) # date(year, month, date)
    WorkContact(name="Justus", phone="187", email="gg.jr@187.de", company="FleischbergBrothers", job_title="dr.rer.med")

def test_serialization_of_contacts():
    my_manager = ContactManager()
    my_contact = PersonalContact(name="Justus", phone="187", email="gg.jr@187.de", birthday=date(1999, 12, 30))
    my_contact2 = WorkContact(name="Justus", phone="187", email="gg.jr@187.de", company="FleischbergBrothers", job_title="dr.rer.med")
    my_manager.add_contact(my_contact)
    my_manager.add_contact(my_contact2)
    my_manager.save_contacts()

def test_deserialization_of_contacts():
    # Instantiate one contact manager to serialise the contacts:
    my_manager = ContactManager()
    my_contact = PersonalContact(name="Justus", phone="187", email="gg.jr@187.de", birthday=date(1999, 12, 30))
    my_contact2 = WorkContact(name="Justus", phone="187", email="gg.jr@187.de", company="FleischbergBrothers", job_title="dr.rer.med")
    my_manager.add_contact(my_contact)
    my_manager.add_contact(my_contact2)
    my_manager.save_contacts()

    # Now instantiate a new one to deserialize them:
    second_manager = ContactManager()
    second_manager.load_contacts()
    log.info("CONTACTS DESERIALIZED: %s", str(second_manager))