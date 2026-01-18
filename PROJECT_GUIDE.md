# Job Optimizer - Complete Project Guide

**A Production Scheduling System with AI-Powered Agents**

This guide explains what every file does and how the system works, in plain English.

---

## What Does This System Do?

Imagine you're running a factory with multiple machines. You have 20 jobs to complete today, each requiring different machines and having different deadlines. Some jobs are urgent ("rush" jobs), machines break down randomly, and switching between product types takes time (setup time).

**This system automatically figures out the best schedule** to complete all jobs while:
- Meeting deadlines (especially rush jobs)
- Avoiding machine breakdowns
- Minimizing wasted time from switching products
- Balancing workload across machines

It uses **4 AI agents** that work together, like a team of scheduling experts, each specializing in a different problem.

---

## Project Structure - What's Where

```
job-optimizer/
├── agents/           ← The AI "brains" of the system
├── models/           ← Data structures (jobs, machines, schedules)
├── ui/               ← The web interface you interact with
├── utils/            ← Helper tools and config files
├── requirements.txt  ← List of Python libraries needed
└── setup.bat         ← One-click Windows setup script
```

---

## The Files Explained

### 📁 **agents/** - The AI Decision Makers

These are the smart components that make scheduling decisions. Each agent is like a specialist consultant.

