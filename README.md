# ✈️ TripSync AI

### AI-Powered Multi-Agent Travel Planner with Budget Optimization

TripSync AI is an AI-powered travel planning application that helps users plan trips based on their destination, travel dates, number of travelers, and budget.

It uses specialized agents to generate travel recommendations and estimate expenses. If the estimated trip cost exceeds the user's budget, the planner explores alternatives to help bring the cost within budget.

## 🚀 Features

* ✈️ **Transport Recommendations** — Suggests suitable transportation options.
* 🏨 **Accommodation Planning** — Recommends accommodation options.
* 🍽️ **Food Planning** — Provides food recommendations.
* 🎯 **Activity Planning** — Suggests activities based on the trip.
* 💰 **Budget Estimation** — Displays estimated travel expenses and a budget breakdown.
* 🤖 **Multi-Agent Architecture** — Uses specialized agents for different travel-planning tasks.
* 🔄 **Budget-Aware Replanning** — Explores alternatives when the estimated cost exceeds the available budget.
* 📊 **Interactive Dashboard** — Displays trip information and estimated expenses visually.
* 📄 **PDF Export** — Allows users to export their trip plan.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI
* **Frontend:** HTML, CSS, JavaScript
* **AI Integration:** Google Gemini API
* **Visualization:** Chart.js
* **PDF Export:** jsPDF

## ⚙️ How It Works

1. Enter your starting city and destination.
2. Select your travel dates and number of travelers.
3. Set your total travel budget.
4. The specialized agents generate travel recommendations and estimated costs.
5. The planner checks whether the estimated expenses fit the budget.
6. If necessary, it explores alternatives and recalculates the estimate.
7. Review the final trip plan and budget breakdown on the dashboard.

## 📂 Project Structure

```text
TripSync-AI/
├── app.py
├── planner.py
├── index.html
├── styles.css
├── app.js
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*Update this structure to match the actual files in your repository.*

## 💻 Getting Started

### Prerequisites

* Python installed
* Git installed
* A Google Gemini API key if you want to use AI-powered recommendations

### 1. Clone the repository

```bash
git clone https://github.com/chiragsoni01/TripSync-AI.git
cd TripSync-AI
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file and add your Gemini API key using the variable name expected by your application.

**Never commit your `.env` file or publish your API key.**

### 5. Run the application

Start the FastAPI backend using the command appropriate for your project. For example, if your FastAPI instance is named `app` inside `app.py`:

```bash
uvicorn app:app --reload
```

If your backend uses a different filename or application variable, adjust the command accordingly.

Then open the frontend using a local web server and follow the application's configured API address.

## ⚠️ Important Note

TripSync AI is a student learning project. Travel costs and recommendations are estimates and may not reflect live prices or actual availability. The application does not guarantee bookings.

## 🔮 Future Improvements

* Deploy the application online.
* Integrate live flight and hotel data from suitable APIs.
* Improve travel recommendations and budget optimization.
* Add user accounts and saved itineraries.
* Expand testing and error handling.

## 👨‍💻 Author

**Chirag Soni**
B.Tech Computer Science Engineering — Artificial Intelligence & Machine Learning

GitHub: [chiragsoni01](https://github.com/chiragsoni01)

---

⭐ If you find this project interesting, feel free to explore the repository!
