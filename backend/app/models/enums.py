from enum import Enum


class UserRole(str, Enum):
    owner = "owner"
    admin = "admin"


class SessionStatus(str, Enum):
    planned = "planned"
    arrived = "arrived"
    completed = "completed"
    canceled = "canceled"
