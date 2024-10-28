from sqlalchemy import Column, BigInteger, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from models.user import User
from models.currency_lk import CurrencyLK

# The Account model represents the 'account' table in the database. 
# It stores details about user accounts, such as their balance, associated user, currency, and timestamps for creation and updates.
# Foreign keys link the account to the User and CurrencyLK models, creating relationships between these entities.
# Additional fields track if the account has been deleted and who created or last updated the record.

Base = declarative_base()

class Account(Base):
    __tablename__ = 'account'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(Text, nullable=False)
    user_id = Column(BigInteger, ForeignKey(User.id))
    name = Column(Text, nullable=False)
    currency_id = Column(BigInteger, ForeignKey(CurrencyLK.id))
    balance = Column(Float, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_on = Column(DateTime)
    created_by = Column(BigInteger, ForeignKey(User.id))
    updated_on = Column(DateTime)
    updated_by = Column(BigInteger)
