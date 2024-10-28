from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Index
#
from sqlalchemy.ext.declarative import declarative_base

# This code defines the User class, which represents the 'user' table in the database.
# It contains essential user information such as email, password, and metadata like account creation, login status, and deletion status.
# The table includes indexed fields to enhance search performance on fields like 'urn', 'email', and 'created_at'.

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    # Defining the columns that make up the 'user' table
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    is_logged_in = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    last_login = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    
    # Indexes are added to improve query performance on specific fields like urn, email, and created_at.
    __table_args__ = (
        Index('idx_user_urn', 'urn'),
        Index('idx_user_email', 'email'),
        Index('idx_user_created_at', 'created_at'),
    )

    # String representation of the User object for easy debugging and logging.
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
