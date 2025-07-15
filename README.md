# 🌙 LunaJoy - Mental Health Matching Platform

LunaJoy connects patients with the perfect mental health professionals using AI-powered matching technology.

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- Python (v3.11 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/lunajoy.git
cd lunajoy
```

2. **Start the Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

3. **Start the Frontend**
```bash
cd frontend
npm install
npm start
```

The application will open at `http://localhost:3000`

## 🎯 How to Use LunaJoy

### For Patients

1. **Start Your Search**
   - Click "Start Your Journey" on the homepage
   - Or navigate directly to the search form

2. **Enter Your Preferences**
   - **Location**: Select your state
   - **Appointment Type**: Choose between therapy or medication management
   - **Insurance**: Select your insurance provider
   - **Preferences** (optional): Language, therapist gender, clinical needs
   - **Availability** (optional): Urgency level and preferred time slots

3. **Review Your Matches**
   - Get up to 9 personalized matches
   - See match scores and explanations
   - View detailed profiles by clicking "View Profile"

4. **Connect with Professionals**
   - **Sign In** for full features (save favorites, contact directly)
   - **Book Appointment**: Schedule directly with the professional
   - **Send Message**: Contact them through the platform

### User Types & Benefits

- **🌱 Anonymous Users**: Quick matches without registration
- **🌿 Basic Users**: Enhanced matching with demographic data
- **🌳 Premium Users**: AI-powered predictions based on your history

## 🔧 Key Features

- **Lightning Fast**: Results in under 60 seconds
- **Smart Matching**: 3-tier progressive matching system
- **HIPAA Compliant**: Your data is secure and private
- **Real-time Availability**: See who's available now
- **Multi-criteria Scoring**: Matches based on 10+ factors

## 📱 Navigation

- **Home**: Search form and main landing
- **How It Works**: Detailed explanation of the matching process
- **Results**: Your personalized matches
- **Profile Modal**: Detailed view of each professional

## 🧪 Test Users

For testing the different matching strategies:

```
Anonymous: Just search without logging in
Basic User: test_user_basic
Premium User: user_01307_c530ad
```

## 💡 Tips for Best Results

1. **Be Specific**: The more details you provide, the better your matches
2. **Consider Availability**: If you need help urgently, select "Immediate"
3. **Try Different Options**: Adjust your preferences if you want more choices
4. **Save Favorites**: Sign in to save professionals for later

## 🛟 Troubleshooting

**Backend Connection Error?**
- Ensure the backend is running on `http://127.0.0.1:8000`
- Check the terminal for any Python errors

**No Matches Found?**
- Try broadening your search criteria
- Check if professionals are available in your state

**Login Issues?**
- Use one of the test user IDs provided
- No password required for demo

## 📊 Understanding Match Scores

- **90-100%**: Excellent match - highly recommended
- **70-89%**: Good match - strong compatibility
- **50-69%**: Fair match - some alignment
- **Below 50%**: Limited compatibility

## 🔒 Privacy & Security

- No data is stored in browser storage
- All communications are encrypted
- HIPAA compliant architecture
- Your search history is private

---


**Made with 💚 for your mental health**