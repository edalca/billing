import streamlit as st
from streamlit_cookies_controller import CookieController

# Name of the cookie that will store the session data
COOKIE_NAME = "decomons_session"

class SessionManager:
    """
    Manages user session persistence using browser cookies and Streamlit session state.
    Provides a centralized API for setting, getting, and clearing session data.
    """
    def __init__(self):
        self.controller = CookieController()

    def get_saved_session(self) -> dict:
        """Retrieves the session data from the browser cookie."""
        return self.controller.get(COOKIE_NAME)

    def set_session(self, data: dict):
        """
        Saves session data to both Streamlit's memory and a browser cookie.
        Valid for 30 days.
        """
        # 1. Update memory (Session State)
        for key, value in data.items():
            st.session_state[key] = value
        
        # 2. Update browser storage (Cookie)
        self.controller.set(COOKIE_NAME, data)

    def logout(self):
        """Clears all session data from memory and deletes the browser cookie."""
        self.controller.remove(COOKIE_NAME)
        st.session_state.clear()
        st.rerun()

    def sync_from_cookie(self):
        """
        Attempts to restore a session from a cookie if the memory is empty.
        Used at application startup.
        """
        saved = self.get_saved_session()
        if saved and not st.session_state.get('logged_in'):
            try:
                for key, value in saved.items():
                    st.session_state[key] = value
            except Exception:
                # If cookie is corrupted, clear it
                self.controller.remove(COOKIE_NAME)

# Initialize a single instance to be used across the app
session_manager = SessionManager()