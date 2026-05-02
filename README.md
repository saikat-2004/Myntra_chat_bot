# 💄 Myntra Lipstick Care Chatbot

<div align="center">

![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-green?style=for-the-badge&logo=postgresql)

</div>

---

## 📖 About

The **Myntra Lipstick Care Chatbot** is an intelligent, conversational assistant built to help users discover and learn about lipstick products from Myntra. It provides personalized lipstick care suggestions, product recommendations, and beauty tips — all in real time. Every conversation is stored securely in a **Neon PostgreSQL** cloud database, making interactions persistent and traceable.

---

## ✨ Features

- 💬 **Conversational AI Chatbot** — Engage in natural, helpful conversations about lipstick care and recommendations.
- 🛍️ **Myntra Product Data** — Real-time lipstick data scraped directly from Myntra for up-to-date suggestions.
- 💾 **Conversation History Storage** — All chat sessions are stored in a Neon-hosted PostgreSQL database.
- 🌐 **Web Interface** — Clean, responsive UI built with HTML and CSS for a smooth user experience.
- ⚡ **Real-Time Data** — Always working with the latest scraped product information.
- 🗄️ **Neon PostgreSQL Integration** — Cloud-native PostgreSQL via Neon console for reliable data persistence.

---

## 🛠️ Tech Stack

| Layer       | Technology                     |
|-------------|-------------------------------|
| Language    | Python 3.8+                   |
| Backend     | Flask                         |
| Frontend    | HTML, CSS                     |
| Database    | PostgreSQL (Neon Cloud)       |
| Scraping    | Python Scraper (custom)       |

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed before proceeding:

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- A [Neon](https://neon.tech/) account with a PostgreSQL database set up
- pip (comes with Python)

---

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/SaikatSamanta/myntra-chatbot.git
cd myntra-chatbot
```

**2. Set up a virtual environment**

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the root directory and add your Neon PostgreSQL credentials:

```env
DATABASE_URL=your_neon_postgresql_connection_string
SECRET_KEY=your_secret_key
```

**5. Scrape Myntra lipstick data**

Run the scraper to populate your database with product data:

```bash
python -c "from app.scraper import scrape_myntra_lipsticks; scrape_myntra_lipsticks(max_pages=2)"
```

**6. Run the application**

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000
