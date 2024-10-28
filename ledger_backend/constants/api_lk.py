from typing import Final, Set

# This class, APILK, serves as a centralized place to store API action keys as constants.
# Each action is defined as a class-level constant with a descriptive name for clarity and consistency.
# Additionally, the NO_METERING_APIS set lists certain APIs (like REGISTER, LOGIN, LOGOUT) that should not be metered or tracked for usage.
# Using Final ensures these constants are immutable and won't be accidentally changed elsewhere in the code.

class APILK:

    # A
    # B
    # C
    CREATE_ACCOUNT: Final[str] = "CREATE_ACCOUNT"
    CREATE_TRANSACTION: Final[str] = "CREATE_TRANSACTION"
    # D
    # E
    # F
    # G
    # H
    # I
    # J
    # K

    # L
    LOGIN: Final[str] = "LOGIN"
    LOGOUT: Final[str] = "LOGOUT"
    # M
    # N
    # O
    # P
    # Q

    # R
    REGISTER: Final[str] = "REGISTER"

    # S
    # T
    # U
    # V
    # X
    # Y
    # Z


    NO_METERING_APIS: Final[Set[str]] = {
        REGISTER, 
        LOGIN, 
        LOGOUT,
    }
