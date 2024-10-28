from sqlalchemy import Column, BigInteger, Float, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

from models.account import Account
from models.user import User

# This code defines the Transaction class, representing the 'transaction' table in the database.
# The table stores transactional data, linking payers and payees via their account IDs and URNs.
# It also stores the transaction amount, purpose, and timestamps for creation and updates.
# The ForeignKey relationships link transactions to the user and account tables for integrity.

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    urn = Column(Text)
    payer_account_id = Column(BigInteger, ForeignKey(Account.id))
    payer_account_urn = Column(Text, nullable=True)
    payee_account_id = Column(BigInteger, ForeignKey(Account.id))
    payee_account_urn = Column(Text, nullable=True)
    amount = Column(Float)
    purpose = Column(Text, nullable=True)
    created_on = Column(DateTime)
    created_by = Column(BigInteger, ForeignKey(User.id))
    updated_on = Column(DateTime)
    updated_by = Column(BigInteger)
