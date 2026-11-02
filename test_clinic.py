"""Standard-library workflow tests for the clinic system."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from unittest.mock import patch

from clinic import Clinic
from json_storage import JSONStorage
from main import ClinicCLI


class ClinicWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.clinic = Clinic(JSONStorage(self.temporary_directory.name))
        self.patient = self.clinic.register_patient(
            "Jordan Lee", "555-0100", 35, "Female"
        )
        self.clinician = self.clinic.register_clinician(
            "Dr. Patel", "555-0200", "Family Medicine"
        )
        self.appointment_date = date.today() + timedelta(days=2)
        self.manager = self.clinic.appointment_manager

    def tearDown(self):
        self.temporary_directory.cleanup()

    def schedule(self, appointment_time="10:00", purpose="Consultation"):
        return self.manager.schedule_appointment(
            self.patient.person_id,
            self.clinician.person_id,
            self.appointment_date.isoformat(),
            appointment_time,
            purpose,
            30,
        )

    def test_registration_search_update_and_validation(self):
        self.assertEqual(self.clinic.search_patients("jordan"), [self.patient])
        self.assertEqual(self.clinic.search_clinicians("patel"), [self.clinician])
        self.clinic.update_patient(self.patient.person_id, name="Jordan Smith")
        self.clinic.update_clinician(
            self.clinician.person_id, specialization="Internal Medicine"
        )
        with self.assertRaises(ValueError):
            self.clinic.update_patient(
                self.patient.person_id, name="Changed", age=-1
            )
        self.assertEqual(self.patient.name, "Jordan Smith")
        self.assertEqual(
            self.clinician.specialization, "Internal Medicine"
        )

    def test_overlap_is_rejected_and_reschedule_is_safe(self):
        first = self.schedule("10:00")
        second = self.schedule("11:00", "Follow-up")
        with self.assertRaisesRegex(ValueError, "appointment then"):
            self.schedule("10:15", "Conflict")
        with self.assertRaisesRegex(ValueError, "appointment then"):
            self.manager.reschedule_appointment(
                second.appointment_id, self.appointment_date, "10:20"
            )
        with self.assertRaisesRegex(ValueError, "HH:MM"):
            self.manager.reschedule_appointment(
                second.appointment_id,
                self.appointment_date + timedelta(days=1),
                "12:00:00",
            )
        self.assertEqual(second.appointment_date, self.appointment_date)
        self.assertEqual(second.appointment_time.strftime("%H:%M"), "11:00")
        self.manager.reschedule_appointment(
            second.appointment_id, self.appointment_date, "12:00"
        )
        self.assertEqual(second.appointment_time.strftime("%H:%M"), "12:00")
        self.assertEqual(len(self.clinic.appointments), 2)
        self.assertEqual(first.status, "scheduled")

    def test_statuses_reports_and_persistence(self):
        cancelled = self.schedule("10:00")
        completed = self.schedule("11:00", "Follow-up")
        self.manager.cancel_appointment(cancelled.appointment_id)
        self.manager.complete_appointment(completed.appointment_id)
        self.assertEqual(
            len(self.manager.get_patient_appointments(self.patient.person_id)), 2
        )
        self.assertEqual(
            len(self.manager.get_clinician_appointments(self.clinician.person_id)), 2
        )
        report = self.manager.generate_daily_report(self.appointment_date)
        self.assertEqual(
            report["summary"],
            {"scheduled": 0, "completed": 1, "cancelled": 1},
        )

        reopened = Clinic(JSONStorage(self.temporary_directory.name))
        self.assertEqual(
            reopened.get_patient(self.patient.person_id).name, "Jordan Lee"
        )
        self.assertEqual(
            reopened.appointments[cancelled.appointment_id].status, "cancelled"
        )
        self.assertEqual(
            reopened.appointments[completed.appointment_id].status, "completed"
        )

    def test_future_and_format_validation(self):
        with self.assertRaisesRegex(ValueError, "future"):
            self.manager.schedule_appointment(
                self.patient.person_id,
                self.clinician.person_id,
                (date.today() - timedelta(days=1)).isoformat(),
                "00:00",
                "Past appointment",
            )
        with self.assertRaisesRegex(ValueError, "HH:MM"):
            self.schedule("10:00:00")

    def test_malformed_json_is_reported(self):
        path = os.path.join(self.temporary_directory.name, "patients.json")
        with open(path, "w", encoding="utf-8") as data_file:
            data_file.write("{malformed")
        with self.assertRaisesRegex(ValueError, "malformed JSON"):
            JSONStorage(self.temporary_directory.name).load("patients")

    def test_incomplete_json_record_is_reported(self):
        path = os.path.join(self.temporary_directory.name, "patients.json")
        with open(path, "w", encoding="utf-8") as data_file:
            json.dump([{"patient_id": "P001", "name": "Incomplete"}], data_file)

        with self.assertRaisesRegex(ValueError, "missing required fields"):
            Clinic(JSONStorage(self.temporary_directory.name))

    def test_empty_json_file_is_treated_as_no_records(self):
        storage = JSONStorage(self.temporary_directory.name)
        storage.files["patients"].write_text("", encoding="utf-8")

        self.assertEqual(storage.load("patients"), [])

    def test_failed_json_save_preserves_original_and_removes_temporary_file(self):
        storage = JSONStorage(self.temporary_directory.name)
        patient_file = storage.files["patients"]
        patient_file.write_text('[{"patient_id": "P001"}]', encoding="utf-8")

        with self.assertRaises(TypeError):
            storage.save("patients", [{"unsupported": object()}])

        self.assertEqual(
            patient_file.read_text(encoding="utf-8"),
            '[{"patient_id": "P001"}]'
        )
        self.assertFalse(patient_file.with_name("patients.json.tmp").exists())

    def test_invalid_appointment_references_are_rejected_on_load(self):
        data_directory = self.temporary_directory.name
        storage = JSONStorage(data_directory)
        with open(storage.files["appointments"], "w", encoding="utf-8") as data_file:
            json.dump(
                [{
                    "appointment_id": "A001",
                    "patient_id": "P404",
                    "clinician_id": "C404",
                    "date": "2026-12-15",
                    "time": "09:00",
                    "purpose": "Consultation"
                }],
                data_file
            )

        with self.assertRaisesRegex(ValueError, "unknown patient"):
            Clinic(storage)

    def test_cancelled_and_completed_appointments_do_not_block_time(self):
        cancelled = self.schedule("10:00")
        self.manager.cancel_appointment(cancelled.appointment_id)
        completed = self.schedule("10:00", "Replacement")
        self.manager.complete_appointment(completed.appointment_id)
        replacement = self.schedule("10:00", "Another replacement")
        self.assertEqual(replacement.status, "scheduled")

    def test_back_to_back_appointments_are_allowed(self):
        self.schedule("10:00")
        appointment = self.schedule("10:30", "Next consultation")
        self.assertEqual(appointment.appointment_time.strftime("%H:%M"), "10:30")

    def test_appointment_queries_return_chronological_order(self):
        later = self.schedule("11:00", "Later consultation")
        earlier = self.schedule("09:00", "Earlier consultation")

        patient_appointments = self.manager.get_patient_appointments(
            self.patient.person_id
        )
        clinician_appointments = self.manager.get_clinician_appointments(
            self.clinician.person_id
        )
        date_appointments = self.manager.get_appointments_by_date(
            self.appointment_date
        )
        report_appointments = self.manager.generate_daily_report(
            self.appointment_date
        )["appointments"]

        for appointments in (
            patient_appointments,
            clinician_appointments,
            date_appointments,
            report_appointments
        ):
            self.assertEqual(appointments, [earlier, later])

    def test_cli_displays_conflict_error_without_adding_appointment(self):
        self.schedule("10:00")
        application = ClinicCLI()
        application.clinic = self.clinic
        answers = [
            "3", "1",
            self.patient.person_id,
            self.clinician.person_id,
            self.appointment_date.isoformat(),
            "10:15",
            "Conflicting appointment",
            "30",
            "0", "0"
        ]
        output = io.StringIO()

        with patch("builtins.input", side_effect=answers):
            with redirect_stdout(output):
                application.run()

        self.assertIn(
            "Error: This clinician already has an appointment then.",
            output.getvalue()
        )
        self.assertEqual(len(self.clinic.appointments), 1)


if __name__ == "__main__":
    unittest.main()
