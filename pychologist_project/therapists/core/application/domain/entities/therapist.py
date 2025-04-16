from datetime import datetime

class TherapistEntity:
    def __init__(self, id=None, user_id=None, name="", license_number="", specialization="", created_at=None, updated_at=None):
        self._id = id
        self._user_id = user_id
        self._name = name
        self._license_number = license_number
        self._specialization = specialization
        self._created_at = created_at
        self._updated_at = updated_at

    def __eq__(self, other):
        if not isinstance(other, TherapistEntity):
            return False
        return (
            self.id == other.id and
            self.user_id == other.user_id and
            self.name == other.name and
            self.license_number == other.license_number and
            self.specialization == other.specialization
        )

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, (int, type(None))):
            raise ValueError("ID must be an integer or None.")
        self._id = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        if not isinstance(value, (int, type(None))):
            raise ValueError("User ID must be an integer or None.")
        self._user_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        self._name = value

    @property
    def license_number(self):
        return self._license_number

    @license_number.setter
    def license_number(self, value):
        if not isinstance(value, str):
            raise ValueError("License number must be a string.")
        self._license_number = value

    @property
    def specialization(self):
        return self._specialization

    @specialization.setter
    def specialization(self, value):
        if not isinstance(value, str):
            raise ValueError("Specialization must be a string.")
        self._specialization = value

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        if not isinstance(value, (type(None), datetime)):
            raise ValueError("Created at must be a datetime object or None.")
        self._created_at = value

    @property
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        if not isinstance(value, (type(None), datetime)):
            raise ValueError("Updated at must be a datetime object or None.")
        self._updated_at = value

    def __repr__(self):
        return (
            f"TherapistEntity(id={self._id}, user_id={self._user_id}, name={self._name}, "
            f"license_number={self._license_number}, specialization={self._specialization})"
        )