# 🧠🎮 Psycho Tilt LoL - Predictive Mental Analytics

An intelligent system for psychological analysis, tilt prevention, and real-time emotional stability prediction for League of Legends players, powered by data analytics and Machine Learning.

## 🚀 The Problem & The Solution
In competitive esports, performance depends heavily not only on mechanical skill but also on macro-emotional control. "Tilt" (accumulated frustration) severely impairs decision-making and performance, frequently leading to consecutive loss streaks.

**Psycho Tilt LoL** solves this by automating raw game telemetry collection directly from the official **Riot Games API**, allowing users to log their subjective emotional states, and processing this data through a Machine Learning pipeline that predicts the risk of psychological collapse *before* entering the matchmaking queue (*pre-match predictor*).

## 🏗️ System Architecture (Separation of Concerns)
The project is built following strict modular design principles to isolate infrastructure from business logic and the user interface:

- **Presentation Layer (UI):** Built using `dashboard.py` (Streamlit for interactive web analytics) and `app.py` (A modular CLI alternative for console-based operations).
- **Service Layer (`core/sync_service.py` & `core/riot_api.py`):** Gateways handling asynchronous HTTP communication, Rate Limiting controls, and payload normalization for JSON data fetched from Riot servers.
- **Persistence Layer (`core/database.py`):** Centralized SQL relational transactions managed via SQLite, ensuring history idempotency using unique game identifiers (`match_id`).
- **Analytical & Predictive Layer (`core/analytics.py` & `core/ml_predictor.py`):** Core engines processing feature engineering (time-series shifts, One-Hot Encoding) and on-the-fly training of a supervised classification model (**Random Forest**).

## 📊 Core Features Implemented
1. **Pre-Match Risk Predictor (AI):** Evaluates environmental and performance variables (biological fatigue timeframes, previous loss streaks, and specific high-stress champion selections) to statistically estimate the probability of frustration.
2. **Post-Loss Resilience Index (Tilt-Back):** Time-series analysis utilizing index shifts (`.shift()`) to calculate the real variance in tilt metrics immediately following a defeat.
3. **Competitive Fatigue Curve:** Chronological cumulative aggregations that identify cognitive wear thresholds based on consecutive games played during a single day.
4. **Three-Tier Emotional Matrix:** A dynamic classification layout (Comfort Zone, high-drain Trap Champions, and high-risk Bait/Danger Zone).

## 🛠️ Installation and Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/psycho_tilteo_lol.git](https://github.com/YOUR_USERNAME/psycho_tilteo_lol.git)
   cd psycho_tilteo_lol
2. Install official dependencies:

pip install -r requirements.txt

3. Configure secure environment variables (Cybersecurity Best Practices):
Create a .env file in the root directory:

RIOT_API_KEY=RGAPI-your-official-key-here
REGION=your-region-here

4. Launch the web analytics platform:

streamlit run dashboard.py

🛡️ Cyber Security & Data Privacy
This project strictly enforces the decoupling of sensitive credentials from the source code. Private access tokens (RGAPI) are injected directly into the operating system memory at runtime via a local protected .env file. This file is explicitly excluded from version control within .gitignore to prevent credential leaks in public code repositories.