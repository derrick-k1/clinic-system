from datetime import date, time, datetime, timedelta

class Appointment:
    STATUSES = ["scheduled", "completed", "cancelled"]

    def __init__(
        self,
        appointment_id,
        patient_id,
        clinician_id,
        appointment_date,
        appointment_time,
        purpose,
        duration=30,
        status="scheduled"
    ):
        self._appointment_id = self._validate_text(
            appointment_id, "Appointment ID"
        )
        self._patient_id = self._validate_text(patient_id, "Patient ID")
        self._clinician_id = self._validate_text(clinician_id, "Clinician ID")

        self._date = self.validate_date(appointment_date)
        self._time = self.validate_time(appointment_time)

        self._purpose = self._validate_text(purpose, "Purpose")

        if isinstance(duration, bool) or not isinstance(duration, int):
            raise ValueError("Duration must be a whole number.")

        if duration < 1 or duration > 480:
            raise ValueError("Duration must be between 1 and 480 minutes.")

        self._duration = duration

        if status not in self.STATUSES:
            raise ValueError("Invalid appointment status.")

        self._status = status

    @staticmethod
    def _validate_text(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("{} cannot be empty.".format(label))
        return value.strip()

    @staticmethod
    def validate_date(value):
        if isinstance(value, date) and not isinstance(value, datetime):
            return value

        try:
            text = str(value).strip()
            parsed = date.fromisoformat(text)
            if parsed.isoformat() != text:
                raise ValueError
            return parsed
        except (TypeError, ValueError):
            raise ValueError("Use YYYY-MM-DD for the date.")

    @staticmethod
    def validate_time(value):
        if isinstance(value, time):
            if value.tzinfo is not None or value.second or value.microsecond:
                raise ValueError("Use HH:MM for the time.")
            return value

        try:
            text = str(value).strip()
            parsed = datetime.strptime(text, "%H:%M").time()
            if parsed.strftime("%H:%M") != text:
                raise ValueError
            return parsed
        except (TypeError, ValueError):
            raise ValueError("Use HH:MM for the time.")

    @property
    def appointment_id(self):
        return self._appointment_id

    @property
    def patient_id(self):
        return self._patient_id

    @property
    def clinician_id(self):
        return self._clinician_id

    @property
    def appointment_date(self):
        return self._date

    @property
    def appointment_time(self):
        return self._time

    @property
    def purpose(self):
        return self._purpose

    @property
    def duration(self):
        return self._duration

    @property
    def status(self):
        return self._status

    @property
    def start_datetime(self):
        return datetime.combine(self._date, self._time)

    @property
    def end_datetime(self):
        return self.start_datetime + timedelta(minutes=self.duration)

    def update_schedule(self, new_date, new_time):
        validated_date = self.validate_date(new_date)
        validated_time = self.validate_time(new_time)
        self._date = validated_date
        self._time = validated_time

    def cancel(self):
        if self.status != "scheduled":
            raise ValueError("Only scheduled appointments can be cancelled.")

        self._status = "cancelled"

    def complete(self):
        if self.status != "scheduled":
            raise ValueError("Only scheduled appointments can be completed.")

        self._status = "completed"

    def restore_status(self, status):
        if status not in self.STATUSES:
            raise ValueError("Invalid status.")

        self._status = status

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "clinician_id": self.clinician_id,
            "date": self.appointment_date.isoformat(),
            "time": self.appointment_time.strftime("%H:%M"),
            "purpose": self.purpose,
            "duration": self.duration,
            "status": self.status
        }

    def __str__(self):
        return (
            f"Appointment ID: {self.appointment_id} | "
            f"Patient: {self.patient_id} | "
            f"Clinician: {self.clinician_id} | "
            f"Date: {self.appointment_date} | "
            f"Time: {self.appointment_time.strftime('%H:%M')} | "
            f"Duration: {self.duration} minutes | "
            f"Purpose: {self.purpose} | "
            f"Status: {self.status}"
        )
