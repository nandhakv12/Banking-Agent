"""
Firestore Database Operations
All database CRUD operations for accounts and transactions
"""

import sys
import os
import uuid
import random
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase.client import get_firestore, document_to_dict, collection_to_list
from config import (
    COLLECTION_USERS,
    COLLECTION_ACCOUNTS,
    COLLECTION_TRANSACTIONS,
    MIN_DEPOSIT,
    INTEREST_RATES,
    ROUTING_NUMBER,
    MAX_TRANSFER_AMOUNT,
    MAX_ACCOUNTS_PER_USER
)


# Add these constants right after imports
USERS_TABLE = COLLECTION_USERS
ACCOUNTS_TABLE = COLLECTION_ACCOUNTS
TRANSACTIONS_TABLE = COLLECTION_TRANSACTIONS
# ============================================================
# ACCOUNT OPERATIONS
# ============================================================

def generate_account_number() -> str:
    """Generate unique 12-digit account number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])


def create_account(user_id: str, account_type: str, initial_deposit: float, account_name: str = '') -> dict:
    """Create a new bank account"""
    try:
        db = get_firestore()
        account_type = account_type.lower()

        # Validate account type
        if account_type not in ['checking', 'savings']:
            return {'success': False, 'error': 'Account type must be checking or savings'}

        # Validate minimum deposit
        if initial_deposit < MIN_DEPOSIT[account_type]:
            return {
                'success': False,
                'error': f'Minimum deposit for {account_type} is ${MIN_DEPOSIT[account_type]:.2f}'
            }

        # Check max accounts limit
        user_accounts = db.collection(COLLECTION_ACCOUNTS)\
                          .where('user_id', '==', user_id)\
                          .where('status', '==', 'ACTIVE')\
                          .get()

        if len(list(user_accounts)) >= MAX_ACCOUNTS_PER_USER:
            return {
                'success': False,
                'error': f'Maximum {MAX_ACCOUNTS_PER_USER} accounts allowed per user'
            }

        # Generate account details
        account_id     = str(uuid.uuid4())
        account_number = generate_account_number()

        # Default account name
        if not account_name:
            count = len(list(user_accounts))
            account_name = f'My {account_type.title()} Account' if count == 0 else f'{account_type.title()} Account {count + 1}'

        # Create account
        account_data = {
            'account_id':        account_id,
            'user_id':           user_id,
            'account_number':    account_number,
            'routing_number':    ROUTING_NUMBER,
            'account_type':      account_type.upper(),
            'account_name':      account_name,
            'balance':           float(initial_deposit),
            'available_balance': float(initial_deposit),
            'currency':          'USD',
            'status':            'ACTIVE',
            'interest_rate':     INTEREST_RATES[account_type],
            'created_at':        datetime.utcnow().isoformat(),
            'updated_at':        datetime.utcnow().isoformat()
        }

        db.collection(COLLECTION_ACCOUNTS).document(account_id).set(account_data)

        # Create initial transaction
        create_transaction(
            account_id=account_id,
            user_id=user_id,
            transaction_type='CREDIT',
            amount=initial_deposit,
            balance_after=initial_deposit,
            description='Initial deposit',
            status='COMPLETED'
        )

        return {
            'success': True,
            'message': f'🎉 {account_type.title()} account created successfully!',
            'account': {
                'account_id':     account_id,
                'account_number': f'****{account_number[-4:]}',
                'routing_number': ROUTING_NUMBER,
                'account_type':   account_type.upper(),
                'account_name':   account_name,
                'balance':        initial_deposit,
                'interest_rate':  INTEREST_RATES[account_type],
                'status':         'ACTIVE'
            }
        }

    except Exception as e:
        return {'success': False, 'error': f'Failed to create account: {str(e)}'}


def get_accounts(user_id: str) -> dict:
    """Get all accounts for a user"""
    try:
        db = get_firestore()

        accounts_ref = db.collection(COLLECTION_ACCOUNTS)\
                         .where('user_id', '==', user_id)\
                         .where('status', '==', 'ACTIVE')

        accounts = collection_to_list(accounts_ref)

        # Format accounts for display
        formatted_accounts = []
        for acc in accounts:
            formatted_accounts.append({
                'account_id':        acc['account_id'],
                'account_number':    f'****{acc["account_number"][-4:]}',
                'account_type':      acc['account_type'],
                'account_name':      acc['account_name'],
                'balance':           acc['balance'],
                'available_balance': acc['available_balance'],
                'interest_rate':     acc['interest_rate'],
                'status':            acc['status']
            })

        total_balance = sum(acc['balance'] for acc in formatted_accounts)

        return {
            'success':       True,
            'accounts':      formatted_accounts,
            'total_accounts': len(formatted_accounts),
            'total_balance': total_balance
        }

    except Exception as e:
        return {'success': False, 'error': f'Failed to get accounts: {str(e)}'}


def get_account(account_id: str, user_id: str) -> dict:
    """Get specific account details"""
    try:
        db  = get_firestore()
        doc = db.collection(COLLECTION_ACCOUNTS).document(account_id).get()
        acc = document_to_dict(doc)

        if not acc:
            return {'success': False, 'error': 'Account not found'}

        # Verify ownership
        if acc['user_id'] != user_id:
            return {'success': False, 'error': 'Unauthorized access'}

        return {
            'success': True,
            'account': {
                'account_id':        acc['account_id'],
                'account_number':    f'****{acc["account_number"][-4:]}',
                'account_type':      acc['account_type'],
                'account_name':      acc['account_name'],
                'balance':           acc['balance'],
                'available_balance': acc['available_balance'],
                'interest_rate':     acc['interest_rate'],
                'routing_number':    acc['routing_number'],
                'status':            acc['status']
            }
        }

    except Exception as e:
        return {'success': False, 'error': f'Failed to get account: {str(e)}'}


def get_balance(account_id: str, user_id: str) -> dict:
    """Get account balance"""
    try:
        result = get_account(account_id, user_id)
        if not result['success']:
            return result

        account = result['account']
        return {
            'success':           True,
            'account_name':      account['account_name'],
            'account_type':      account['account_type'],
            'account_number':    account['account_number'],
            'balance':           account['balance'],
            'available_balance': account['available_balance'],
            'currency':          'USD'
        }

    except Exception as e:
        return {'success': False, 'error': f'Failed to get balance: {str(e)}'}


# ============================================================
# TRANSACTION OPERATIONS
# ============================================================

def create_transaction(account_id: str, user_id: str, transaction_type: str,
                      amount: float, balance_after: float, description: str,
                      status: str = 'COMPLETED', memo: str = '',
                      reference: str = '') -> dict:
    """Create a transaction record"""
    try:
        db = get_firestore()

        transaction_id = str(uuid.uuid4())

        transaction_data = {
            'transaction_id':   transaction_id,
            'account_id':       account_id,
            'user_id':          user_id,
            'transaction_type': transaction_type,
            'amount':           float(amount),
            'balance_after':    float(balance_after),
            'currency':         'USD',
            'description':      description,
            'memo':             memo,
            'reference':        reference,
            'status':           status,
            'created_at':       datetime.utcnow().isoformat()
        }

        db.collection(COLLECTION_TRANSACTIONS).document(transaction_id).set(transaction_data)

        return {'success': True, 'transaction_id': transaction_id}

    except Exception as e:
        return {'success': False, 'error': f'Failed to create transaction: {str(e)}'}


def get_transactions(account_id: str, user_id: str, limit: int = 10) -> dict:
    """Get transaction history for an account"""
    try:
        db = get_firestore()

        # Verify account ownership first
        account_result = get_account(account_id, user_id)
        if not account_result['success']:
            return account_result

        # Get transactions
        transactions_ref = db.collection(COLLECTION_TRANSACTIONS)\
                             .where('account_id', '==', account_id)\
                             .order_by('created_at', direction='DESCENDING')\
                             .limit(limit)

        transactions = collection_to_list(transactions_ref)

        # Format transactions
        formatted_txns = []
        for txn in transactions:
            formatted_txns.append({
                'transaction_id': txn['transaction_id'][:8],
                'type':           txn['transaction_type'],
                'amount':         txn['amount'],
                'description':    txn.get('description', ''),
                'balance_after':  txn['balance_after'],
                'date':           txn['created_at'][:10],
                'status':         txn['status']
            })

        return {
            'success':      True,
            'account_name': account_result['account']['account_name'],
            'transactions': formatted_txns,
            'count':        len(formatted_txns)
        }

    except Exception as e:
        return {'success': False, 'error': f'Failed to get transactions: {str(e)}'}


# ============================================================
# TRANSFER OPERATIONS
# ============================================================

def transfer_money(user_id: str, from_account_id: str, to_account_id: str,
                  amount: float, memo: str = '') -> dict:
    """Transfer money between accounts"""
    try:
        db = get_firestore()

        # Validate amount
        if amount <= 0:
            return {'success': False, 'error': 'Amount must be greater than 0'}
        if amount > MAX_TRANSFER_AMOUNT:
            return {'success': False, 'error': f'Maximum transfer amount is ${MAX_TRANSFER_AMOUNT:,.2f}'}

        # Get source account
        from_doc = db.collection(COLLECTION_ACCOUNTS).document(from_account_id).get()
        from_acc = document_to_dict(from_doc)

        if not from_acc:
            return {'success': False, 'error': 'Source account not found'}
        if from_acc['user_id'] != user_id:
            return {'success': False, 'error': 'Unauthorized: source account'}
        if from_acc['status'] != 'ACTIVE':
            return {'success': False, 'error': 'Source account is not active'}
        if from_acc['available_balance'] < amount:
            return {
                'success': False,
                'error': f'Insufficient funds. Available: ${from_acc["available_balance"]:.2f}'
            }

        # Get destination account
        to_doc = db.collection(COLLECTION_ACCOUNTS).document(to_account_id).get()
        to_acc = document_to_dict(to_doc)

        if not to_acc:
            return {'success': False, 'error': 'Destination account not found'}
        if to_acc['status'] != 'ACTIVE':
            return {'success': False, 'error': 'Destination account is not active'}

        # Calculate new balances
        new_from_balance = from_acc['balance'] - amount
        new_to_balance   = to_acc['balance'] + amount

        # Generate reference
        reference = str(uuid.uuid4())[:8].upper()

        # Update source account
        db.collection(COLLECTION_ACCOUNTS).document(from_account_id).update({
            'balance':           new_from_balance,
            'available_balance': new_from_balance,
            'updated_at':        datetime.utcnow().isoformat()
        })

        # Update destination account
        db.collection(COLLECTION_ACCOUNTS).document(to_account_id).update({
            'balance':           new_to_balance,
            'available_balance': new_to_balance,
            'updated_at':        datetime.utcnow().isoformat()
        })

        # Create debit transaction
        create_transaction(
            account_id=from_account_id,
            user_id=user_id,
            transaction_type='DEBIT',
            amount=amount,
            balance_after=new_from_balance,
            description=f'Transfer to {to_acc["account_name"]}',
            memo=memo,
            reference=reference
        )

        # Create credit transaction
        create_transaction(
            account_id=to_account_id,
            user_id=to_acc['user_id'],
            transaction_type='CREDIT',
            amount=amount,
            balance_after=new_to_balance,
            description=f'Transfer from {from_acc["account_name"]}',
            memo=memo,
            reference=reference
        )

        return {
            'success': True,
            'message': '✅ Transfer completed successfully!',
            'transfer': {
                'reference':    reference,
                'amount':       amount,
                'from_account': from_acc['account_name'],
                'to_account':   to_acc['account_name'],
                'new_balance':  new_from_balance,
                'timestamp':    datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        return {'success': False, 'error': f'Transfer failed: {str(e)}'}

def get_account_by_type(user_id: str, account_type: str) -> dict:
    """Get account by user_id and account type (checking/savings)"""
    try:
        db = get_firestore()
        
        # Normalize account type to uppercase
        account_type_upper = account_type.upper()
        
        print(f"🔍 Searching for: user_id={user_id}, type={account_type_upper}")
        
        # Query for account - USE COLLECTION_ACCOUNTS
        accounts_ref = db.collection(COLLECTION_ACCOUNTS)\
                         .where('user_id', '==', user_id)\
                         .where('account_type', '==', account_type_upper)\
                         .where('status', '==', 'ACTIVE')
        
        accounts = list(accounts_ref.stream())
        
        print(f"📊 Found {len(accounts)} accounts")
        
        if not accounts:
            # Debug: show all accounts for user
            all_accounts = db.collection(COLLECTION_ACCOUNTS)\
                             .where('user_id', '==', user_id)\
                             .stream()
            
            all_list = list(all_accounts)
            print(f"📊 Total accounts for user: {len(all_list)}")
            for acc in all_list:
                acc_data = acc.to_dict()
                print(f"   - Type: {acc_data.get('account_type')}, Status: {acc_data.get('status')}")
            
            return {'success': False, 'error': f'No {account_type} account found'}
        
        account_doc = accounts[0]
        account = account_doc.to_dict()
        account['account_id'] = account_doc.id
        
        print(f"✅ Found account: {account.get('account_name')}")
        
        return {'success': True, 'account': account}
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {'success': False, 'error': f'Failed to find account: {str(e)}'}
    
def get_account_owner_name(account_id: str) -> str:
    """Get the name of the account owner"""
    try:
        db = get_firestore()
        
        # Get account - USE COLLECTION_ACCOUNTS
        account_doc = db.collection(COLLECTION_ACCOUNTS).document(account_id).get()
        if not account_doc.exists:
            return "Unknown"
        
        account = account_doc.to_dict()
        user_id = account.get('user_id')
        
        # Get user - USE COLLECTION_USERS
        user_doc = db.collection(COLLECTION_USERS).document(user_id).get()
        if not user_doc.exists:
            return "Unknown"
        
        user = user_doc.to_dict()
        return f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        
    except Exception as e:
        return "Unknown"

# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Firestore operations...\n")

    # Create test user first in auth
    from firebase.auth import register_user, login_user

    print("0️⃣  Creating test user...")
    reg = register_user("firestore_test@test.com", "TestPass123!", "Fire", "Store")
    if reg['success']:
        user_id = reg['user_id']
        print(f"   ✅ User created: {user_id}\n")

        # Test create account
        print("1️⃣  Testing create_account...")
        acc1 = create_account(user_id, 'checking', 500.00)
        print(f"   Result: {acc1}\n")

        if acc1['success']:
            acc1_id = acc1['account']['account_id']

            # Create second account
            acc2 = create_account(user_id, 'savings', 1000.00, 'My Savings')
            acc2_id = acc2['account']['account_id']

            # Test get_accounts
            print("2️⃣  Testing get_accounts...")
            all_accs = get_accounts(user_id)
            print(f"   Result: {all_accs}\n")

            # Test get_balance
            print("3️⃣  Testing get_balance...")
            balance = get_balance(acc1_id, user_id)
            print(f"   Result: {balance}\n")

            # Test transfer
            print("4️⃣  Testing transfer_money...")
            transfer = transfer_money(user_id, acc1_id, acc2_id, 100.00, 'Test transfer')
            print(f"   Result: {transfer}\n")

            # Test get_transactions
            print("5️⃣  Testing get_transactions...")
            txns = get_transactions(acc1_id, user_id)
            print(f"   Result: {txns}\n")

    print("✅ Firestore tests complete!")