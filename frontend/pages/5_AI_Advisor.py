import streamlit as st
import requests as _req
import os
import json
import time

st.set_page_config(
    page_title="AI Advisor — QuadraWealth",
    page_icon="🤖",
    layout="wide",
)

# ── Custom CSS for Chat — Apple Style ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.main .block-container { padding-top: 1.5rem; max-width: 1100px; }

/* ─── Chat Bubble Styling ─── */
.chat-container { display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 2rem; }

.message {
    max-width: 85%;
    padding: 1.25rem 1.75rem;
    border-radius: 20px;
    font-size: 1.05rem;
    line-height: 1.55;
    position: relative;
    animation: fadeInUp 0.5s ease-out both;
}

.user-message {
    align-self: flex-end;
    background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
    color: white;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 15px rgba(0, 180, 216, 0.2);
}

.assistant-message {
    align-self: flex-start;
    background: #1A1F2E;
    color: #FAFAFA;
    border: 1px solid rgba(0, 212, 170, 0.15);
    border-bottom-left-radius: 4px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.agent-badge {
    display: inline-block;
    background: rgba(0, 212, 170, 0.15);
    color: #00D4AA;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 10px;
    margin-bottom: 8px;
    letter-spacing: 0.05em;
}

/* ─── Reasoning Accordion ─── */
.reasoning-box {
    background: rgba(0, 0, 0, 0.2);
    border-left: 3px solid #00D4AA;
    padding: 1rem;
    margin: 1rem 0;
    font-family: 'Inter', monospace !important;
    font-size: 0.85rem;
    color: rgba(250, 250, 250, 0.6);
    border-radius: 4px;
}

.step-indicator { color: #00D4AA; font-weight: 700; margin-right: 8px; }

/* ─── Animations ─── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ─── Sidebar Profile Badge ─── */
.profile-card {
    background: #1A1F2E;
    border: 1px solid rgba(0, 212, 170, 0.2);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.profile-label { font-size: 0.7rem; color: rgba(250,250,250,0.4); text-transform: uppercase; }
.profile-value { font-size: 0.9rem; font-weight: 600; color: #FAFAFA; margin-bottom: 6px; }

/* ─── Status ─── */
.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}
.status-live { background: #00D4AA; box-shadow: 0 0 10px #00D4AA; }
.status-mock { background: #FFB703; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### Agent Settings")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    risk_tolerance = st.select_slider(
        "Risk Profile",
        options=["conservative", "moderate", "aggressive"],
        value=st.session_state.get("risk_tolerance", "moderate")
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Backend Connection Info
    try:
        backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
        resp = _req.get(f"{backend_url}/api/agents/status", timeout=2)
        if resp.status_code == 200:
            status = resp.json()
            is_live = status.get("llm_live", False)
            modeling = status.get("modeling", "ReAct Multi-Agent Coordination")

            st.markdown(f"""
            <div class="profile-card">
                <div class="profile-label">Orchestrator Status</div>
                <div class="profile-value">
                    <span class="status-indicator {'status-live' if is_live else 'status-mock'}"></span>
                    {'Live AI Reasoning' if is_live else 'Template Fallback'}
                </div>
                <div class="profile-label">Agent Modeling</div>
                <div class="profile-value">{modeling}</div>
                <div class="profile-label">Specialist Network</div>
                <div class="profile-value">{", ".join(status.get("agents", []))}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Agents Service Offline")
    except Exception:
        st.warning("Could not connect to backend")

    if st.button("Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main UI ──
st.title("🤖 Multi-Agent AI Advisor")
st.markdown("### Ask QuadraWealth's network of specialists anything about your capital.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
chat_placeholder = st.container()
with chat_placeholder:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        agent = msg.get("agent", "You")

        if role == "user":
            st.markdown(f"""
            <div class="message user-message">
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            agent_details = msg.get("details", [])
            plan = msg.get("plan", {})

            with st.container():
                st.markdown(f"""
                <div class="message assistant-message">
                    <div class="agent-badge">AI Advisor</div>
                    {content}
                </div>
                """, unsafe_allow_html=True)

                if agent_details:
                    with st.expander("🔍 View Specialists' Reasoning & Collaboration"):
                        if plan:
                            st.info(f"**Plan:** {plan.get('rationale', 'Decomposing request.')}")

                        for detail in agent_details:
                            st.markdown(f"#### 🛰️ {detail['agent']} ({detail['role']})")
                            st.markdown(detail['response'])

                            if detail.get('reasoning_steps'):
                                steps_html = "".join([f'<div><span class="step-indicator">→</span>{s}</div>' for s in detail['reasoning_steps']])
                                st.markdown(f"""
                                <div class="reasoning-box">
                                    {steps_html}
                                </div>
                                """, unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input("Ex: Should I buy Apple stock and hedge with gold?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Rerun to show user message immediately
    st.rerun()

# Handle AI Response (after rerun)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]

    with st.spinner("🧠 Orchestrator is planning and delegating..."):
        try:
            backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
            payload = {
                "query": user_query,
                "risk_tolerance": risk_tolerance
            }
            start_time = time.time()
            response = _req.post(f"{backend_url}/api/agents/chat", json=payload, timeout=60)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["response"],
                    "details": data["agent_details"],
                    "plan": data["execution_plan"]
                })
                st.rerun()
            else:
                st.error(f"Error from agent system: {response.text}")
        except Exception as e:
            st.error(f"Failed to communicate with AI Agents: {e}")
