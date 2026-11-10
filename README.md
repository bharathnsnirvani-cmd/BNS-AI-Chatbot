
# 🤖 BNS AI – Intelligent AI Chatbot

BNS AI is an intelligent conversational chatbot developed using Python, Streamlit, and Google's Gemini AI. It provides an interactive platform where users can ask questions, receive AI-generated responses, and communicate using voice input.

## 🚀 Features

- 🤖 AI-powered conversations using Google Gemini.
- 🧠 Context-aware conversation memory.
- 💬 Multiple chat sessions.
- 🎙️ Voice input and speech transcription.
- 🔊 Text-to-speech response playback.
- 🎨 Professional and responsive user interface.
- ⚡ Real-time AI responses.
- 🗑️ Chat management and history.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application framework |
| Google Gemini API | AI chatbot intelligence |
| Google Gen AI SDK | Gemini API integration |
| HTML & CSS | Interface customization |
| JavaScript | Browser speech functionality |

## 📂 Project Structure

```text
BNS-AI-Chatbot/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
└── .streamlit/
    └── secrets.toml
```

**Note:** `secrets.toml` contains your private API key and must not be uploaded to GitHub.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/bharathnsnirvani-cmd/BNS-AI-Chatbot.git
```

### 2. Open the project folder

```bash
cd BNS-AI-Chatbot
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a folder named `.streamlit`.

Inside it, create `secrets.toml` and add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Get your API key from:

https://aistudio.google.com/app/apikey

Never share or upload your API key.

### 5. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## 🧠 AI Model

This project currently uses:

**Gemini 3.1 Flash-Lite**

## 🔮 Future Enhancements

- Permanent conversation storage.
- User authentication.
- Multilingual voice conversations.
- File upload and document analysis.
- Image understanding.
- Public cloud deployment.

## 👨‍💻 Developer

**Bharath N S**

GitHub: https://github.com/bharathnsnirvani-cmd

Project: BNS AI – Intelligent AI Chatbot

## 📜 License

This project is developed for educational and learning purposes.
