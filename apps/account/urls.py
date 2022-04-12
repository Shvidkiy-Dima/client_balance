from . import bp
from apps.account import views

bp.add_url_rule('/deposit/', view_func=views.DepositView.as_view('deposit'))
bp.add_url_rule('/withdraw/', view_func=views.WithdrawView.as_view('withdraw'))
bp.add_url_rule('/balance/<uuid:account_uuid>/', view_func=views.balance)

bp.add_url_rule('/_make_user/', view_func=views._make_user, methods=['POST'])
