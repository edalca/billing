import streamlit as st
from db import SessionLocal, Company
from db.user import authenticate
from core.i18n import _
from core.session import session_manager

def run_login():
    """
    Renders the login interface and handles the authentication process.
    Uses the centralized SessionManager to persist the session via cookies.
    """
    st.set_page_config(page_title=_("Login System"), layout="centered")
    
    st.title(_("System Login"))
    st.markdown("---")
    
    # 1. Fetch available companies for the dropdown
    login_session = SessionLocal()
    try:
        companies = login_session.query(Company).all()
        company_dict = {c.name: c.id for c in companies}
    finally:
        login_session.close()

    # 2. Safety check: Ensure the system has data
    if not company_dict:
        st.error(_("Critical Error: No registered companies found."))
        st.stop()

    # 3. Login Form
    with st.container():
        with st.form("login_form"):
            selected_company_name = st.selectbox(
                _("Select Workspace"), 
                list(company_dict.keys())
            )
            input_user = st.text_input(_("Username"))
            input_pass = st.text_input(_("Password"), type="password")

            submit = st.form_submit_button(_("Log In"), use_container_width=True, type="primary")

            if submit:
                if input_user and input_pass:
                    # Validate credentials against the database
                    user_role = authenticate(input_user, input_pass)
                    
                    if user_role:
                        # Prepare data for the session
                        session_data = {
                            'logged_in': True,
                            'username': input_user,
                            'role': user_role,
                            'company_id': company_dict[selected_company_name],
                            'company_name': selected_company_name,
                            'language': 'es'
                        }
                        
                        # Use the central manager to set everything (State + Cookie)
                        session_manager.set_session(session_data)
                        
                        # Force a rerun to enter the main application
                        st.rerun()
                    else:
                        st.error(_("Invalid username or password."))
                else:
                    st.warning(_("Please fill in all credentials."))