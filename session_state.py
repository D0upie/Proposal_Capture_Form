# session_state.py

import streamlit as st

class SessionState:
    def __init__(self):
        self.data = {}

session_state = SessionState()
