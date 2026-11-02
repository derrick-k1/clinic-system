class Person:
    def __init__(self, person_id, name, phone):
        self._person_id = self._validate_text(person_id, "ID")
        self._name = self._validate_text(name, "Name")
        self._phone = self._validate_text(phone, "Phone number")

    @staticmethod
    def _validate_text(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("{} cannot be empty.".format(label))
        return value.strip()

    @property
    def person_id(self):
        return self._person_id

    @property
    def name(self):
        return self._name

    @property
    def phone(self):
        return self._phone

    def update_name(self, name):
        self._name = self._validate_text(name, "Name")

    def update_phone(self, phone):
        self._phone = self._validate_text(phone, "Phone")

    def to_dict(self):
        return {
            "person_id": self.person_id,
            "name": self.name,
            "phone": self.phone
        }

    def __str__(self):
        return f"{self.person_id} | {self.name} | {self.phone}"
