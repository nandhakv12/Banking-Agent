"""
Firebase Authentication
Handles user registration and login
"""

import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase.client import get_firestore, get_auth, document_to_dict
from config import (
    COLLECTION_USERS,
    COLLECTION_SESSIONS,
    SESSION_EXPIRY_HOURS,
    MIN_PASSWORD_LENGTH
)


# ============================================================
# REGISTER
# ============================================================

def register_user(email: str, password: str, first_name: str, last_name: str) -> dict:
    """Register a new user with Firebase Auth + Firestore"""
    try:
        db   = get_firestore()
        auth = get_auth()

        # Validate inputs
        if not email or not first_name or not last_name:
            return {'success': False, 'error': 'All fields are required'}

        if len(password) < MIN_PASSWORD_LENGTH:
            return {'success': False, 'error': f'Password must be at least {MIN_PASSWORD_LENGTH} characters'}

        # Create Firebase Auth user
        firebase_user = auth.create_user(
            email=email.lower().strip(),
            password=password,
            display_name=f"{first_name} {last_name}"
        )

        # Save profile in Firestore
        user_data = {
            'user_id':        firebase_user.uid,
            'email':          email.lower().strip(),
            'first_name':     first_name.strip(),
            'last_name':      last_name.strip(),
            'status':         'ACTIVE',
            'email_verified': False,
            'created_at':     datetime.utcnow().isoformat(),
            'updated_at':     datetime.utcnow().isoformat(),
            'last_login':     None
        }

        db.collection(COLLECTION_USERS)\
          .document(firebase_user.uid)\
          .set(user_data)

        return {
            'success':    True,
            'message':    f'Welcome {first_name}! Account created successfully!',
            'user_id':    firebase_user.uid,
            'email':      email.lower().strip(),
            'first_name': first_name,
            'last_name':  last_name
        }

    except Exception as e:
        error = str(e)
        if 'EMAIL_EXISTS' in error or 'email-already-exists' in error:
            return {'success': False, 'error': 'Email already registered'}
        if 'INVALID_EMAIL' in error or 'invalid-email' in error:
            return {'success': False, 'error': 'Invalid email format'}
        if 'WEAK_PASSWORD' in error or 'weak-password' in error:
            return {'success': False, 'error': 'Password is too weak'}
        return {'success': False, 'error': f'Registration failed: {error}'}


# ============================================================
# LOGIN
# ============================================================

def login_user(email: str, password: str) -> dict:
    """Login user using Firebase Auth REST API"""
    try:
        import requests
        from config import FIREBASE_PROJECT_ID
        import json

        # Use Firebase Auth REST API to verify password
        api_key = get_firebase_api_key()
        if not api_key:
            return {'success': False, 'error': 'Firebase API key not configured'}

        # Call Firebase Auth REST API
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        response = requests.post(url, json={
            'email':             email.lower().strip(),
            'password':          password,
            'returnSecureToken': True
        })

        data = response.json()

        if 'error' in data:
            error_msg = data['error']['message']
            if 'INVALID_PASSWORD' in error_msg or 'INVALID_LOGIN_CREDENTIALS' in error_msg:
                return {'success': False, 'error': 'Incorrect email or password'}
            if 'EMAIL_NOT_FOUND' in error_msg:
                return {'success': False, 'error': 'No account found with this email'}
            if 'USER_DISABLED' in error_msg:
                return {'success': False, 'error': 'Account has been disabled'}
            return {'success': False, 'error': error_msg}

        uid = data['localId']

        # Get user profile from Firestore
        db       = get_firestore()
        user_doc = db.collection(COLLECTION_USERS).document(uid).get()
        user     = document_to_dict(user_doc)

        if not user:
            return {'success': False, 'error': 'User profile not found'}

        # Create session
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)

        db.collection(COLLECTION_SESSIONS).document(session_id).set({
            'session_id': session_id,
            'user_id':    uid,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat(),
            'active':     True
        })

        # Update last login
        db.collection(COLLECTION_USERS).document(uid).update({
            'last_login': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })

        return {
            'success':    True,
            'message':    f'Welcome back, {user["first_name"]}!',
            'user_id':    uid,
            'first_name': user['first_name'],
            'last_name':  user['last_name'],
            'email':      user['email'],
            'session_id': session_id
        }

    except Exception as e:
        return {'success': False, 'error': f'Login failed: {str(e)}'}


# ============================================================
# GET USER
# ============================================================

def get_user(user_id: str) -> dict:
    """Get user profile from Firestore"""
    try:
        db       = get_firestore()
        user_doc = db.collection(COLLECTION_USERS).document(user_id).get()
        user     = document_to_dict(user_doc)

        if not user:
            return {'success': False, 'error': 'User not found'}

        return {'success': True, 'user': user}

    except Exception as e:
        return {'success': False, 'error': f'Failed to get user: {str(e)}'}


def validate_session(session_id: str) -> dict:
    """Validate if session is still active"""
    try:
        db          = get_firestore()
        session_doc = db.collection(COLLECTION_SESSIONS).document(session_id).get()
        session     = document_to_dict(session_doc)

        if not session:
            return {'valid': False, 'error': 'Session not found'}

        # Check expiry
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.utcnow() > expires_at:
            return {'valid': False, 'error': 'Session expired'}

        if not session.get('active'):
            return {'valid': False, 'error': 'Session inactive'}

        return {
            'valid':   True,
            'user_id': session['user_id']
        }

    except Exception as e:
        return {'valid': False, 'error': str(e)}


def logout_user(session_id: str) -> dict:
    """Logout user by deactivating session"""
    try:
        db = get_firestore()
        db.collection(COLLECTION_SESSIONS).document(session_id).update({
            'active': False
        })
        return {'success': True, 'message': 'Logged out successfully'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ============================================================
# HELPER
# ============================================================

def get_firebase_api_key() -> str:
    """Get Firebase Web API key from env"""
    return os.environ.get('FIREBASE_API_KEY', '')


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Firebase Auth...\n")

    # Test registration
    print("1️⃣  Testing registration...")
    result = register_user(
        email="testuser1@securebank.com",
        password="TestPassword123!",
        first_name="Test",
        last_name="User"
    )
    print(f"   Result: {result}\n")

    if result['success']:
        # Test login
        print("2️⃣  Testing login...")
        login_result = login_user(
            email="testuser@securebank.com",
            password="TestPassword123!"
        )
        print(f"   Result: {login_result}\n")

        if login_result['success']:
            # Test session validation
            print("3️⃣  Testing session validation...")
            session_result = validate_session(login_result['session_id'])
            print(f"   Result: {session_result}\n")

            # Test logout
            print("4️⃣  Testing logout...")
            logout_result = logout_user(login_result['session_id'])
            print(f"   Result: {logout_result}\n")

    print("✅ Auth tests complete!")