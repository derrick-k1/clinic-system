from datetime import datetime
from decorators import log_operation, measure_time
from appointment import Appointment

class AppointmentManager:
    def __init__(self, patients, clinicians, appointments, storage):
        self.patients = patients
        self.clinicians = clinicians
        self.appointments = appointments
        self.storage = storage

    def generate_id(self):
        numbers = []

        for appointment_id in self.appointments:
            if appointment_id.startswith("A"):
                try:
                    numbers.append(int(appointment_id[1:]))
                except ValueError:
                    continue

        return f"A{max(numbers, default=0) + 1:03d}"

    def check_references(self, patient_id, clinician_id):
        if patient_id not in self.patients:
            raise ValueError("Patient does not exist.")

        if clinician_id not in self.clinicians:
            raise ValueError("Clinician does not exist.")

    def has_conflict(self, clinician_id, start, end, exclude_id=None):
        for appointment in self.appointments.values():
            if appointment.appointment_id == exclude_id:
                continue

            if appointment.clinician_id != clinician_id:
                continue

            if appointment.status != "scheduled":
                continue

            if (
                start < appointment.end_datetime
                and end > appointment.start_datetime
            ):
                return True

        return False

    @log_operation
    def schedule_appointment(
        self,
        patient_id,
        clinician_id,
        appointment_date,
        appointment_time,
        purpose,
        duration=30
    ):
        self.check_references(patient_id, clinician_id)

        appointment = Appointment(
            self.generate_id(),
            patient_id,
            clinician_id,
            appointment_date,
            appointment_time,
            purpose,
            duration
        )

        if appointment.start_datetime <= datetime.now():
            raise ValueError("Appointment must be in the future.")

        if self.has_conflict(
            clinician_id,
            appointment.start_datetime,
            appointment.end_datetime
        ):
            raise ValueError("This clinician already has an appointment then.")

        self.appointments[appointment.appointment_id] = appointment

        try:
            self.storage.save_all(
                self.patients,
                self.clinicians,
                self.appointments
            )
        except Exception:
            del self.appointments[appointment.appointment_id]
            raise

        return appointment

    @log_operation
    def reschedule_appointment(self, appointment_id, new_date, new_time):
        if appointment_id not in self.appointments:
            raise ValueError("Appointment not found.")

        appointment = self.appointments[appointment_id]

        if appointment.status != "scheduled":
            raise ValueError("Only scheduled appointments can be rescheduled.")

        old_date = appointment.appointment_date
        old_time = appointment.appointment_time

        appointment.update_schedule(new_date, new_time)

        try:
            if appointment.start_datetime <= datetime.now():
                raise ValueError("New appointment time must be in the future.")

            if self.has_conflict(
                appointment.clinician_id,
                appointment.start_datetime,
                appointment.end_datetime,
                exclude_id=appointment_id
            ):
                raise ValueError("This clinician already has an appointment then.")

            self.storage.save_all(
                self.patients,
                self.clinicians,
                self.appointments
            )

        except Exception:
            appointment.update_schedule(old_date, old_time)
            raise

        return appointment

    @log_operation
    def cancel_appointment(self, appointment_id):
        if appointment_id not in self.appointments:
            raise ValueError("Appointment not found.")

        appointment = self.appointments[appointment_id]
        old_status = appointment.status

        appointment.cancel()

        try:
            self.storage.save_all(
                self.patients,
                self.clinicians,
                self.appointments
            )
        except Exception:
            appointment.restore_status(old_status)
            raise

    @log_operation
    def complete_appointment(self, appointment_id):
        if appointment_id not in self.appointments:
            raise ValueError("Appointment not found.")

        appointment = self.appointments[appointment_id]
        old_status = appointment.status

        appointment.complete()

        try:
            self.storage.save_all(
                self.patients,
                self.clinicians,
                self.appointments
            )
        except Exception:
            appointment.restore_status(old_status)
            raise

    @staticmethod
    def _sort_appointments(appointments):
        return sorted(
            appointments,
            key=lambda appointment: appointment.start_datetime
        )

    def get_patient_appointments(self, patient_id):
        return self._sort_appointments(
            appointment
            for appointment in self.appointments.values()
            if appointment.patient_id == patient_id
        )

    def get_clinician_appointments(self, clinician_id):
        return self._sort_appointments(
            appointment
            for appointment in self.appointments.values()
            if appointment.clinician_id == clinician_id
        )

    def get_appointments_by_date(self, selected_date):
        selected_date = Appointment.validate_date(selected_date)

        return self._sort_appointments(
            appointment
            for appointment in self.appointments.values()
            if appointment.appointment_date == selected_date
        )

    def search_appointments(self, search_term):
        search_term = search_term.lower()

        return [
            appointment
            for appointment in self.appointments.values()
            if (
                search_term in appointment.appointment_id.lower()
                or search_term in appointment.patient_id.lower()
                or search_term in appointment.clinician_id.lower()
                or search_term in appointment.purpose.lower()
            )
        ]

    @measure_time
    def generate_daily_report(self, selected_date):
        appointments = self.get_appointments_by_date(selected_date)

        summary = {
            "scheduled": 0,
            "completed": 0,
            "cancelled": 0
        }

        for appointment in appointments:
            summary[appointment.status] += 1

        return {
            "date": Appointment.validate_date(selected_date),
            "summary": summary,
            "appointments": appointments
        }
