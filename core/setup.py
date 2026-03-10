import streamlit as st
from db import SessionLocal, User, Company
from core.i18n import _
from core.session import session_manager

def is_installed() -> bool:
    """Checks if the database has records to skip setup."""
    session = SessionLocal()
    try:
        user_count = session.query(User).count()
        company_count = session.query(Company).count()
        return user_count > 0 and company_count > 0
    except Exception:
        return False
    finally:
        session.close()

def run_setup():
    """
    Renders a 2-step setup wizard with data persistence.
    """
    st.set_page_config(page_title=_("System Installation"), layout="centered")
    
    # Initialize variables in session state if they don't exist
    if 'setup_step' not in st.session_state:
        st.session_state['setup_step'] = 1
    if 'temp_company' not in st.session_state:
        st.session_state['temp_company'] = ""
    if 'temp_lang' not in st.session_state:
        st.session_state['temp_lang'] = "en"

    st.title(_("Initial Setup"))
    
    # Visual Progress Indicator
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**Step 1:** {('🔵' if st.session_state['setup_step'] == 1 else '✅')}")
        st.caption(_("Configuration"))
    with cols[1]:
        st.markdown(f"**Step 2:** {('🔵' if st.session_state['setup_step'] == 2 else '⚪')}")
        st.caption(_("Admin Account"))
    
    st.divider()

    # --- STEP 1: ENVIRONMENT CONFIGURATION ---
    if st.session_state['setup_step'] == 1:
        with st.form("step_1_form"):
            st.subheader(_("Step 1: Workspace Settings"))
            
            lang_options = {"English": "en", "Español": "es"}
            # Set default index based on previously selected language
            current_lang_idx = 0 if st.session_state['temp_lang'] == 'en' else 1
            
            selected_lang_name = st.selectbox(
                "System Language / Idioma", 
                list(lang_options.keys()),
                index=current_lang_idx
            )
            
            # CRITICAL FIX: Use 'value' to restore the name when coming back
            company_name = st.text_input(
                _("Primary Company Name (e.g., Decomons)"),
                value=st.session_state['temp_company']
            )
            
            if st.form_submit_button(_("Next"), use_container_width=True):
                if company_name:
                    # Save data before moving forward
                    st.session_state['temp_lang'] = lang_options[selected_lang_name]
                    st.session_state['temp_company'] = company_name
                    st.session_state['setup_step'] = 2
                    st.rerun()
                else:
                    st.error(_("Please enter a company name."))

    # --- STEP 2: USER CREATION & FINALIZATION ---
    elif st.session_state['setup_step'] == 2:
        with st.form("step_2_form"):
            st.subheader(_("Step 2: Admin Credentials"))
            st.info(_("Creating admin for: {0}", st.session_state['temp_company']))
            
            admin_user = st.text_input(_("Administrator Username"))
            admin_pass = st.text_input(_("Password"), type="password")

            col_btns = st.columns(2)
            with col_btns[0]:
                # BACK BUTTON: Just changes the step, the data is already in session_state
                if st.form_submit_button(_("Back"), use_container_width=True):
                    st.session_state['setup_step'] = 1
                    st.rerun()
            
            with col_btns[1]:
                if st.form_submit_button(_("Install System"), type="primary", use_container_width=True):
                    if admin_user and admin_pass:
                        setup_session = SessionLocal()
                        try:
                            # 1. Create Company from temp storage
                            new_company = Company(name=st.session_state['temp_company'])
                            setup_session.add(new_company)
                            setup_session.flush()
                            
                            # 2. Create Admin User
                            new_user = User(username=admin_user, password=admin_pass, role="admin")
                            setup_session.add(new_user)
                            setup_session.commit()
                            
                            # 3. Final Session & Cookie Data
                            session_data = {
                                'logged_in': True,
                                'username': admin_user,
                                'role': "admin",
                                'company_id': new_company.id,
                                'company_name': st.session_state['temp_company'],
                                'language': st.session_state['temp_lang']
                            }
                            session_manager.set_session(session_data)
                            
                            st.success(_("System installed successfully! Welcome aboard."))
                            st.rerun()
                            
                        except Exception as e:
                            setup_session.rollback()
                            st.error(_("Installation error: {0}", str(e)))
                        finally:
                            setup_session.close()
                    else:
                        st.error(_("Please fill in all required fields."))