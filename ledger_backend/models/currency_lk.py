from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

# This code defines the CurrencyLK class which represents the 'currency_lk' table in the database.
# The table stores currency information such as the currency code, name, and description.
# It also tracks when the currency data was created and last updated.
# The id is an auto-incremented primary key, ensuring each currency entry is unique.

Base = declarative_base()

class CurrencyLK(Base):
    __tablename__ = 'currency_lk'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(Text)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
