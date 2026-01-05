"""
Multi-Agent Production Job Optimizer - Manager Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, time
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
from utils.data_generator import generate_random_jobs, get_demo_machines, get_demo_constraint

st.set_page_config(
    page_title="Multi-Agent Job Optimizer",
    page_icon="🏭",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-metric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 0.85em;
        font-weight: 700;
        border-radius: 0.25rem;
        background-color: #28a745;
        color: white;
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

# Sidebar Configuration
with st.sidebar:
    st.header("📥 Data Management")
    
    gen_col1, gen_col2 = st.columns(2)
    with gen_col1:
        if st.button("🎲 Small Batch", use_container_width=True):
            st.session_state.jobs = generate_random_jobs(8, rush_probability=0.2)
            st.session_state.results = {}
            st.success("Generated 8 jobs")
    with gen_col2:
        if st.button("🚀 Production", use_container_width=True):
            st.session_state.jobs = generate_random_jobs(20, rush_probability=0.3)
            st.session_state.results = {}
            st.success("Generated 20 jobs")
            
    st.markdown("---")
    st.header("⚙️ Constraint Tweaks")
    
    constraint = st.session_state.constraint
    shift_col1, shift_col2 = st.columns(2)
    with shift_col1:
        constraint.shift_start = st.time_input("Start", value=constraint.shift_start)
    with shift_col2:
        constraint.shift_end = st.time_input("End", value=constraint.shift_end)
        
    st.markdown("---")
    st.markdown("### System Status")
    st.success("✅ Groq AI Connected")
    st.info(f"📦 {len(st.session_state.jobs)} jobs loaded")

# Data Preview
if st.session_state.jobs:
    with st.expander("📋 View Input Job Queue", expanded=False):
        data_preview = [{
            "Job ID": j.job_id,
            "Product": j.product_type,
            "Duration": f"{j.processing_time} min",
            "Deadline": j.due_time.strftime("%H:%M"),
            "Priority": "⚡ RUSH" if j.is_rush else "Normal"
        } for j in st.session_state.jobs]
        st.dataframe(pd.DataFrame(data_preview), use_container_width=True)

# Main Controls
st.header("🎯 AI Orchestration")
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("📊 Baseline (FIFO)", use_container_width=True):
        if not st.session_state.jobs: st.error("No jobs!")
        else:
            with st.spinner("Running Baseline..."):
                baseline = BaselineScheduler()
                sched, explanation = baseline.schedule(st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                st.session_state.results['Baseline'] = {'schedule': sched, 'explanation': explanation}
                st.success("Fixed Baseline Done")

with c2:
    if st.button("🔄 Batching (AI)", use_container_width=True):
        if not st.session_state.jobs: st.error("No jobs!")
        else:
            with st.spinner("AI Grouping..."):
                agent = BatchingAgent()
                sched, explanation = agent.create_batched_schedule(st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                sched.calculate_kpis(st.session_state.machines, st.session_state.constraint)
                st.session_state.results['Batching'] = {'schedule': sched, 'explanation': explanation}
                st.success("Batching Optimized")

with c3:
    if st.button("⚖️ Load Balance (AI)", use_container_width=True):
        if 'Batching' not in st.session_state.results: st.error("Run Batching first!")
        else:
            with st.spinner("Balancing Workload..."):
                agent = BottleneckAgent()
                sched, explanation = agent.rebalance_schedule(st.session_state.results['Batching']['schedule'], st.session_state.machines, st.session_state.constraint, st.session_state.jobs)
                sched.calculate_kpis(st.session_state.machines, st.session_state.constraint)
                st.session_state.results['Balanced'] = {'schedule': sched, 'explanation': explanation}
                st.success("Workload Balanced")

with c4:
    if st.button("🤖 Orchestrated (Full)", use_container_width=True, type="primary"):
        if not st.session_state.jobs: st.error("No jobs!")
        else:
            with st.status("🚀 Multi-Agent Workflow Running...", expanded=True) as status:
                st.write("👔 Supervisor analyzing...")
                st.write("🔄 specialist agents collaborating...")
                orchestrator = OptimizationOrchestrator()
                res = orchestrator.optimize(st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
                if res['success']:
                    st.session_state.results['Orchestrated'] = {'schedule': res['schedule'], 'explanation': res['explanation']}
                    status.update(label="✅ Comprehensive Optimization Success!", state="complete")
                    st.balloons()
                else:
                    status.update(label="❌ Optimization Failed - Constraints unmet", state="error")

# Visualization Logic
def create_gantt(schedule):
    colors = {'P_A': '#1f77b4', 'P_B': '#ff7f0e', 'P_C': '#2ca02c'}
    fig = go.Figure()
    for m_id, assigns in schedule.assignments.items():
        for a in assigns:
            start_min = a.start_time.hour * 60 + a.start_time.minute
            dur = a.job.processing_time
            fig.add_trace(go.Bar(
                name=a.job.job_id, y=[m_id], x=[dur], base=start_min, orientation='h',
                marker=dict(color=colors.get(a.job.product_type, '#999999')),
                text=f"{a.job.job_id}({a.job.product_type})", textposition='inside',
                hovertemplate=f"<b>{a.job.job_id}</b><br>Start: {a.start_time.strftime('%H:%M')}<br>Priority: {a.job.priority}<extra></extra>"
            ))
    fig.update_layout(
        barmode='overlay', height=300, margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(tickmode='array', tickvals=[480, 540, 600, 660, 720, 780, 840, 900, 960],
                  ticktext=['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'],
                  title="Shift Timeline")
    )
    return fig

# Dashboard Display
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
    
    # Selection for detailed view
    view_mode = st.radio("Select Schedule to Visualize:", list(st.session_state.results.items()), format_func=lambda x: x[0], horizontal=True)
    selected_name, selected_data = view_mode
    selected_sched = selected_data['schedule']
    selected_explanation = selected_data.get('explanation', "No detailed reasoning available for this mode.")
    
    col_viz1, col_viz2 = st.columns([2, 1])
    with col_viz1:
        st.subheader(f"📅 {selected_name} Schedule Visualization")
        st.plotly_chart(create_gantt(selected_sched), use_container_width=True)
        
        # Job Allocation Table
        st.subheader(f"📋 {selected_name} Job Allocation Details")
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
        
    with col_viz2:
        st.subheader("📝 AI Reasoning")
        st.markdown(selected_explanation)
            
    # Validation Check
    st.subheader("✅ Compliance Report")
    with st.spinner("Validating..."):
        v_agent = ConstraintAgent()
        valid, violations, report = v_agent.validate_schedule(selected_sched, st.session_state.jobs, st.session_state.machines, st.session_state.constraint)
        if valid:
            st.success("✓ This schedule complies with all operational constraints.")
        else:
            st.error(f"✗ Found {len(violations)} violations.")
            for v in violations: st.write(f"- {v}")


st.markdown("---")
st.markdown("<div style='text-align: center; color: #999;'>Multi-Agent Production Optimizer | Day 5 Manager Demo</div>", unsafe_allow_html=True)

