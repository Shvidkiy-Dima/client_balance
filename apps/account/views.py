from flask import make_response, jsonify, request, current_app, abort
from flask.views import MethodView
from marshmallow import ValidationError
from apps.account.models import Account, Transaction
from apps.account.serializers import TransactionSerializer


class AccountBaseView(MethodView):
    serializer = TransactionSerializer
    transaction_type = None

    def get_data(self):
        try:
           data = self.serializer.load_with_transaction(data=request.json,
                                                        transaction_type=self.transaction_type)
           is_valid = True
        except ValidationError as err:
            is_valid = False
            data = err.messages

        return is_valid, data

    def perform_crete(self, data):
        self.serializer.create(data, self.transaction_type)

    def post(self, *args, **kwargs):
        is_valid, data = self.get_data()

        if not is_valid:
            return jsonify(data), 400

        self.perform_crete(data)
        return '', 204


class DepositView(AccountBaseView):
    transaction_type = Transaction.TransactionType.DEPOSIT

    def post(self, *args, **kwargs):
        """
        Deposit
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
                type: object
                properties:
                    amount:
                        type: integer

                    account_uuid:
                        type: string

        responses:
          204:
             description: Successful
          400:
             description: Bad request.
          404:
             description: Account not found
        """
        return super().post(*args, **kwargs)


class WithdrawView(AccountBaseView):
    transaction_type = Transaction.TransactionType.WITHDRAW

    def post(self, *args, **kwargs):
        """
        Withdraw
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
                type: object
                properties:
                    amount:
                        type: integer

                    account_uuid:
                        type: string

        responses:
          204:
             description: Successful
          400:
             description: Bad request.
          404:
             description: Account not found
        """
        return super().post(*args, **kwargs)


def balance(account_uuid):
    """
    Get account balance
    ---
    parameters:
      - name: account_uuid
        in: path
        type: string
        required: true

    responses:
      200:
       schema:
        type: object
        properties:
          balance:
            type: string
            description: account balance

      404:
        description: Account not found


    """
    account = Account.query.get(account_uuid)
    if account is None:
        abort(404)

    return jsonify({'balance': account.balance}), 200


def _make_user():
    """
   Create test account
    ---
    responses:
      201:
       schema:
        type: object
        description: Create account
        properties:
          account_uuid:
            type: string
            description: account uuid
    """
    acc = Account()
    current_app.session.add(acc)
    current_app.session.commit()
    return make_response(jsonify({'account_uuid': str(acc.uuid)}), 201)
