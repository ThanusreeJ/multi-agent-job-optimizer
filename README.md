# 🤖 Multi-Agent Production Job Optimizer

AI-powered multi-agent system for optimizing manufacturing production schedules using LangGraph and Groq LLM.

## 🎯 Overview

This project demonstrates a **Proof-of-Concept (POC)** that applies multi-agent AI to solve production scheduling challenges. The system autonomously generates, validates, and optimizes schedules, significantly reducing job tardiness and setup time compared to traditional FIFO methods.

### Key Features

- ✅ **Multi-Agent Architecture**: Specialized agents (Supervisor, Batching, Bottleneck, Constraint) collaborate to optimize schedules
- ✅ **Machine Downtime Management**: Handle scheduled maintenance and simulate unexpected failures
- ✅ **Real-time Re-optimization**: Automatically replans when disruptions occur
- ✅ **Transparent AI Reasoning**: See exactly how and why scheduling decisions are made
- ✅ **Interactive Dashboard**: Streamlit UI with Gantt charts and performance metrics
- ✅ **Baseline Comparison**: Side-by-side comparison with traditional FIFO scheduling

### Performance Improvements

- 🎯 **50%+ reduction** in total job tardiness
- ⚙️ **30%+ reduction** in setup time and product changeovers
- 📊 **20%+ improvement** in machine load balancing

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API Key ([Get one free here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd job-optimizer
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # OR
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**
   ```bash
   copy .env.template .env  # Windows
   # OR
   cp .env.template .env  # Linux/Mac
   ```

   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   GROQ_MODEL_NAME=llama-3.3-70b-versatile
   ```

5. **Run the application**
   ```bash
   streamlit run ui/app.py
   ```

6. **Open browser** at `http://localhost:8501`

---

## 📁 Project Structure

```
job-optimizer/
├── agents/                  # Multi-agent system
│   ├── supervisor.py        # Orchestrates agent workflow
│   ├── batching_agent.py    # Groups jobs to minimize setup time
│   ├── bottleneck_agent.py  # Balances load across machines
│   ├── constraint_agent.py  # Validates schedule compliance
│   └── orchestrator.py      # LangGraph workflow engine
├── models/                  # Data models
│   ├── job.py              # Job definition
│   ├── machine.py          # Machine configuration
│   ├── schedule.py         # Schedule structure
│   └── constraint.py       # Business rules
├── ui/                      # Streamlit dashboard
│   └── app.py              # Main application
├── utils/                   # Utilities
│   ├── baseline_scheduler.py  # FIFO baseline
│   ├── config_loader.py    # Configuration parser
│   └── data_generator.py   # Synthetic data generator
├── requirements.txt         # Python dependencies
├── .env.template           # Environment variable template
└── sample_jobs.csv         # Example job list
```

---

## 🎮 Usage

### 1. Upload Job List

Use the provided `sample_jobs.csv` or create your own:

```csv
job_id,product_type,processing_time,due_time,priority,machine_options
J001,P_A,45,10:00,Rush,M1|M2
J002,P_B,30,11:00,Normal,M2|M3
```

### 2. Configure Machine Downtime (Optional)

- **Manual Entry**: Add individual downtime windows via UI
- **CSV Upload**: Bulk upload maintenance schedules
- **Simulate Failures**: Test real-time re-optimization

### 3. Run Optimization

Choose from multiple strategies:
- **Baseline (FIFO)**: Traditional first-in-first-out
- **Batching Only**: Group similar jobs
- **Balanced Only**: Distribute load evenly
- **Orchestrated**: Full multi-agent optimization

### 4. View Results

- **Gantt Chart**: Visual timeline of job assignments
- **Metrics Table**: Tardiness, setup time, load balance
- **AI Reasoning**: Natural language explanations
- **Compliance Report**: Constraint validation results

---

## 🧪 Testing Scenarios

The system includes 5 standardized test scenarios:

1. **Easy/Baseline**: 5 jobs, 2 machines, no rush orders
2. **Moderate Load**: 15 jobs, 3 machines, 2 rush orders, 1 downtime
3. **Complex Multi-Constraint**: 30 jobs, 5 machines, multiple downtimes
4. **Rush-Heavy**: 20 jobs, 50% rush orders, constrained capacity
5. **Downtime Crisis**: Real-time re-optimization after machine failure

Run tests:
```bash
python test_downtime.py
```

---

## 🛠️ Configuration

### Machine Configuration

Edit machine capabilities and downtimes in the UI or via JSON:

```json
{
  "machines": [
    {
      "machine_id": "M1",
      "compatible_products": ["P_A", "P_B"],
      "downtimes": [
        {"start": "10:00", "end": "11:00", "reason": "Maintenance"}
      ]
    }
  ]
}
```

### Objective Weights

Tune optimization priorities:
- **Tardiness Weight**: Penalty for missed deadlines
- **Setup Weight**: Cost of product changeovers
- **Balance Weight**: Importance of load distribution

See [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for detailed tuning guidance.

---

## 📊 Architecture

### Multi-Agent Workflow

```
User Input → Supervisor Agent
                ├── Batching Agent (minimize setup)
                ├── Bottleneck Agent (balance load)
                └── Constraint Agent (validate rules)
             → Optimized Schedule
```

### Technology Stack

- **LangGraph**: Multi-agent orchestration
- **Groq LLM**: Llama 3.3 70B (high-speed inference)
- **Streamlit**: Interactive web dashboard
- **Plotly**: Gantt chart visualization
- **Pandas**: Data manipulation

---

## 🤝 Contributing

This is a POC project. For production use, consider:
- Integration with ERP/MES systems
- Real-time IoT machine monitoring
- Multi-shift/multi-day scheduling
- Machine learning from historical data
- User authentication and role management

---

## 📄 License

This project is a Proof-of-Concept for internal demonstration purposes.

---

## 🙋 Support

For questions or issues, contact the project team:
- **Lead Developer**: Neetu Singh
- **Project Manager**: Narendra Babu
- **Sponsor**: Ananta Vijay Siddhiraju

---

## 🎓 Learn More

- See [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for detailed system documentation
- See [QUICK_START.md](QUICK_START.md) for step-by-step setup
- Review BRD document for complete business requirements
