# FeaLens (See Through the Bias) 👁️‍🗨️

**FeaLens** is an enterprise-grade AI fairness auditing platform designed to detect, analyze, and mitigate bias in automated decision-making systems. Built for the Google Solution Challenge, it addresses algorithmic discrimination across **Hiring, Loan Approvals, and Medical Diagnostics**.


## 🌟 The Problem
As AI systems increasingly govern critical life decisions (who gets a job, who gets a loan, who receives medical care), the risk of algorithmic bias scaling exponentially has never been higher. Most organizations lack the tools to transparently audit their datasets and models for unfair treatment of underrepresented or protected groups.

## 🚀 Our Solution
FeaLens provides a seamless, multi-agent automated auditing workflow:
1. **Upload & Explore**: Securely upload CSV datasets and dynamically explore records.
2. **Automated AI Auditing**: A powerful Mistral AI multi-agent backend automatically identifies sensitive attributes (e.g., Gender, Race, Age) and computes robust statistical fairness metrics (Disparate Impact Ratio, Demographic Parity).
3. **Actionable Intelligence**: Generates a human-readable, executive-level bias report with explicit mitigation recommendations.
4. **Natural Language Queries**: Ask the AI direct questions about the dataset's fairness profile.

## ⚙️ Tech Stack
* **Frontend**: React.js, Vite, TailwindCSS (Dark-mode, Glassmorphism UI)
* **Backend**: Python, FastAPI, Pandas
* **AI & Orchestration**: Mistral AI SDK (Multi-Agent Architecture)
* **Storage**: Supabase Integration (Ready)

---

## 💻 Running the Project Locally

### Prerequisites
* Node.js (v18+)
* Python 3.10+
* A [Mistral AI](https://mistral.ai/) API Key

### 1. Backend Setup
```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# (or manual install) pip install fastapi uvicorn pandas mistralai python-dotenv python-multipart

# Configure Environment Variables
# Create a .env file in the backend folder and add:
# MISTRAL_API_KEY="your_mistral_api_key_here"

# Start the server
python main.py
```
*The backend API will run on `http://localhost:8000`*

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The UI will run on `http://localhost:5173` (or 5174).*

---

## 🧠 The Multi-Agent Architecture
Our system utilizes a decentralized agentic approach powered by Mistral AI:
- **Supervisor Agent**: Receives user inputs, detects the domain (Hiring/Loan/Medical), and intelligently routes the task.
- **Worker Agents**: Specialized domain agents retrieve dataset context and compute strict fairness rules.
- **Reporting Engine**: Synthesizes mathematical metrics into actionable, human-readable insights while preventing LLM hallucinations via strict data grounding.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📜 License
Built for the Google Solution Challenge 2026. Open-sourced under the MIT License.
