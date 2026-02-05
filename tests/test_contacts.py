from ContactManagement import Contact, ContactManager, EmergencyContact, PersonalContact, WorkContact
from datetime import date

def test_contact_classes():
    ContactManager()
    EmergencyContact(name="Justus", phone="187", email="gg.jr@187.de", priority_level=1)
    PersonalContact(name="Justus", phone="187", email="gg.jr@187.de", birthday=date(1999, 12, 30)) # date(year, month, date)
    WorkContact(name="Justus", phone="187", email="gg.jr@187.de", company="FleischbergBrothers", job_title="dr.rer.med")

