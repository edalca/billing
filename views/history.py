import streamlit as st
import pandas as pd
import db
import calendar
from datetime import date
from sqlalchemy import extract
from core.i18n import _
# Importamos la lógica de impresión (asegúrate de que la ruta sea correcta en tu proyecto)
from utils.print import get_invoices_pdf_bytes 

def render_history_view():
    """
    Renders the Invoice History view.
    Allows filtering by branch and period, viewing totals, and generating 
    consolidated PDFs for the selected invoices.
    """
    st.header(_("History & PDF Generation"))

    # Localized months list
    MONTHS_LIST = [
        "", _("January"), _("February"), _("March"), _("April"), _("May"), _("June"),
        _("July"), _("August"), _("September"), _("October"), _("November"), _("December")
    ]

    # --- 1. FILTERS ---
    with st.container(border=True):
        col_b, col_m, col_y = st.columns(3)
        
        company_id = st.session_state.get('company_id')
        db_session = db.SessionLocal()
        try:
            # Multi-company security: only fetch branches for the current company
            available_branches = db_session.query(db.Branch).filter(db.Branch.company_id == company_id).all()
            branch_map = {b.name: b.id for b in available_branches}
        finally:
            db_session.close()

        if not branch_map:
            st.error(_("No branches found. Please create one in Administration."))
            st.stop()

        sel_branch_name = col_b.selectbox(_("Branch"), list(branch_map.keys()))
        target_branch_id = branch_map[sel_branch_name]
        
        sel_month = col_m.selectbox(
            _("Month"), 
            range(1, 13), 
            index=date.today().month-1, 
            format_func=lambda x: MONTHS_LIST[x]
        )
        sel_year = col_y.selectbox(_("Year"), [2025, 2026], index=1)

    st.divider()

    # --- 2. DATA QUERY ---
    session = db.SessionLocal()
    try:
        # Fetch invoices for the selected period and branch
        invoices = session.query(db.Invoice).filter(
            db.Invoice.branch_id == target_branch_id,
            extract('month', db.Invoice.date) == sel_month,
            extract('year', db.Invoice.date) == sel_year
        ).order_by(db.Invoice.invoice_no.asc()).all()

        if invoices:
            # 3. METRICS AND PDF GENERATION
            total_billing = sum(i.grand_total for i in invoices)
            st.metric(_("Total Monthly Billing"), f"L. {total_billing:,.2f}")

            # PDF Generation Button
            if st.button(_("Generate Invoices PDF (One per page)"), use_container_width=True, type="primary"):
                with st.spinner(_("Processing documents...")):
                    try:
                        # Call your existing PDF utility
                        pdf_bytes = get_invoices_pdf_bytes(invoices, sel_branch_name, sel_month, sel_year)
                        
                        st.download_button(
                            label=_("⬇️ Download Ready PDF File"),
                            data=bytes(pdf_bytes),
                            file_name=f"Facturas_{sel_branch_name}_{sel_month}_{sel_year}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(_("Error generating PDF: {0}", str(e)))

            st.divider()
            
            # 4. REFERENCE TABLE
            st.subheader(_("Invoice Records"))
            df_data = [{
                _("Invoice No."): i.invoice_no, 
                _("Customer"): i.customer_name, 
                _("Date"): pd.to_datetime(i.date).strftime('%d/%m/%Y'), 
                _("Total"): f"L. {i.grand_total:,.2f}"
            } for i in invoices]
            
            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

        else:
            st.info(_("No invoices found for this period."))

    finally:
        session.close()

# Start the view
render_history_view()