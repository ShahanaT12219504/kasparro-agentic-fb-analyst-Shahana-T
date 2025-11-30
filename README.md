# 📌 **Kasparro – Agentic FB Analyst Assignment**  

## 🚀 **Overview**
This repository contains my submission for the **Kasparro Applied AI Engineer – Agentic FB Analyst Assignment**.

I built a **modular, agentic AI pipeline** that analyzes Facebook Ads performance and generates:

- Structured performance insights  
- Hypotheses on performance issues  
- Evaluated insights  
- Creative recommendations  

The system uses a clean, production-style multi-agent architecture with full modularity, traceability, and config-driven behavior.

---

## 🧠 **Architecture Overview**
The system consists of five main agents:

### 🔹 **Planner Agent**
- Reads user query  
- Generates step-by-step execution plan  
- Includes offline-safe fallback  

### 🔹 **Data Agent**
- Loads FB Ads dataset  
- Summarizes metrics (CTR, ROAS, Spend, Revenue)  
- Supports last-n-days filtering  

### 🔹 **Insight Agent**
- Generates hypotheses about performance issues  
- Produces structured, actionable insights  
- Works with LLMs or offline fallback  

### 🔹 **Evaluator Agent**
- Validates insights  
- Adds confidence & reasoning  
- Ensures useful final output  

### 🔹 **Creative Generator Agent**
- Suggests creative improvements  
- Helps enhance low-performing ads  
- Model-based & fallback compatible  

---

## ⚙️ **Pipeline Flow**
```
Planner 
  → Data Agent
      → Insight Agent 
          → Evaluator 
              → Creative Generator
```

Final outputs are saved in:

```
/reports/insights.json  
/reports/creatives.json  
/reports/report.md
```

---

## 📂 **Project Structure**
```
kasparro-agentic-fb-analyst-Shahana-T/
│
├── config/
│   └── config.yaml
│
├── src/
│   ├── agents/
│   │   ├── planner.py
│   │   ├── data_agent.py
│   │   ├── insight_agent.py
│   │   ├── evaluator.py
│   │   └── creative_generator.py
│   │
│   ├── orchestrator/
│   │   └── runner.py
│   │
│   ├── utils/
│       ├── data_loader.py
│       ├── logging_utils.py
│       └── prompts_loader.py
│
├── prompts/
│   ├── planner.md
│   ├── insight_agent.md
│   ├── evaluator.md
│   └── creative_generator.md
│
├── reports/
│   ├── insights.json
│   ├── creatives.json
│   └── report.md
│
├── run.py
└── README.md
```

---

## 📊 **Generated Outputs**

### ✔ **insights.json**
Structured validated insights with reasoning + confidence.

### ✔ **creatives.json**
Creative recommendations for improving ad performance.

### ✔ **report.md**
A combined human-readable summary.

---

## 🧪 **How to Run Locally**

### **1. Install dependencies**
```
pip install -r requirements.txt
```

(or manually install pandas, numpy, pyyaml, etc.)

### **2. Run the pipeline**
```
python run.py
```

### **3. Check outputs**
```
/reports/
```
These files are auto-generated:

- `/reports/insights.json`  
- `/reports/creatives.json`  
- `/reports/report.md`

---

## 🛠️ **Tech Stack**
- Python 3.10  
- Modular agent architecture  
- Config-driven pipeline  
- Offline-safe LLM client  
- JSON & Markdown reporting  
- Logging utilities  

---

