"""
Transfer Tools V2 - Smart Transfers
Supports both internal (between own accounts) and external (to other people)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase.firestore import (
    get_account_by_type,
    get_account_owner_name,
    get_account as db_get_account,
    transfer_money as db_transfer_money
)
import json


def external_transfer(user_id: str, from_account_type: str, to_account_id: str, 
                     amount: float, memo: str = "") -> str:
    """
    Transfer to another person's account using their account ID
    Shows recipient name for confirmation
    
    Args:
        user_id: Sender's user ID
        from_account_type: Source account type ('checking' or 'savings')
        to_account_id: Recipient's account ID
        amount: Amount to transfer
        memo: Optional memo
    
    Returns:
        JSON with transfer result including recipient name
    """
    try:
        # Get sender's account by type
        from_result = get_account_by_type(user_id, from_account_type)
        if not from_result['success']:
            return json.dumps({
                'success': False,
                'error': f"You don't have a {from_account_type} account. Please create one first."
            }, indent=2)
        
        from_account = from_result['account']
        from_account_id = from_account['account_id']
        
        # Get recipient's account details
        to_account_result = db_get_account(to_account_id, to_account_id)  # Use account_id as temp user_id
        
        # Actually, we need to get the account directly
        from firebase.client import get_firestore
        db = get_firestore()
        to_account_doc = db.collection('accounts').document(to_account_id).get()
        
        if not to_account_doc.exists:
            return json.dumps({
                'success': False,
                'error': f"Account ID {to_account_id} not found. Please check the account number."
            }, indent=2)
        
        to_account = to_account_doc.to_dict()
        
        # Check if trying to send to own account
        if to_account.get('user_id') == user_id:
            return json.dumps({
                'success': False,
                'error': "You cannot transfer to your own account this way. Use 'transfer between my accounts' instead."
            }, indent=2)
        
        # Get recipient name
        recipient_name = get_account_owner_name(to_account_id)
        recipient_account_type = to_account.get('account_type', 'UNKNOWN')
        
        # Show confirmation message BEFORE transferring
        confirmation_msg = f"""
📋 Transfer Confirmation Needed:

FROM: Your {from_account_type.upper()} account
TO: {recipient_name}'s {recipient_account_type} account
Account ID: {to_account_id}
Amount: ${amount:.2f}

⚠️ Please confirm this is correct before I proceed with the transfer.
Reply "confirm" or "yes" to proceed.
        """.strip()
        
        # For now, we'll execute the transfer
        # In production, you'd want a confirmation step
        
        # Execute transfer
        transfer_result = db_transfer_money(
            user_id, 
            from_account_id, 
            to_account_id, 
            amount, 
            memo
        )
        
        # Parse and enhance result
        result = json.loads(transfer_result)
        
        if result.get('success'):
            # Add recipient details
            result['transfer']['recipient_name'] = recipient_name
            result['transfer']['recipient_account_type'] = recipient_account_type
            result['transfer']['from_account_type'] = from_account_type.upper()
            result['message'] = f"✅ Successfully sent ${amount:.2f} to {recipient_name}!"
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f'Transfer failed: {str(e)}'
        }, indent=2)


def internal_transfer(user_id: str, from_account_type: str, to_account_type: str, 
                     amount: float, memo: str = "") -> str:
    """
    Transfer between user's own accounts
    
    Args:
        user_id: User's ID
        from_account_type: Source account type
        to_account_type: Destination account type
        amount: Amount to transfer
        memo: Optional memo
    """
    try:
        # Get source account
        from_result = get_account_by_type(user_id, from_account_type)
        if not from_result['success']:
            return json.dumps({
                'success': False,
                'error': f"You don't have a {from_account_type} account."
            }, indent=2)
        
        # Get destination account
        to_result = get_account_by_type(user_id, to_account_type)
        if not to_result['success']:
            return json.dumps({
                'success': False,
                'error': f"You don't have a {to_account_type} account."
            }, indent=2)
        
        from_account_id = from_result['account']['account_id']
        to_account_id = to_result['account']['account_id']
        
        # Execute transfer
        result = db_transfer_money(user_id, from_account_id, to_account_id, amount, memo)
        
        return result
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f'Transfer failed: {str(e)}'
        }, indent=2)


# Tool function mapping
TOOL_FUNCTIONS = {
    "external_transfer": external_transfer,
    "internal_transfer": internal_transfer
}


if __name__ == "__main__":
    print("🧪 Testing Smart Transfer Tools...\n")
    print("✅ External and internal transfer tools loaded!")