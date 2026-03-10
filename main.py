import streamlit as st
import db
from core.setup import is_installed, run_setup
from core.login import run_login
from core.navigation import render_navigation
from core.session import session_manager

# 1. DB INITIALIZATION
db.Base.metadata.create_all(bind=db.engine)

# 2. SESSION RESTORATION
# Try to log the user in automatically if a cookie exists
session_manager.sync_from_cookie()

# 3. MAIN FLOW
if not is_installed():
    run_setup()
    st.stop()

if not st.session_state.get('logged_in'):
    run_login()
    st.stop()

render_navigation()