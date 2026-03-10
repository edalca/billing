import streamlit as st
import db
from utils import check_auth

check_auth()
# Only admins should see this (logic can be expanded)
if st.session_state.role != "admin":
    st.error("Access Denied: Admin only.")
    st.stop()

st.header("🏢 Admin Panel")

tab1, tab2 = st.tabs(["Manage Branches", "Manage Users"])

with tab1:
    st.subheader("Add New Branch")
    with st.form("new_branch_form"):
        new_branch = st.text_input("Branch Name (e.g., Tegucigalpa)")
        if st.form_submit_button("Create Branch"):
            session = db.SessionLocal()
            try:
                exists = session.query(db.Branch).filter(db.Branch.name == new_branch).first()
                if exists:
                    st.warning("Branch already exists.")
                else:
                    branch = db.Branch(name=new_branch)
                    session.add(branch)
                    session.commit()
                    st.success(f"Branch '{new_branch}' created!")
            finally:
                session.close()

    st.subheader("Existing Branches")
    session = db.SessionLocal()
    branches = session.query(db.Branch).all()
    for b in branches:
        st.text(f"📍 ID: {b.id} | Name: {b.name}")
    session.close()

with tab2:
    st.subheader("User Management")
    st.info("System currently has 1 Admin. Add user logic here.")
    # (Similar form logic for db.User can go here)