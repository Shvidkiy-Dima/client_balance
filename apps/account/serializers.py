from flask import current_app
from marshmallow import Schema, fields, ValidationError
from apps.account.models import Account, Transaction


class TransactionSchema(Schema):
    account_uuid = fields.UUID(required=True)
    amount = fields.Decimal(required=True)

    def load_with_transaction(self, data, transaction_type):
        res = self.load(data)
        res['account'] = account = self.load_account(res['account_uuid'])

        if transaction_type == Transaction.TransactionType.WITHDRAW \
                and account.balance - res['amount'] < 0:

            raise ValidationError({"message": 'Lack of money', 'code': 'lack_of'})

        return res

    def load_account(self, account_uuid):
        acc, is_locked = Account.get_locked_account(account_uuid)

        if is_locked:
            raise ValidationError({"message":"Blocked by the transaction", 'code': 'locked'})

        if acc is None:
            raise ValidationError({'message': f'Account with uuid {account_uuid} doesnt exists', 'code': 'not_found'})

        return acc

    def create(self, data, transaction_type):

        account = data['account']

        if transaction_type == Transaction.TransactionType.DEPOSIT:
            account.balance += data['amount']

        else:
            account.balance -= data['amount']

        transaction = Transaction(account_uuid=account.uuid, amount=data['amount'],
                                  transaction_type=transaction_type)

        current_app.session.add(transaction)
        current_app.session.commit()
        return transaction


TransactionSerializer = TransactionSchema()
