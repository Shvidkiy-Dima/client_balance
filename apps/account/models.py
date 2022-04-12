import enum
from typing import Tuple, Union
from decimal import Decimal
from sqlalchemy.exc import OperationalError
from sqlalchemy import Column, DECIMAL,  ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import BaseModel
from utils.models import IntEnum


class Account(BaseModel):
    __tablename__ = "Account"

    balance = Column(DECIMAL(12, 2), default=Decimal(0.00), nullable=False)

    @classmethod
    def get_locked_account(cls, acc_uuid) -> Tuple[Union["Account", None], bool]:
        """
        UPDATE FOR NOWAIT - lock row from account table while transaction not end.

        :return: (Account, is_locked)
        """
        try:
            acc = cls.query.with_for_update(nowait=True).get(acc_uuid)
        except OperationalError:
            return None, True

        return acc, False


class Transaction(BaseModel):
    __tablename__ = "Transaction"

    class TransactionType(enum.Enum):
        DEPOSIT = 0
        WITHDRAW = 1

    amount = Column(DECIMAL(12, 2), nullable=False)
    transaction_type = Column(IntEnum(TransactionType), nullable=False)

    account_uuid = Column(UUID(as_uuid=True), ForeignKey('Account.uuid'), nullable=False)
    account = relationship('Account', backref='transactions')
