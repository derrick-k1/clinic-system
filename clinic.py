from patient import Patient
from clinician import Clinician
from appointment import Appointment
from json_storage import JSONStorage
from appointment_manager import AppointmentManager

class Clinic:
    def __init__(self, storage=None):
        self.storage = storage or JSONStorage()

        self.patients = {}
        self.clinicians = {}
        self.appointments = {}

        self.load_data()

        self.appointment_manager = AppointmentManager(
            self.patients,
            self.clinicians,
            self.appointments,
            self.storage
        )

    def load_data(self):
        data = self.storage.load_all()

        for item in data["patients"]:
            patient = Patient(
                item["patient_id"],
                item["name"],
                item["phone"],
                item["age"],
                item["gender"]
            )

            if patient.person_id in self.patients:
                raise ValueError("Duplicate patient ID found.")

            self.patients[patient.person_id] = patient

        for item in data["clinicians"]:
            clinician = Clinician(
                item["clinician_id"],
                item["name"],
                item["phone"],
                item["specialization"]
            )

            if clinician.person_id in self.clinicians:
                raise ValueError("Duplicate clinician ID found.")

            self.clinicians[clinician.person_id] = clinician

        for item in data["appointments"]:
            appointment = Appointment(
                item["appointment_id"],
                item["patient_id"],
                item["clinician_id"],
                item["date"],
                item["time"],
                item["purpose"],
                item.get("duration", 30),
                item.get("status", "scheduled")
            )

            if appointment.appointment_id in self.appointments:
                raise ValueError("Duplicate appointment ID found.")

            if appointment.patient_id not in self.patients:
                raise ValueError("Appointment has an unknown patient.")

            if appointment.clinician_id not in self.clinicians:
                raise ValueError("Appointment has an unknown clinician.")

            self.appointments[appointment.appointment_id] = appointment

        saved = list(self.appointments.values())

        for index, appointment in enumerate(saved):
            if appointment.status != "scheduled":
                continue

            for other in saved[index + 1:]:
                if (
                    other.status == "scheduled"
                    and other.clinician_id == appointment.clinician_id
                    and appointment.start_datetime < other.end_datetime
                    and appointment.end_datetime > other.start_datetime
                ):
                    raise ValueError(
                        "Saved appointments contain a scheduling conflict."
                    )

    def save_data(self):
        self.storage.save_all(
            self.patients,
            self.clinicians,
            self.appointments
        )

    @staticmethod
    def generate_id(prefix, records):
        numbers = []

        for record_id in records:
            if record_id.startswith(prefix):
                try:
                    numbers.append(int(record_id[len(prefix):]))
                except ValueError:
                    continue

        return f"{prefix}{max(numbers, default=0) + 1:03d}"

    # PATIENT MANAGEMENT

    def register_patient(self, name, phone, age, gender):
        patient_id = self.generate_id("P", self.patients)

        patient = Patient(
            patient_id,
            name,
            phone,
            age,
            gender
        )

        self.patients[patient_id] = patient

        try:
            self.save_data()
        except Exception:
            del self.patients[patient_id]
            raise

        return patient

    def get_patient(self, patient_id):
        patient = self.patients.get(patient_id)

        if patient is None:
            raise ValueError("Patient not found.")

        return patient

    def search_patients(self, search_term):
        search_term = search_term.lower()

        return [
            patient
            for patient in self.patients.values()
            if (
                search_term in patient.person_id.lower()
                or search_term in patient.name.lower()
                or search_term in patient.phone.lower()
            )
        ]

    def update_patient(
        self,
        patient_id,
        name=None,
        phone=None,
        age=None,
        gender=None
    ):
        patient = self.get_patient(patient_id)

        old_values = (
            patient.name,
            patient.phone,
            patient.age,
            patient.gender
        )

        try:
            if name is not None:
                patient.update_name(name)

            if phone is not None:
                patient.update_phone(phone)

            if age is not None:
                patient.update_age(age)

            if gender is not None:
                patient.update_gender(gender)

            self.save_data()

        except Exception:
            patient.update_name(old_values[0])
            patient.update_phone(old_values[1])
            patient.update_age(old_values[2])
            patient.update_gender(old_values[3])
            raise

        return patient

    # CLINICIAN MANAGEMENT

    def register_clinician(self, name, phone, specialization):
        clinician_id = self.generate_id("C", self.clinicians)

        clinician = Clinician(
            clinician_id,
            name,
            phone,
            specialization
        )

        self.clinicians[clinician_id] = clinician

        try:
            self.save_data()
        except Exception:
            del self.clinicians[clinician_id]
            raise

        return clinician

    def get_clinician(self, clinician_id):
        clinician = self.clinicians.get(clinician_id)

        if clinician is None:
            raise ValueError("Clinician not found.")

        return clinician

    def search_clinicians(self, search_term):
        search_term = search_term.lower()

        return [
            clinician
            for clinician in self.clinicians.values()
            if (
                search_term in clinician.person_id.lower()
                or search_term in clinician.name.lower()
                or search_term in clinician.phone.lower()
                or search_term in clinician.specialization.lower()
            )
        ]

    def update_clinician(
        self,
        clinician_id,
        name=None,
        phone=None,
        specialization=None
    ):
        clinician = self.get_clinician(clinician_id)

        old_values = (
            clinician.name,
            clinician.phone,
            clinician.specialization
        )

        try:
            if name is not None:
                clinician.update_name(name)

            if phone is not None:
                clinician.update_phone(phone)

            if specialization is not None:
                clinician.update_specialization(specialization)

            self.save_data()

        except Exception:
            clinician.update_name(old_values[0])
            clinician.update_phone(old_values[1])
            clinician.update_specialization(old_values[2])
            raise

        return clinician
