from person import Person

class Patient(Person):
    def __init__(self, patient_id, name, phone, age, gender):
        super().__init__(patient_id, name, phone)

        self._age = self.validate_age(age)
        self._gender = self._validate_text(gender, "Gender")

    @staticmethod
    def validate_age(age):
        if isinstance(age, bool) or not isinstance(age, int):
            raise ValueError("Age must be a number.")

        if age < 0 or age > 130:
            raise ValueError("Age must be between 0 and 130.")

        return age

    @property
    def age(self):
        return self._age

    @property
    def gender(self):
        return self._gender

    def update_age(self, age):
        self._age = self.validate_age(age)

    def update_gender(self, gender):
        self._gender = self._validate_text(gender, "Gender")

    def to_dict(self):
        return {
            "patient_id": self.person_id,
            "name": self.name,
            "phone": self.phone,
            "age": self.age,
            "gender": self.gender
        }

    def __str__(self):
        return (
            f"Patient ID: {self.person_id} | "
            f"Name: {self.name} | "
            f"Phone: {self.phone} | "
            f"Age: {self.age} | "
            f"Gender: {self.gender}"
        )
