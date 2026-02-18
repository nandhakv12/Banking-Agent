# 🏦 SecureBank AI Banking Assistant

An AI-powered banking chatbot built with **Claude API**, **Firebase**, and **Streamlit**.

## 🌟 Features

- ✅ **User Authentication** - Firebase Auth with email/password
- ✅ **Account Management** - Create checking and savings accounts
- ✅ **Balance Inquiry** - Check balances across all accounts
- ✅ **Money Transfers** - Internal (between own accounts) and external (to friends)
- ✅ **Transaction History** - View recent transactions
- ✅ **Multi-Agent System** - Specialized AI agents for different banking tasks
- ✅ **Smart Transfer** - Auto-detects recipient names for confirmation

## 🛠️ Tech Stack

- **AI**: Anthropic Claude API (Sonnet 4.5)
- **Backend**: Python, FastAPI concepts
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth
- **Frontend**: Streamlit
- **Architecture**: Multi-agent system with supervisor

## 📁 Project Structure
```
banking-chatbot/
├── streamlit_app.py          # Main web interface
├── config.py                 # Configuration
├── firebase/
│   ├── client.py            # Firebase connection
│   ├── auth.py              # Authentication
│   └── firestore.py         # Database operations
├── agents/
│   ├── account_agent.py     # Account management
│   ├── balance_agent.py     # Balance inquiries
│   ├── transfer_agent.py    # Money transfers
│   └── transaction_agent.py # Transaction history
├── graph/
│   └── supervisor.py        # Routes requests to agents
└── tools/
    ├── account_tools.py     # Account operations
    ├── balance_tools.py     # Balance checks
    ├── transfer_tools_v2.py # Smart transfers
    └── transaction_tools.py # Transaction queries
```

## 🚀 Setup

### Prerequisites

- Python 3.10+
- Firebase account
- Anthropic API key

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/banking-chatbot.git
   cd banking-chatbot
```

2. **Create virtual environment**
```bash
   python -m venv bankenv
   bankenv\Scripts\activate  # Windows
   # or
   source bankenv/bin/activate  # Mac/Linux
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Setup Firebase**
   - Create a Firebase project at https://console.firebase.google.com
   - Enable Authentication (Email/Password)
   - Enable Firestore Database
   - Download service account key → `firebase/serviceAccountKey.json`
   - Get Firebase API key from Project Settings

5. **Setup environment variables**
   
   Create `.env` file:
```env
   # Anthropic API
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
   
   # Firebase
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_SERVICE_ACCOUNT=D:\path\to\serviceAccountKey.json
   FIREBASE_API_KEY=AIzaSyXXXXXXXXXXX
```

6. **Run the app**
```bash
   streamlit run streamlit_app.py
```

## 📖 Usage

1. **Register** - Create a new account
2. **Login** - Sign in with your credentials
3. **Create Accounts** - Open checking or savings accounts
4. **Transfer Money** - Move money between accounts or send to friends
5. **Check Balance** - View all your account balances
6. **View Transactions** - See your recent activity

## 🤖 AI Agents

The system uses a **multi-agent architecture**:

- **Supervisor Agent** - Routes requests to specialized agents
- **Account Agent** - Handles account creation and management
- **Balance Agent** - Processes balance inquiries
- **Transfer Agent** - Manages money transfers (internal & external)
- **Transaction Agent** - Retrieves transaction history

## 🔐 Security

- ✅ Firebase Authentication
- ✅ Session management
- ✅ User ID verification on all operations
- ✅ Transfer confirmation with recipient name display
- ✅ Maximum transfer limits ($10,000)
- ✅ Secure credential management

## 💡 Key Features

### Smart Transfers
- **Internal**: "Transfer $50 from checking to savings"
- **External**: "Send $100 to account abc-123"
  - Auto-detects recipient name
  - Shows confirmation before sending

### Auto Balance Display
- No account ID needed
- Shows all accounts automatically
- Displays total balance

### Simple UX
- Natural language processing
- Minimal user verification
- Fast and intuitive

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📧 Contact

Your Name - nandhakv12@gmail.com

## 🙏 Acknowledgments

- Anthropic Claude API
- Firebase
- Streamlit