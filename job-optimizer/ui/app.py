"""
Multi-Agent Production Job Optimizer - Manager Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.job import Job
from models.machine import Machine, Constraint
from utils.baseline_scheduler import BaselineScheduler
from agents.batching_agent import BatchingAgent
from agents.bottleneck_agent import BottleneckAgent
from agents.constraint_agent import ConstraintAgent
from agents.orchestrator import OptimizationOrchestrator
from utils.data_generator import (
    generate_random_jobs, 
    get_demo_machines, 
    get_demo_constraint,
    generate_random_downtime,
    parse_downtime_csv,
    parse_jobs_csv
)
from typing import Tuple, List

st.set_page_config(
    page_title="Multi-Agent Job Optimizer",
    page_icon="🏭",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-family: 'Outfit', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1f77b4, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        text-align: center;
        margin-bottom: 2.5rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Card/Container Styling */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
    
    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #f0f2f6;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fb;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🏭 Multi-Agent Production Optimizer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Driven Manufacturing Scheduling & Load Balance</p>', unsafe_allow_html=True)

# Initialize session state
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'machines' not in st.session_state:
    st.session_state.machines = get_demo_machines()
if 'constraint' not in st.session_state:
    st.session_state.constraint = get_demo_constraint()
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'data_mode' not in st.session_state:
    st.session_state.data_mode = "Random"
if 'last_downtime_msg' not in st.session_state:
    st.session_state.last_downtime_msg = ""

# Visualization Logic
def create_gantt(schedule, machines, constraint):
    # Dynamic Colors for Products
    unique_prods = set()
    for m in machines: unique_prods.update(m.capabilities)
    color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    colors = {prod: color_palette[i % len(color_palette)] for i, prod in enumerate(sorted(list(unique_prods)))}
    
    fig = go.Figure()
    
    # Add Downtime first (as background)
    for m in machines:
        for dt in m.downtime_windows:
            start_min = dt.start_time.hour * 60 + dt.start_time.minute
            end_min = dt.end_time.hour * 60 + dt.end_time.minute
            dur = end_min - start_min
            fig.add_trace(go.Bar(
                name="Downtime", y=[m.machine_id], x=[dur], base=start_min, orientation='h',
                marker=dict(color='rgba(200, 200, 200, 0.6)', line=dict(color='gray', width=1)),
                text=f"DOWNTIME: {dt.reason}", textposition='inside',
                showlegend=False,
                hoverinfo='text'
            ))

    for m_id, assigns in schedule.assignments.items():
        for a in assigns:
            start_min = a.start_time.hour * 60 + a.start_time.minute
            dur = a.job.processing_time
            fig.add_trace(go.Bar(
                name=a.job.job_id, y=[m_id], x=[dur], base=start_min, orientation='h',
                marker=dict(color=colors.get(a.job.product_type, '#999999')),
                text=f"{a.job.job_id}", textposition='inside',
                hovertemplate=f"<b>{a.job.job_id} ({a.job.product_type})</b><br>Start: {a.start_time.strftime('%H:%M')}<br>End: {a.end_time.strftime('%H:%M')}<br>Priority: {a.job.priority}<extra></extra>"
            ))
            
    # Dynamic Ticks based on shift duration
    shift_start_hour = constraint.shift_start.hour
    shift_end_hour = constraint.shift_end.hour + (1 if constraint.shift_end.minute > 0 else 0)
    tickvals = [h * 60 for h in range(shift_start_hour, shift_end_hour + 1)]
    ticktext = [f"{h:02d}:00" for h in range(shift_start_hour, shift_end_hour + 1)]
    
    fig.update_layout(
        barmode='overlay', height=350, margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(tickmode='array', tickvals=tickvals, ticktext=ticktext, title="Shift Timeline")
    )
    return fig

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio("Go to:", ["📁 Data Setup", "🚀 Optimization Engine", "⚙️ System Configuration"])
    
    st.markdown("---")
    st.markdown("### 📊 System Health")
    st.success("✅ Groq AI Connected")
    num_jobs = len(st.session_state.jobs)
    num_dt = sum(len(m.downtime_windows) for m in st.session_state.machines)
    st.info(f"📦 {num_jobs} Jobs Loaded")
    if num_dt > 0:
        st.warning(f"⚠️ {num_dt} Downtime Events")
    else:
        st.info("No Downtime Active")

# --- PAGE: DATA SETUP ---
if page == "📁 Data Setup":
    st.header("📋 Production Data Setup")
    
    tab1, tab2 = st.tabs(["🏗️ Jobs Management", "📉 Downtime & Assets"])
    
    with tab1:
        st.subheader("Manage Production Jobs")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Scenario A: POC / Demo Mode**")
            job_count = st.number_input("Number of jobs to generate", 5, 50, 15)
            rush_prob = st.slider("Rush Order Probability", 0.0, 1.0, 0.2)
            if st.button("🎲 Generate Random Jobs", use_container_width=True):
                st.session_state.jobs = generate_random_jobs(
                    job_count, 
                    rush_probability=rush_prob, 
                    machines=st.session_state.machines, 
                    constraint=st.session_state.constraint
                )
                st.session_state.results = {}
                st.success(f"Generated {job_count} jobs successfully!")
                
        with col2:
            st.info("**Scenario B: Industry Level (CSV Upload)**")
            st.markdown("""
            **CSV Format:** `job_id, product_type, processing_time, due_time, priority, machine_options`
            *(Note: machine_options use ';' separator)*
            """)
            job_file = st.file_uploader("Upload jobs.csv", type="csv")
            if job_file:
                content = job_file.getvalue().decode("utf-8")
                jobs, errors = parse_jobs_csv(content)
                if errors:
                    for err in errors: st.error(err)
                else:
                    st.session_state.jobs = jobs
                    st.session_state.results = {}
                    st.success(f"Loaded {len(jobs)} jobs from CSV!")
        
        if st.session_state.jobs:
            st.markdown("---")
            st.subheader("Current Job Queue")
            data_preview = [{
                "Job ID": j.job_id,
                "Product": j.product_type,
                "Duration": f"{j.processing_time} min",
                "Deadline": j.due_time.strftime("%H:%M"),
                "Priority": "⚡ RUSH" if j.is_rush else "Normal",
                "Compatibility": ", ".join(j.machine_options)
            } for j in st.session_state.jobs]
            st.dataframe(pd.DataFrame(data_preview), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Machine Availability & Downtime")
        dt_col1, dt_col2 = st.columns(2)
        
        with dt_col1:
            st.info("**Scenario A: Random Stress-Test**")
            if st.button("🚧 Inject Random Downtime", use_container_width=True):
                generate_random_downtime(st.session_state.machines, st.session_state.constraint)
                st.session_state.results = {}
                st.warning("Random downtime injected into system.")
                
            if st.button("🧹 Clear All Downtime", use_container_width=True):
                for m in st.session_state.machines:
                    m.downtime_windows = []
                st.session_state.results = {}
                st.success("All machines cleared of downtime.")
                
        with dt_col2:
            st.info("**Scenario B: Maintenance Schedule (CSV)**")
            st.markdown("""
            **CSV Format:** `machine_id, downtime_start, downtime_end, reason`
            """)
            dt_file = st.file_uploader("Upload downtime.csv", type="csv")
            if dt_file:
                content = dt_file.getvalue().decode("utf-8")
                errors = parse_downtime_csv(content, st.session_state.machines)
                if errors:
                    for err in errors: st.error(err)
                else:
                    st.session_state.results = {}
                    st.success("Downtime schedule updated!")
        
        st.markdown("---")
        st.subheader("Asset Status")
        m_data = []
        for m in st.session_state.machines:
            m_data.append({
                "Machine": m.machine_id,
                "Capabilities": ", ".join(m.capabilities),
                "Active Downtimes": len(m.downtime_windows),
                "Next Event": m.downtime_windows[0].reason if m.downtime_windows else "None"
            })
        st.table(pd.DataFrame(m_data))

# --- PAGE: OPTIMIZATION ENGINE ---
elif page == "🚀 Optimization Engine":
    st.header("🎯 Multi-Agent Orchestration")
    
    if not st.session_state.jobs:
        st.warning("⚠️ No jobs loaded. Please go to **Data Setup** first.")
    else:
        # Optimization Controls
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("📊 Baseline (FIFO)", use_container_width=True):
                with st.spinner("Calculating..."):
                    baseline = BaselineScheduler()
                    sched, explanation = baseline.schedule(st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                    st.session_state.results['Baseline'] = {'schedule': sched, 'explanation': explanation}

        with c2:
            if st.button("🔄 Batching (AI)", use_container_width=True):
                with st.spinner("Optimizing..."):
                    agent = BatchingAgent()
                    sched, explanation = agent.create_batched_schedule(st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                    sched.calculate_kpis(st.session_state.machines, st.session_state.constraint)
                    st.session_state.results['Batching'] = {'schedule': sched, 'explanation': explanation}

        with c3:
            if st.button("⚖️ Load Balance (AI)", use_container_width=True):
                if 'Batching' not in st.session_state.results: st.error("Run Batching first!")
                else:
                    with st.spinner("Balancing..."):
                        agent = BottleneckAgent()
                        sched, explanation = agent.rebalance_schedule(st.session_state.results['Batching']['schedule'], st.session_state.machines, st.session_state.constraint, st.session_state.jobs)
                        sched.calculate_kpis(st.session_state.machines, st.session_state.constraint)
                        st.session_state.results['Balanced'] = {'schedule': sched, 'explanation': explanation}

        with c4:
            if st.button("🤖 Orchestrated (Full)", use_container_width=True, type="primary"):
                with st.status("🚀 Collaboration in Progress...", expanded=True) as status:
                    orchestrator = OptimizationOrchestrator()
                    res = orchestrator.optimize(st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                    
                    if res['schedule']:
                        st.session_state.results['Orchestrated'] = {'schedule': res['schedule'], 'explanation': res['explanation']}
                        
                    if res['success']:
                        status.update(label="✅ Optimization Success!", state="complete")
                        st.balloons()
                    else:
                        status.update(label="⚠️ Constraints Unmet (Best Effort shown)", state="error")

        # Scenario C: Sudden Failure
        st.markdown("---")
        st.subheader("🚨 Scenario C: Sudden Machine Failure")
        with st.expander("Simulate Real-time Disruption", expanded=False):
            dis_c1, dis_c2, dis_c3 = st.columns(3)
            with dis_c1:
                fail_m_id = st.selectbox("Failed Machine", [m.machine_id for m in st.session_state.machines])
            with dis_c2:
                mid_shift_min = (st.session_state.constraint.shift_start.hour * 60 + st.session_state.constraint.shift_start.minute + 
                                 st.session_state.constraint.shift_end.hour * 60 + st.session_state.constraint.shift_end.minute) // 2
                fail_time = st.time_input("Start Time", value=time(mid_shift_min // 60, mid_shift_min % 60))
            with dis_c3:
                fail_dur = st.number_input("Minutes Down", value=120, step=15)

            if st.button("💥 Trigger Failure & Re-optimize", use_container_width=True, type="primary"):
                now = datetime.now()
                fail_start_dt = datetime.combine(now.date(), fail_time)
                fail_end_dt = fail_start_dt + timedelta(minutes=fail_dur)
                target_machine = next((m for m in st.session_state.machines if m.machine_id == fail_m_id))
                target_machine.add_downtime(fail_start_dt, fail_end_dt, "Panic: Unplanned Failure")
                
                with st.status("🔄 EMERGENCY ACTION...", expanded=True) as status:
                    orchestrator = OptimizationOrchestrator()
                    res = orchestrator.optimize(st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                    if res['success']:
                        st.session_state.results['Event-Driven'] = {'schedule': res['schedule'], 'explanation': res['explanation']}
                        status.update(label="✅ Disruption Resolved", state="complete")
                        st.snow()

        # Dashboard Logic
        if st.session_state.results:
            st.markdown("---")
            st.header("📊 Strategy Comparison Dashboard")
            
            # Comparison Table
            metrics = ["Tardiness (min)", "Setup Time (min)", "Switches", "Balance Imbalance (%)"]
            comp_data = {"Metric": metrics}
            for name, data in st.session_state.results.items():
                k = data['schedule'].kpis
                comp_data[name] = [k.total_tardiness, k.total_setup_time, k.num_setup_switches, f"{k.utilization_imbalance:.1f}%"]
            st.table(pd.DataFrame(comp_data))
            
            view_mode = st.radio("Visualize Plan:", list(st.session_state.results.items()), format_func=lambda x: x[0], horizontal=True)
            selected_name, selected_data = view_mode
            selected_sched = selected_data['schedule']
            selected_explanation = selected_data.get('explanation', "Details processing...")
            
            v_col1, v_col2 = st.columns([2, 1])
            with v_col1:
                st.subheader(f"📅 {selected_name} Visualization")
                st.plotly_chart(create_gantt(selected_sched, st.session_state.machines, st.session_state.constraint), use_container_width=True)
                
                # Job Allocation Table
                st.subheader("📋 Job Allocation Details")
                sched_rows = []
                for m_id, assigns in selected_sched.assignments.items():
                    for a in assigns:
                        sched_rows.append({
                            "Machine": m_id,
                            "Job ID": a.job.job_id,
                            "Product": a.job.product_type,
                            "Start": a.start_time.strftime("%H:%M"),
                            "End": a.end_time.strftime("%H:%M"),
                            "Duration": f"{a.job.processing_time} min",
                            "Priority": "⚡ RUSH" if a.job.is_rush else "Normal"
                        })
                if sched_rows:
                    df_sched = pd.DataFrame(sched_rows).sort_values(by=["Machine", "Start"])
                    st.dataframe(df_sched, use_container_width=True, hide_index=True)

            with v_col2:
                st.markdown("### 📝 AI Reasoning")
                st.markdown(selected_explanation)
                
                # Compliance Summary
                st.markdown("### ✅ Compliance")
                with st.spinner("Validating..."):
                    v_agent = ConstraintAgent()
                    valid, violations, report = v_agent.validate_schedule(selected_sched, st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                    if valid:
                        st.success("Complies with all constraints.")
                    else:
                        st.error(f"{len(violations)} violations found.")
                        # Show all violations in an expander for readability
                        with st.expander("View All Violations", expanded=True):
                            for v in violations: st.write(f"- {v}")

# --- PAGE: SYSTEM CONFIGURATION ---
elif page == "⚙️ System Configuration":
    st.header("⚙️ Global Constraints & Policy")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Shift Boundaries")
        st.session_state.constraint.shift_start = st.time_input("Shift Start", value=st.session_state.constraint.shift_start)
        st.session_state.constraint.shift_end = st.time_input("Shift End", value=st.session_state.constraint.shift_end)
        st.session_state.constraint.max_overtime_minutes = st.number_input("Max Overtime (min)", value=st.session_state.constraint.max_overtime_minutes)
        
    with col2:
        st.subheader("Objective Weights")
        st.session_state.constraint.tardiness_weight = st.slider("Tardiness Weight", 0.0, 2.0, st.session_state.constraint.tardiness_weight)
        st.session_state.constraint.setup_weight = st.slider("Setup Weight", 0.0, 2.0, st.session_state.constraint.setup_weight)
        st.session_state.constraint.utilization_weight = st.slider("Balance Weight", 0.0, 2.0, st.session_state.constraint.utilization_weight)
        
    st.markdown("---")
    st.info("System configuration changes will apply to all subsequent optimization runs.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #999;'>Multi-Agent Production Optimizer | Premium Manager Dashboard V2.0</div>", unsafe_allow_html=True)

