from person import Person

class Clinician(Person):
    def __init__(self, clinician_id, name, phone, specialization):
        super().__init__(clinician_id, name, phone)
        self._specialization = self._validate_text(
            specialization, "Specialization"
        )

    @property
    def specialization(self):
        return self._specialization

    def update_specialization(self, specialization):
        self._specialization = self._validate_text(
            specialization, "Specialization"
        )

    def to_dict(self):
        return {
            "clinician_id": self.person_id,
            "name": self.name,
            "phone": self.phone,
            "specialization": self.specialization
        }

    def __str__(self):
        return (
            f"Clinician ID: {self.person_id} | "
            f"Name: {self.name} | "
            f"Phone: {self.phone} | "
            f"Specialization: {self.specialization}"
        )
