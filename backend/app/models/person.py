"""
person.py
---------
Domain-layer abstract base class `Person`.

OOP concepts demonstrated here:

- **Abstraction**: `Person` is an ABC (Abstract Base Class). It defines
  *what* every person in the bank must be able to do
  (`get_dashboard_permissions`) without saying *how* -- that's left to
  each subclass. You can never do `Person(...)` directly; Python raises
  a TypeError if you try, because it has an abstractmethod.

- **Encapsulation**: `_full_name`, `_email` etc. are stored with a
  leading underscore (protected) and only exposed through `@property`
  getters. `email` also has a setter that validates the format before
  allowing the change -- so a caller can never put the object into an
  invalid state from outside.
"""
from abc import ABC, abstractmethod


class Person(ABC):
    def __init__(self, user_id: int, full_name: str, email: str, phone: str | None = None):
        self._user_id = user_id
        self._full_name = full_name
        self._email = email
        self._phone = phone

    # ---------- Encapsulated properties ----------
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str):
        if not value or not value.strip():
            raise ValueError("full_name cannot be empty")
        self._full_name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if "@" not in value:
            raise ValueError("Invalid email address")
        self._email = value

    @property
    def phone(self) -> str | None:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        self._phone = value

    # ---------- Abstraction ----------
    @abstractmethod
    def get_dashboard_permissions(self) -> list[str]:
        """Every concrete subclass MUST implement this. It answers:
        'what can this kind of person see/do on their dashboard?'"""
        raise NotImplementedError

    @abstractmethod
    def get_role(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._user_id} name={self._full_name!r}>"
