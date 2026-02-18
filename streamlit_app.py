"""
SecureBank AI Banking Assistant
Streamlit Web Interface
"""

import streamlit as st
import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firebase.auth import register_user, login_user, get_user
from graph.supervisor import SupervisorAgent
from config import APP_TITLE, APP_ICON

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'supervisor' not in st.session_state:
    st.session_state.supervisor = None


# ============================================================
# AUTHENTICATION PAGES
# ============================================================

def show_login_page():
    """Display login page"""
    st.markdown("# 🏦 SecureBank")
    st.markdown("### AI-Powered Banking Assistant")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        # LOGIN TAB
        with tab1:
            st.markdown("### Welcome Back!")
            
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password")
                
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("Please enter both email and password")
                    else:
                        with st.spinner("Logging in..."):
                            result = login_user(email, password)
                            
                            if result['success']:
                                st.session_state.logged_in = True
                                st.session_state.user_id = result['user_id']
                                st.session_state.user_name = result['first_name']
                                st.session_state.supervisor = SupervisorAgent()
                                st.success(f"Welcome back, {result['first_name']}!")
                                st.rerun()
                            else:
                                st.error(result['error'])
        
        # REGISTER TAB
        with tab2:
            st.markdown("### Create Account")
            
            with st.form("register_form"):
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", 
                                        help="Min 12 characters with uppercase, lowercase, number, and special character")
                
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if not all([first_name, last_name, email, password]):
                        st.error("Please fill in all fields")
                    else:
                        with st.spinner("Creating account..."):
                            result = register_user(email, password, first_name, last_name)
                            
                            if result['success']:
                                st.success("Account created! Please login.")
                            else:
                                st.error(result['error'])


# ============================================================
# CHAT PAGE
# ============================================================

def show_chat_page():
    """Display main chat interface"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_name}! 👋")
        st.markdown("---")
        
        st.markdown("### 🏦 Quick Actions")
        if st.button("💰 Check Balance", use_container_width=True):
            add_message("What's my balance?", "user")
        
        if st.button("➕ Open Account", use_container_width=True):
            add_message("I want to open a new account", "user")
        
        if st.button("💸 Transfer Money", use_container_width=True):
            add_message("I want to transfer money", "user")
        
        if st.button("📜 Transaction History", use_container_width=True):
            add_message("Show my recent transactions", "user")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.conversation_history = []
            st.session_state.messages = []
            st.session_state.supervisor = None
            st.rerun()
    
    # Main chat area
    st.markdown("# 🏦 SecureBank AI Assistant")
    st.markdown("Ask me anything about your accounts, balances, transfers, and more!")
    st.markdown("---")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        add_message(prompt, "user")


def add_message(content, role):
    """Add message and get AI response"""
    
    # Add user message
    st.session_state.messages.append({"role": role, "content": content})
    
    # Display user message
    with st.chat_message(role):
        st.markdown(content)
    
    # Get AI response
    if role == "user":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Check if credits are available
                    if st.session_state.supervisor is None:
                        st.session_state.supervisor = SupervisorAgent()
                    
                    result = st.session_state.supervisor.chat(
                        content,
                        st.session_state.user_id,
                        st.session_state.conversation_history
                    )
                    
                    response = result['response']
                    st.session_state.conversation_history = result['conversation_history']
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    error_msg = str(e)
                    if 'credit balance is too low' in error_msg:
                        response = "⚠️ **API Credits Needed**\n\nPlease add credits to your Anthropic account:\n1. Go to https://console.anthropic.com/settings/billing\n2. Add $5 or more\n3. Refresh this page\n\nFor now, I can show you:\n• Your account structure\n• How to navigate the app\n• Banking features available"
                    else:
                        response = f"I encountered an error: {error_msg}\n\nPlease try again or contact support."
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})


# ============================================================
# MAIN APP
# ============================================================

def main():
    """Main app entry point"""
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_chat_page()


if __name__ == "__main__":
    main()