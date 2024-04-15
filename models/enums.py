from enum import Enum


class Status(Enum):
    PENDING = 'Pending'
    RESOLVED = 'Resolved'
    ON_HOLD = 'On hold'
    ASSIGNED = 'Assigned'
    CANCELLED = 'Cancelled'


class Priority(Enum):
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'
