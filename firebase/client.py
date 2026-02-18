"""
Firebase Client
Single Firebase connection used by entire app
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIREBASE_SERVICE_ACCOUNT, FIREBASE_PROJECT_ID


# ============================================================
# INITIALIZE FIREBASE (only once)
# ============================================================

_firebase_app = None
_firestore_client = None


def initialize_firebase():
    """Initialize Firebase connection (called once at startup)"""
    global _firebase_app, _firestore_client

    if _firebase_app is not None:
        return _firestore_client

    try:
        # Try Streamlit secrets FIRST
        try:
            import streamlit as st
            
            # Check if we have Firebase secrets
            if 'FIREBASE_SERVICE_ACCOUNT' in st.secrets:
                print("📂 Loading Firebase from Streamlit secrets")
                
                # Convert Streamlit secrets to dict
                firebase_creds = dict(st.secrets['FIREBASE_SERVICE_ACCOUNT'])
                cred = credentials.Certificate(firebase_creds)
                
                print("✅ Firebase credentials loaded from Streamlit secrets")
            else:
                raise KeyError("FIREBASE_SERVICE_ACCOUNT not in secrets")
                
        except (ImportError, KeyError) as e:
            # Streamlit not available or no secrets - use local file
            print(f"📂 Streamlit secrets not available ({e}), using local file")
            
            if not FIREBASE_SERVICE_ACCOUNT or FIREBASE_SERVICE_ACCOUNT == "None" or FIREBASE_SERVICE_ACCOUNT is None:
                raise ValueError(
                    "FIREBASE_SERVICE_ACCOUNT not configured in .env file. "
                    "Please set the path to your serviceAccountKey.json file."
                )
            
            cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT)
            print(f"✅ Firebase credentials loaded from: {FIREBASE_SERVICE_ACCOUNT}")

        # Initialize Firebase app
        _firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_PROJECT_ID or st.secrets.get('FIREBASE_PROJECT_ID', 'resraech')
        })

        # Initialize Firestore client
        _firestore_client = firestore.client()

        print(f"✅ Firebase connected successfully!")
        return _firestore_client

    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        import traceback
        traceback.print_exc()
        raise

def get_firestore():
    """Get Firestore client (initialize if needed)"""
    global _firestore_client

    if _firestore_client is None:
        initialize_firebase()

    return _firestore_client


def get_auth():
    """Get Firebase Auth client"""
    if _firebase_app is None:
        initialize_firebase()
    return auth


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def document_to_dict(doc) -> dict:
    """Convert Firestore document to dictionary"""
    if not doc.exists:
        return None

    data = doc.to_dict()
    data['id'] = doc.id
    return data


def collection_to_list(query) -> list:
    """Convert Firestore query results to list"""
    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        results.append(data)
    return results


# ============================================================
# TEST CONNECTION
# ============================================================

if __name__ == "__main__":
    print("🔥 Testing Firebase connection...")

    db = initialize_firebase()

    # Test write
    test_ref = db.collection('_test').document('connection')
    test_ref.set({'status': 'connected', 'test': True})
    print("✅ Write test passed!")

    # Test read
    doc = test_ref.get()
    data = document_to_dict(doc)
    print(f"✅ Read test passed: {data}")

    # Cleanup
    test_ref.delete()
    print("✅ Delete test passed!")

    print("\n🎉 Firebase is working perfectly!")