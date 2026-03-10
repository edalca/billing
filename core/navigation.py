import streamlit as st
from core.i18n import _
from core.session import session_manager

def render_navigation():
    """
    Renders the sidebar navigation and handles the routing for all views.
    Displays active session information and provides a one-click logout 
    using the centralized SessionManager.
    """
    
    # 1. Sidebar Header: User and Company Information
    st.sidebar.success(_("Active Company: {0}", st.session_state.get('company_name', 'N/A')))
    
    user_info = _("User: {0} ({1})", 
                  st.session_state.get('username', 'Guest'), 
                  st.session_state.get('role', 'user').capitalize())
    st.sidebar.info(user_info)

    # 2. Logout Button
    # The session_manager.logout() handles both Cookie removal and session_state.clear()
    if st.sidebar.button(_("Log Out"), use_container_width=True, type="secondary"):
        session_manager.logout()

    st.sidebar.divider()

    # 3. Navigation Structure (Pages)
    # Ensure these file paths exist in your /views directory
    pages = {
        _("Administration"): [
            st.Page("views/company.py", title=_("Companies & Branches"), icon="⚙️"),
        ],
        _("Operations"): [
            st.Page("views/stock.py", title=_("Inventory Upload"), icon="📦"),
            st.Page("views/generate.py", title=_("Generate Invoices"), icon="🚀"),
            st.Page("views/history.py", title=_("History & PDF"), icon="🧾"),
        ]
    }

    # 4. Run Streamlit Navigation
    pg = st.navigation(pages)
    pg.run()