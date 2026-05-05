from datetime import datetime
from typing import List

import streamlit as st

LOG_KEY = "hl_activity_log"
MAX_ENTRIES = 80


def log_event(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} — {message}"
    if LOG_KEY not in st.session_state:
        st.session_state[LOG_KEY] = []
    st.session_state[LOG_KEY].append(line)
    if len(st.session_state[LOG_KEY]) > MAX_ENTRIES:
        st.session_state[LOG_KEY] = st.session_state[LOG_KEY][-MAX_ENTRIES:]


def get_activity_log() -> List[str]:
    return list(st.session_state.get(LOG_KEY, []))


def clear_activity_log() -> None:
    st.session_state[LOG_KEY] = []
