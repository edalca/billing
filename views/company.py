import streamlit as st
from db import SessionLocal, Company, Branch
from core.i18n import _

def render_company_view():
    """
    Renders the Management interface for Companies and Branches.
    Features a tabbed system for managing the current company's branches
    and a global view to create new companies.
    """
    st.title(_("Administration: Companies & Branches"))
    
    # 1. Get session context
    active_company_id = st.session_state.get('company_id')
    user_role = st.session_state.get('role')
    
    db_session = SessionLocal()
    
    try:
        # Define Tabs
        tab_my_company, tab_all_companies = st.tabs([
            _("🏢 My Company"), 
            _("🌐 All Companies")
        ])

        # --- TAB 1: MY COMPANY & BRANCHES ---
        with tab_my_company:
            current_company = db_session.query(Company).filter(Company.id == active_company_id).first()
            if current_company:
                st.header(_("Active Workspace: {0}", current_company.name))
                
                # Branch Management (Current logic)
                st.subheader(_("Managed Branches"))
                branches = current_company.branches
                if branches:
                    for branch in branches:
                        with st.expander(f"📍 {branch.name}"):
                            st.write(_("Branch ID: {0}", branch.id))
                else:
                    st.info(_("No branches registered yet."))

                st.divider()
                with st.form("add_branch_form", clear_on_submit=True):
                    st.subheader(_("Add New Branch"))
                    new_branch_name = st.text_input(_("Branch Name"))
                    if st.form_submit_button(_("Create Branch"), type="primary"):
                        if new_branch_name:
                            new_branch = Branch(name=new_branch_name, company_id=active_company_id)
                            db_session.add(new_branch)
                            db_session.commit()
                            st.success(_("Branch created!"))
                            st.rerun()
            else:
                st.error(_("Active company not found."))

        # --- TAB 2: GLOBAL COMPANY MANAGEMENT ---
        with tab_all_companies:
            st.header(_("System Companies"))
            
            # List all companies in the DB
            all_companies = db_session.query(Company).all()
            
            # Display as a clean table or list
            for comp in all_companies:
                is_active = " (Active)" if comp.id == active_company_id else ""
                st.write(f"🏢 **{comp.name}** {is_active}")
                st.caption(_("ID: {0} | Branches: {1}", comp.id, len(comp.branches)))

            st.divider()

            # Form to create a NEW Company
            if user_role == "admin":
                st.subheader(_("Register New Company"))
                with st.form("add_company_form", clear_on_submit=True):
                    new_comp_name = st.text_input(_("New Company Name"))
                    if st.form_submit_button(_("Create Company"), type="primary"):
                        if new_comp_name:
                            try:
                                new_comp = Company(name=new_comp_name)
                                db_session.add(new_comp)
                                db_session.commit()
                                st.success(_("Company '{0}' registered!", new_comp_name))
                                st.rerun()
                            except Exception as e:
                                db_session.rollback()
                                st.error(_("Error: {0}", str(e)))
                        else:
                            st.warning(_("Please enter a name."))
            else:
                st.warning(_("Only administrators can register new companies."))

    finally:
        db_session.close()

render_company_view()