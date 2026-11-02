import json
from pathlib import Path

class JSONStorage:
    REQUIRED_FIELDS = {
        "patients": {"patient_id", "name", "phone", "age", "gender"},
        "clinicians": {"clinician_id", "name", "phone", "specialization"},
        "appointments": {
            "appointment_id",
            "patient_id",
            "clinician_id",
            "date",
            "time",
            "purpose"
        }
    }

    def __init__(self, directory=None):
        self.directory = (
            Path(directory) if directory is not None else Path(__file__).parent
        )
        self.directory.mkdir(parents=True, exist_ok=True)

        self.files = {
            "patients": self.directory / "patients.json",
            "clinicians": self.directory / "clinicians.json",
            "appointments": self.directory / "appointments.json"
        }

    def load(self, record_type):
        if record_type not in self.files:
            raise ValueError("Unknown record type.")

        path = self.files[record_type]

        if not path.exists() or path.stat().st_size == 0:
            return []

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError(f"{path.name} must contain a list.")

            if not all(isinstance(item, dict) for item in data):
                raise ValueError(f"{path.name} contains invalid records.")

            required_fields = self.REQUIRED_FIELDS[record_type]

            for index, item in enumerate(data, start=1):
                missing_fields = required_fields.difference(item)

                if missing_fields:
                    missing = ", ".join(sorted(missing_fields))
                    raise ValueError(
                        f"{path.name} record {index} is missing "
                        f"required fields: {missing}."
                    )

            return data

        except json.JSONDecodeError as error:
            raise ValueError(
                f"{path.name} contains malformed JSON. "
                "The original file was not changed."
            ) from error

    def save(self, record_type, records):
        if record_type not in self.files:
            raise ValueError("Unknown record type.")

        path = self.files[record_type]
        temporary_path = path.with_name(path.name + ".tmp")

        try:
            with open(temporary_path, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=4)

            temporary_path.replace(path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    def load_all(self):
        return {
            "patients": self.load("patients"),
            "clinicians": self.load("clinicians"),
            "appointments": self.load("appointments")
        }

    def save_all(self, patients, clinicians, appointments):
        self.save(
            "patients",
            [patient.to_dict() for patient in patients.values()]
        )

        self.save(
            "clinicians",
            [clinician.to_dict() for clinician in clinicians.values()]
        )

        self.save(
            "appointments",
            [appointment.to_dict() for appointment in appointments.values()]
        )
