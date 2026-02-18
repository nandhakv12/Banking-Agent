"""
Tools module - All banking tools
"""

from tools.account_tools import ACCOUNT_TOOLS, create_bank_account, get_all_accounts, get_account_details
from tools.balance_tools import BALANCE_TOOLS, check_balance, get_total_balance
from tools.transfer_tools import TRANSFER_TOOLS, transfer_between_accounts
from tools.transaction_tools import TRANSACTION_TOOLS, get_transaction_history

# All tools combined
ALL_TOOLS = ACCOUNT_TOOLS + BALANCE_TOOLS + TRANSFER_TOOLS + TRANSACTION_TOOLS

# Tool function mapping
TOOL_FUNCTIONS = {
    "create_bank_account": create_bank_account,
    "get_all_accounts": get_all_accounts,
    "get_account_details": get_account_details,
    "check_balance": check_balance,
    "get_total_balance": get_total_balance,
    "transfer_between_accounts": transfer_between_accounts,
    "get_transaction_history": get_transaction_history
}