#### **supervisor.py** - The Manager
- **What it does:** Makes high-level decisions and coordinates the other agents
- **Think of it as:** The project manager who delegates tasks and picks the best solution
- **Uses AI:** Yes (Groq's Llama 3.3 model)
- **Key job:** Analyzes the overall problem and selects the best final schedule

#### **batching_agent.py** - The Efficiency Expert
- **What it does:** Groups similar jobs together to minimize setup time
- **Think of it as:** Like doing all your laundry at once instead of one shirt at a time
- **Uses AI:** Yes (Groq's Llama 3.3 model)
- **Key job:** Arranges jobs by product type (P_A, P_B, P_C) to reduce machine changeover time
- **UI Button:** "🔄 Batching(AI)"

#### **bottleneck_agent.py** - The Load Balancer
- **What it does:** Spreads work evenly across machines
- **Think of it as:** Making sure no one machine is overwhelmed while others sit idle
- **Uses AI:** Yes (Groq's Llama 3.3 model)
- **Key job:** Moves jobs from overloaded machines to underutilized ones
- **UI Button:** "⚖️ Load Balance(AI)"

#### **constraint_agent.py** - The Quality Inspector
- **What it does:** Checks if schedules are legal/possible
- **Think of it as:** The safety inspector who makes sure rules aren't broken
- **Uses AI:** No (uses hard-coded rules for reliability)
- **Key job:** Validates that schedules don't violate shift times, machine downtimes, or deadlines

#### **orchestrator.py** - The Workflow Conductor
- **What it does:** Runs all agents in the right order using a workflow system
- **Think of it as:** The assembly line manager who ensures each step happens in sequence
- **Uses:** LangGraph (a tool for building multi-step AI workflows)
- **UI Button:** "🤖 Orchestrated (Full)"
- **Flow:** Supervisor → Baseline → Batching → Bottleneck → Validation → Select Best

---

### 📁 **models/** - The Data Blueprints

These files define what jobs, machines, and schedules look like in code.

#### **job.py** - Job Definition
- **Contains:** The `Job` class
- **What it stores:** 
  - Job ID (like "J001")
  - Product type (P_A, P_B, or P_C)
  - How long it takes (processing time in minutes)
  - Deadline (due time)
  - Priority (normal or rush)
  - Which machines can handle it
- **Real-world analogy:** A work order ticket

#### **machine.py** - Machine & Rules Definition
- **Contains:** Three classes:
  - `Machine`: Represents a physical machine (ID, capabilities, downtime windows)
  - `DowntimeWindow`: When a machine is unavailable (like maintenance breaks)
  - `Constraint`: The shift rules (work hours, overtime limits, setup times)
- **Real-world analogy:** The machine specs sheet and shift schedule

#### **schedule.py** - The Schedule Blueprint
- **Contains:** Two classes:
  - `Schedule`: The master schedule holding all job assignments
  - `JobAssignment`: One job on one machine with start/end times
- **What it does:** Tracks when each job runs, calculates KPIs (total tardiness, setup time, etc.)
- **Real-world analogy:** The factory calendar on the wall

---

### 📁 **ui/** - The Web Interface

#### **app.py** - The Entire User Interface
- **What it is:** A Streamlit web app (the thing you see in your browser)
- **Lines of code:** 450+ lines
- **Major sections:**

##### **1. Sidebar - System Configuration (Lines 1-120)**
- Set shift hours (default: 8 AM to 4 PM)
- Add overtime allowance
- Define setup times between product types
- Configure how many machines and their capabilities

##### **2. Data Input (Lines 120-200)**
- **Option A:** Upload a CSV file with jobs
- **Option B:** Generate random test jobs (great for demos)
- Shows the job table once loaded

##### **3. Machine Status Panel (Lines 200-250)**
- Displays each machine's capabilities
- Shows current downtime windows (like "Random POC downtime")
- You can add/remove downtimes using buttons

##### **4. Strategy Buttons (Lines 250-345)**
Four big buttons representing different optimization approaches:

- **📊 Baseline FIFO:** 
  - No AI, just first-come-first-served
  - Used as a comparison to show AI improvements
  - Fast but dumb

- **🔄 Batching Strategy:**
  - Runs the Batching Agent
  - Groups jobs by product type
  - Reduces setup time

- **⚖️ Bottleneck Relief:**
  - Runs the Bottleneck Agent on batched results
  - Balances machine workloads
  - Prevents one machine from being slammed

- **🤖 Orchestrated (Full):**
  - Runs ALL agents in sequence
  - Uses the Orchestrator to coordinate
  - Best overall result (usually)

##### **5. Scenario C: Machine Failure (Lines 345-375)**
- Simulates a real-time emergency (machine breaks down)
- Pick which machine fails, when, and for how long
- Click "💥 Trigger Failure & Re-optimize"
- System re-plans everything around the breakdown

##### **6. Dashboard - Results Comparison (Lines 375-450)**
- **Comparison Table:** Shows metrics for each strategy side-by-side
  - Tardiness (how many minutes late overall)
  - Setup Time (time wasted on changeovers)
  - Switches (number of product type changes)
  - Balance Imbalance (how uneven the workload is)

- **Compliance Panel:** Shows violations (missing jobs, late rush jobs)

- **Gantt Chart:** Visual timeline showing when each job runs on each machine
  - Color-coded by product type
  - Hover to see job details

- **Machine Utilization Chart:** Bar chart showing how busy each machine is

---

### 📁 **utils/** - Helper Tools

#### **baseline_scheduler.py** - The Simple Scheduler
- **What it does:** Creates a basic FIFO (first-in-first-out) schedule
- **No AI involved:** Just assigns jobs in order to the first available machine
- **Purpose:** Provides a baseline to compare against AI optimization
- **Used by:** The "📊 Baseline FIFO" button

#### **data_generator.py** - Random Job Creator
- **What it does:** Generates fake jobs for testing
- **Parameters:** Number of jobs, rush probability, product mix
- **Used by:** The "🎲 Generate Random Jobs" button in the UI
- **Why it exists:** So you can test without creating CSV files

#### **config_loader.py** - Configuration Manager
- **What it does:** Loads machine and constraint settings
- **Default setup:**
  - 3 machines (M1, M2, M3)
  - M1 handles P_A and P_B
  - M2 handles P_A and P_C
  - M3 handles P_B and P_C
  - Default shift: 8:00 AM - 4:00 PM
  - 60 minutes max overtime
  - Setup times: 10-15 minutes between product types

---

## Other Important Files

### **requirements.txt** - Python Dependencies
Lists all the libraries needed:
- `streamlit` - Web interface framework
- `langchain-groq` - Connects to Groq's AI models
- `langgraph` - Workflow orchestration
- `pandas` - Data handling
- `plotly` - Interactive charts
- `python-dotenv` - Environment variable management

### **setup.bat** - Quick Setup Script (Windows)
One-click installer that:
1. Creates a Python virtual environment
2. Installs all dependencies
3. Checks for Groq API key
4. Launches the app

### **.env** - API Keys (You Need to Create This!)
```
GROQ_API_KEY=your_key_here
GROQ_MODEL_SUPERVISOR=llama-3.3-70b-versatile
GROQ_MODEL_AGENTS=llama-3.3-70b-versatile
```

### **sample_jobs.csv** - Example Data
A pre-made CSV with 20 sample jobs you can upload to test the system.

---

## How the UI Workflow Actually Works

### When You Click "🤖 Orchestrated (Full)"

Here's what happens step by step:

1. **Loading Phase**
   - Shows spinning status: "🚀 Collaboration in Progress..."
   - System collects all your jobs, machines, and shift settings

2. **Step 1: Supervisor Analysis**
   - Supervisor Agent looks at the problem
   - Identifies rush jobs, calculates total workload
   - Detects potential bottlenecks

3. **Step 2: Baseline Schedule**
   - Creates a simple FIFO schedule (no AI)
   - Used for comparison

4. **Step 3: Batching Agent**
   - Groups jobs by product type
   - Sequences them to minimize setup time
   - Asks AI: "What's the best order to run these jobs?"

5. **Step 4: Bottleneck Agent**
   - Takes the batched schedule
   - Redistributes jobs to balance machine loads
   - Asks AI: "Which machine is overworked? What should we move?"

6. **Step 5: Constraint Validation**
   - Checks EVERY schedule against rules
   - Looks for:
     - Missing jobs
     - Shift overruns
     - Downtime conflicts
     - Late rush jobs
   
7. **Step 6: Selection**
   - If any schedule is 100% valid → picks the best one → ✅ Success!
   - If none are valid → picks the one with fewest violations → ⚠️ Best Effort
   - Shows results in the dashboard

8. **Results Display**
   - Updates the comparison table
   - Shows compliance violations (if any)
   - Draws the Gantt chart timeline
   - Displays explanation from the agents

---

## Understanding the Results

### ✅ **Green Success Badge**
- All jobs assigned
- All deadlines met
- No rule violations
- Schedule is ready to execute

### ⚠️ **Yellow Warning Badge**
- Best effort achieved
- Some jobs couldn't fit
- Or some rush jobs are late
- Schedule is usable but not perfect
- Check the violation list to see what's impossible

### ❌ **Red Error Badge**
- Complete failure (rare)
- Usually means a system error, not a scheduling problem

---

## Key Metrics Explained

When you see the comparison table, here's what each metric means:

### **Tardiness (minutes)**
- Total minutes that jobs are late past their deadline
- **Lower is better**
- 0 = perfect, everything on time

### **Setup Time (minutes)**
- Time wasted switching between product types
- Example: P_A → P_B takes 10 minutes
- **Lower is better**

### **Switches**
- Number of times machines change product types
- **Lower is better** (fewer interruptions)

### **Balance Imbalance (%)**
- How uneven the workload is across machines
- 0% = perfectly balanced
- 30% = one machine is way busier than others
- **Lower is better**

---

## Common Scenarios You'll See

### **Scenario A: Normal Day**
- All jobs fit comfortably
- Most deadlines met
- AI optimization clearly beats baseline
- **Result:** ✅ Success

### **Scenario B: Tight Constraints**
- 20 jobs, limited capacity
- Some rush jobs have impossible deadlines
- AI does its best but can't meet everything
- **Result:** ⚠️ Best Effort

### **Scenario C: Machine Failure**
- You're halfway through the day
- A machine breaks down
- System re-optimizes remaining jobs
- Works around the downtime
- **Result:** Usually ⚠️ Best Effort (emergency mode)

---

## Why You Might See Violations

### "Not all jobs assigned. Missing: J008, J017..."
- **Reason:** Not enough time/capacity to fit all jobs
- **Fix:** Extend shift hours, reduce job count, or add overtime

### "CRITICAL: Rush job J003 is 34 min late"
- **Reason:** Rush deadline is too tight given other constraints
- **Fix:** Relax the deadline or prioritize it higher

### "Job overlaps with downtime"
- **Reason:** Machine is scheduled for maintenance during that slot
- **Fix:** Remove/adjust the downtime window

---

## How the Agents Actually Talk to AI

When an agent needs to make a decision, it sends a prompt to Groq's Llama model like this:

**Example - Batching Agent:**
```
"You have 20 jobs with 3 product types: P_A, P_B, P_C.
Switching between types takes 10-15 minutes.
3 jobs are RUSH priority with tight deadlines.
What's the optimal batching sequence to minimize setup time
while prioritizing rush jobs?"
```

The AI responds with reasoning like:
```
"Group all P_A jobs together: J007, J005, J013...
Then switch to P_B for rush jobs: J003, J012...
This minimizes switches and handles urgent work first."
```

The agent then **implements** this strategy by actually building the schedule.

---

## Files You Probably Won't Touch

- `__init__.py` - Python boilerplate (ignore these)
- `__pycache__/` - Python cache folders (auto-generated)
- `debug_import.py` - Developer testing tool
- `diagnostics.py` - System health checker
- `test_downtime.py` - Unit test for downtime logic
- `verify_integration.py` - Integration test runner

---

## Quick Start Reminder

1. **Setup:**
   ```
   Double-click setup.bat (Windows)
   ```

2. **Get Groq API Key:**
   - Go to https://console.groq.com
   - Create free account
   - Copy API key
   - Paste into `.env` file

3. **Run:**
   ```
   streamlit run ui/app.py
   ```

4. **Use:**
   - Generate random jobs OR upload CSV
   - Click "🤖 Orchestrated (Full)"
   - Review results in dashboard

---

## Understanding System Configuration - Objective Weights

In the sidebar under "System Configuration," there's a section called **Objective Weights**. This is where you tell the AI agents what's most important to you. Think of it like setting priorities for your factory.

### What Are Objective Weights?

When the AI creates a schedule, it's trying to optimize multiple things at once:
- Minimize late deliveries (tardiness)
- Minimize wasted time switching products (setup time)
- Balance work evenly across machines (utilization)

But these goals often **conflict** with each other! The weights tell the AI which goal matters most.

### The Three Weights Explained

#### **1. Tardiness Weight (0.0 - 2.0)**
**What it controls:** How much the system cares about meeting deadlines

**Default:** 1.0 (normal priority)

**If you INCREASE it (e.g., 1.5 or 2.0):**
- Rush jobs get higher priority
- System tries harder to meet deadlines
- May accept more setup time to finish urgent jobs first
- **Use when:** Customer deadlines are critical, late fees are expensive

**If you DECREASE it (e.g., 0.5 or 0.0):**
- System cares less about deadlines
- May schedule jobs based on efficiency instead of urgency
- Could save setup time but miss deadlines
- **Use when:** Deadlines are flexible, efficiency is more important

**Example scenario:**
- Weight at 2.0: "Rush job J003 MUST finish by 11:45, even if it means extra changeovers"
- Weight at 0.5: "If grouping similar products saves time, go ahead even if J003 is a bit late"

---

#### **2. Setup Weight (0.0 - 2.0)**
**What it controls:** How much the system tries to minimize changeover time

**Default:** 1.0 (normal priority)

**If you INCREASE it (e.g., 1.5 or 2.0):**
- System strongly prefers batching same product types together
- Fewer product switches = less downtime
- May delay some jobs to group similar ones
- **Use when:** Changeovers are expensive/time-consuming, equipment takes long to reconfigure

**If you DECREASE it (e.g., 0.5 or 0.0):**
- System doesn't care much about grouping similar products
- Will switch freely if it helps balance or meet deadlines
- More interruptions but better deadline performance
- **Use when:** Product switches are quick/cheap, deadlines matter more

**Example scenario:**
- Weight at 2.0: "Run ALL P_A jobs together, then ALL P_B jobs, minimize switches"
- Weight at 0.5: "Mix product types freely if it helps finish urgent jobs faster"

---

#### **3. Balance Weight (0.0 - 2.0)**
**What it controls:** How evenly work is spread across machines

**Default:** 1.0 (normal priority)

**If you INCREASE it (e.g., 1.5 or 2.0):**
- System works hard to give each machine equal workload
- Prevents one machine from being slammed while others idle
- Better for long-term machine health and operator fairness
- **Use when:** You want fair workload distribution, prevent machine overuse

**If you DECREASE it (e.g., 0.5 or 0.0):**
- System doesn't care if one machine works way more than others
- May pile work on one machine if it's more efficient
- Can lead to imbalanced utilization
- **Use when:** Some machines are faster/newer, or balance doesn't matter

**Example scenario:**
- Weight at 2.0: "M1, M2, M3 should each work about 6-7 hours, keep it fair"
- Weight at 0.5: "If M1 can handle most P_B jobs efficiently, load it up, who cares about M3"

---

### How Weights Work Together

The AI uses these weights to calculate a **total cost** for each schedule:

```
Total Cost = (Tardiness × Tardiness_Weight) + 
             (Setup_Time × Setup_Weight) + 
             (Imbalance × Balance_Weight)
```

It picks the schedule with the **lowest total cost**.

### Real-World Weight Combinations

#### **Scenario: "Deadlines Are Everything"**
- Tardiness Weight: **2.0** ← Maximize deadline compliance
- Setup Weight: **0.5** ← Don't care about efficiency
- Balance Weight: **0.5** ← Don't care about fairness
- **Result:** Rush jobs almost never late, but lots of changeovers and uneven work

#### **Scenario: "Efficiency First"**
- Tardiness Weight: **0.5** ← Deadlines are flexible
- Setup Weight: **2.0** ← Minimize changeovers
- Balance Weight: **1.0** ← Some balance
- **Result:** Long product runs, minimal setup time, some jobs might be late

#### **Scenario: "Balanced Approach"** (Default)
- Tardiness Weight: **1.0**
- Setup Weight: **1.0**
- Balance Weight: **1.0**
- **Result:** Tries to satisfy all goals equally, good all-around performance

#### **Scenario: "Fair Workload Distribution"**
- Tardiness Weight: **1.0**
- Setup Weight: **0.5**
- Balance Weight: **2.0** ← Prioritize even distribution
- **Result:** Machines have similar workloads, may sacrifice some efficiency

---

### When to Adjust Weights

**Adjust weights BEFORE clicking optimization buttons.** Changes apply to all subsequent runs.

**You should increase Tardiness Weight if:**
- Customer complaints about late deliveries
- Facing penalty fees for missed deadlines
- Rush jobs consistently late in results

**You should increase Setup Weight if:**
- Too many product changeovers in the Gantt chart
- Machines spend more time switching than producing
- Setup time metric is high in comparison table

**You should increase Balance Weight if:**
- One machine shows 90% utilization, another shows 40%
- Balance Imbalance metric is >20% in results
- Want to distribute wear-and-tear across equipment

---

### Pro Tip: Experiment and Compare

Try running the same jobs with different weights:

1. **Run 1:** Default weights (1.0, 1.0, 1.0)
2. **Run 2:** Tardiness-focused (2.0, 0.5, 0.5)
3. **Run 3:** Setup-focused (0.5, 2.0, 0.5)

Compare the metrics table to see how weights affect outcomes. This helps you understand your system's trade-offs.

---

## Tips for Best Results

1. **Keep job count reasonable** - 15-25 jobs per shift is realistic
2. **Allow some overtime** - Gives flexibility for tight schedules
3. **Don't make all jobs rush** - System needs prioritization to work
4. **Check machine compatibility** - Make sure jobs CAN run on available machines
5. **Avoid excessive downtime** - Each downtime window reduces capacity
6. **Tune objective weights** - Adjust based on your business priorities (see section above)

---

## The Bottom Line

This system takes a hard scheduling problem and throws AI at it. The agents collaborate like a team of experts, each focusing on their specialty. The orchestrator makes them work together in a smart sequence.

When constraints are reasonable, you'll get perfect schedules. When constraints are impossible, you'll get the best possible effort with clear explanations of what couldn't be achieved.

It's designed for production environments where schedules change constantly, machines fail unexpectedly, and you need fast re-planning with AI-powered intelligence.

---

**That's the complete tour! You now understand every file and how the whole system works.**
