import streamlit as st
import pandas as pd
import db
import time  # Para permitir que las notificaciones se vean antes del rerun
from datetime import date
from core.i18n import _

def render_stock_view():
    """
    Renders the Inventory Management view.
    Includes bulk upload with auto-reset, ISV calculations, and period filtering.
    """
    # 1. INITIALIZE PERSISTENT STATE
    # This key allows us to "reset" the file uploader after a successful save
    if "uploader_id" not in st.session_state:
        st.session_state["uploader_id"] = 0

    st.header(_("Inventory Management"))

    # Localized month names for the selectbox
    MONTHS_LIST = [
        "", _("January"), _("February"), _("March"), _("April"), _("May"), _("June"),
        _("July"), _("August"), _("September"), _("October"), _("November"), _("December")
    ]

    # --- SECTION 1: FILTERS ---
    with st.container(border=True):
        st.subheader(_("Query and Upload Filters"))
        col1, col2, col3 = st.columns(3)
        
        session_db = db.SessionLocal()
        try:
            company_id = st.session_state.get('company_id')
            branches_db = session_db.query(db.Branch).filter(db.Branch.company_id == company_id).all()
            branch_map = {b.name: b.id for b in branches_db}
        finally:
            session_db.close()

        if not branch_map:
            st.error(_("No branches found. Please create one in Administration."))
            st.stop()

        target_branch_name = col1.selectbox(_("Branch"), list(branch_map.keys()), index=0)
        target_branch_id = branch_map[target_branch_name]
        
        target_month = col2.selectbox(
            _("Month"), 
            range(1, 13), 
            index=date.today().month - 1, 
            format_func=lambda x: MONTHS_LIST[x]
        )
        target_year = col3.selectbox(_("Year"), [2025, 2026], index=1)

    st.divider()

    # --- SECTION 2: UPLOAD (WITH RESET LOGIC) ---
    with st.expander(_("Upload New Inventory (CSV/Excel)")):
        # The key changes every time a successful upload happens, clearing the file
        uploader_key = f"stock_uploader_{st.session_state['uploader_id']}"
        uploaded_file = st.file_uploader(_("Select file"), type=['csv', 'xlsx'], key=uploader_key)
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                df_upload = df_upload.dropna(how='all')
                st.write(_("Preview of the data to be uploaded:"))
                st.dataframe(df_upload.head(), use_container_width=True)
                
                # CONFIRM BUTTON
                if st.button(_("Confirm Upload to {0}", target_branch_name), type="primary", use_container_width=True):
                    session = db.SessionLocal()
                    try:
                        # 1. Clean previous records for this period
                        session.query(db.Stock).filter(
                            db.Stock.branch_id == target_branch_id,
                            db.Stock.month == target_month,
                            db.Stock.year == target_year
                        ).delete()
                        
                        # 2. Bulk Insert (Using 'idx' to avoid 'UnboundLocalError' with '_')
                        for idx, row in df_upload.iterrows():
                            new_item = db.Stock(
                                description=row['Description'],
                                qty=int(row['Quantity']),
                                price=float(row['Unit Price']),
                                tax=int(row['Tax']),
                                month=target_month,
                                year=target_year,
                                branch_id=target_branch_id
                            )
                            session.add(new_item)
                        
                        session.commit()
                        
                        # 3. SUCCESS TRIGGER: Show notification, wait, then refresh
                        st.session_state["uploader_id"] += 1
                        st.toast(_("Inventory updated successfully!"), icon="✅",duration="infinite")
                        
                        # Small delay so the toast notification is visible in the top-right
                        time.sleep(1) 
                        st.rerun()
                        
                    except Exception as e:
                        session.rollback()
                        st.error(_("Error during upload: {0}", str(e)))
                    finally:
                        session.close()
            except Exception as e:
                st.error(_("File reading error: {0}", str(e)))

    st.divider()

    # --- SECTION 3: VISUALIZATION AND CALCULATIONS ---
    st.subheader(_("Inventory List: {0} ({1} {2})", target_branch_name, MONTHS_LIST[target_month], target_year))

    session = db.SessionLocal()
    try:
        current_stock = session.query(db.Stock).filter(
            db.Stock.branch_id == target_branch_id,
            db.Stock.month == target_month,
            db.Stock.year == target_year
        ).all()
        
        if current_stock:
            tab_raw, tab_result = st.tabs([_("Database View"), _("Results with Tax (ISV)")])
            
            raw_list, result_list = [], []
            t_exempt, t_taxable_net, t_isv = 0.0, 0.0, 0.0

            for s in current_stock:
                line_total = round(s.qty * s.price, 2)
                
                if s.tax > 0:
                    net_value = round(line_total / (1 + s.tax/100), 2)
                    isv_value = round(line_total - net_value, 2)
                    t_taxable_net += net_value
                    t_isv += isv_value
                else:
                    net_value = line_total
                    isv_value = 0.0
                    t_exempt += net_value

                raw_list.append({
                    "Description": s.description, 
                    "Qty": s.qty, 
                    "Price": s.price, 
                    "Tax": s.tax
                })
                
                result_list.append({
                    _("Description"): s.description, 
                    _("Qty"): s.qty, 
                    _("Final Price"): f"L. {s.price:,.2f}", 
                    _("Tax (ISV)"): f"L. {isv_value:,.2f}", 
                    _("Total"): f"L. {line_total:,.2f}"
                })

            with tab_raw:
                st.dataframe(pd.DataFrame(raw_list), use_container_width=True, hide_index=True)
            with tab_result:
                st.dataframe(pd.DataFrame(result_list), use_container_width=True, hide_index=True)
                st.divider()
                c1, c2, c3 = st.columns(3)
                c1.metric(_("Net Subtotal"), f"L. {(t_exempt + t_taxable_net):,.2f}")
                c2.metric(_("Total Tax (ISV)"), f"L. {t_isv:,.2f}")
                c3.metric(_("GRAND TOTAL"), f"L. {(t_exempt + t_taxable_net + t_isv):,.2f}")
        else:
            st.info(_("No products registered for this period."))
    finally:
        session.close()

# Start the view logic
render_stock_view()