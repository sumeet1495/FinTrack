from sqlalchemy import Column, BigInteger, Float, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

from models.user import User
from models.account import Account

# The Balances class defines the 'balances' table in the database. 
# This table links to accounts and tracks financial information such as total balance, credit, and debit balances.
# Foreign keys link the balances to the associated 'Account' and 'User' tables.
# The table includes fields for balance creation and updates, helping maintain a record of when the balance data was created and last updated.
# The structure also allows for tracking the account's state (e.g., total balance) over time.

Base = declarative_base()

class Balances(Base):
    __tablename__ = 'balances'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey(Account.id))
    account_urn = Column(Text, nullable=False)
    total_balance = Column(Float)
    total_credit_balance = Column(Float)
    total_debit_balance = Column(Float)
    created_on = Column(DateTime)
    created_by = Column(BigInteger, ForeignKey(User.id))
    updated_on = Column(DateTime)
    updated_by = Column(BigInteger)
