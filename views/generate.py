import streamlit as st
import random
import calendar
import re
import db
import time
from datetime import date
from faker import Faker
from sqlalchemy import extract
from core.i18n import _

# Initialize Faker for random customer names
fake = Faker(['es_MX', 'es_ES'])

def get_valid_dates(month, year):
    """Returns all dates for a given month and year."""
    num_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, num_days + 1)]

def render_generate_view():
    st.header(_("Detailed Invoice Generator"))

    # Localized months
    MONTHS_LIST = [
        "", _("January"), _("February"), _("March"), _("April"), _("May"), _("June"),
        _("July"), _("August"), _("September"), _("October"), _("November"), _("December")
    ]

    # --- 1. PERIOD & BRANCH SELECTION ---
    with st.container(border=True):
        st.subheader(_("Period & Branch Selection"))
        col_branch, col_month, col_year = st.columns(3)
        
        company_id = st.session_state.get('company_id')
        db_session = db.SessionLocal()
        try:
            available_branches = db_session.query(db.Branch).filter(db.Branch.company_id == company_id).all()
            branch_map = {b.name: b.id for b in available_branches}
        finally:
            db_session.close()

        if not branch_map:
            st.error(_("No branches found. Please create one in Administration."))
            st.stop()

        selected_branch_name = col_branch.selectbox(_("Target Branch"), list(branch_map.keys()))
        target_branch_id = branch_map[selected_branch_name]
        
        selected_month = col_month.selectbox(
            _("Month to Generate"), 
            range(1, 13), 
            index=date.today().month - 1, 
            format_func=lambda x: MONTHS_LIST[x]
        )
        selected_year = col_year.selectbox(_("Year"), [2025, 2026], index=1)

    # --- 2. DATABASE STATUS CHECK ---
    current_session = db.SessionLocal()
    try:
        # Check for existing invoices
        existing_count = current_session.query(db.Invoice).filter(
            db.Invoice.branch_id == target_branch_id,
            extract('month', db.Invoice.date) == selected_month,
            extract('year', db.Invoice.date) == selected_year
        ).count()

        if existing_count > 0:
            st.warning(_("Warning: {0} invoices already exist for this period.", existing_count))
            
            with st.expander(_("Danger Zone: Clear History to Regenerate")):
                st.write(_("To generate new invoices, you must first delete the existing ones for this month."))
                if st.button(_("Delete {0} Invoices", existing_count), type="primary", use_container_width=True):
                    current_session.query(db.Invoice).filter(
                        db.Invoice.branch_id == target_branch_id,
                        extract('month', db.Invoice.date) == selected_month,
                        extract('year', db.Invoice.date) == selected_year
                    ).delete(synchronize_session=False)
                    current_session.commit()
                    st.toast(_("History cleared successfully!"), icon="🗑️")
                    time.sleep(1)
                    st.rerun()
            st.stop()

        # --- 3. INVENTORY CHECK ---
        stock_inventory = current_session.query(db.Stock).filter(
            db.Stock.branch_id == target_branch_id,
            db.Stock.month == selected_month,
            db.Stock.year == selected_year
        ).all()

        if not stock_inventory:
            st.info(_("No inventory loaded for {0} this month. Please upload stock first.", selected_branch_name))
        else:
            total_stock_value = sum(item.qty * item.price for item in stock_inventory)
            st.success(_("Available Inventory: L. {0}", f"{total_stock_value:,.2f}"))

            with st.container(border=True):
                st.subheader(_("Billing Parameters"))
                col_cust, col_corr, col_max = st.columns([2, 2, 1])
                
                customer_input = col_cust.text_input(_("Customer (Empty = Random)"), placeholder=_("e.g., Final Consumer"))
                start_correlative = col_corr.text_input(_("Starting Correlative"), placeholder="000-001-01-00000001")
                max_items = col_max.slider(_("Max Items per Invoice"), 1, 12, 5)
                
                days_of_week = [_("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday"), _("Sunday")]
                allowed_days = st.multiselect(_("Allowed Days"), days_of_week, default=days_of_week[:6])

            # --- 4. EXECUTION ---
            if st.button(_("Start Random Generation"), use_container_width=True, type="primary"):
                # VALIDATIONS
                correlative_pattern = r"^\d{3}-\d{3}-\d{2}-\d{8}$"
                if not re.match(correlative_pattern, start_correlative):
                    st.error(_("Invalid correlative format. Expected: 000-000-00-00000000"))
                    st.stop()

                if not allowed_days:
                    st.error(_("Please select at least one day of the week."))
                    st.stop()

                # PROCESS
                all_dates = get_valid_dates(selected_month, selected_year)
                day_map = {days_of_week[i]: i for i in range(7)}
                allowed_indices = [day_map[d] for d in allowed_days]
                valid_dates = [d for d in all_dates if d.weekday() in allowed_indices]

                # Create Invoice Pool
                pool = []
                for item in stock_inventory:
                    for _idx in range(item.qty):
                        pool.append({'desc': item.description, 'price': item.price, 'tax': item.tax})
                random.shuffle(pool)

                # Correlative parsing
                parts = start_correlative.split('-')
                prefix = "-".join(parts[:-1])
                counter = int(parts[-1])
                
                gen_count = 0
                total_initial_items = len(pool)
                progress_bar = st.progress(0)

                while pool:
                    batch_size = random.randint(1, min(max_items, len(pool)))
                    chunk = [pool.pop() for _idx in range(batch_size)]
                    
                    ex, gr, iv = 0.0, 0.0, 0.0
                    invoice_items = []

                    for i in chunk:
                        if i['tax'] == 0:
                            ex += i['price']
                            p_u = i['price']
                        else:
                            p_net = round(i['price'] / 1.15, 2)
                            p_isv = round(i['price'] - p_net, 2)
                            gr += p_net
                            iv += p_isv
                            p_u = p_net

                        invoice_items.append(db.InvoiceItem(description=i['desc'], quantity=1, unit_price=p_u, tax_pct=i['tax']))

                    new_inv = db.Invoice(
                        invoice_no=f"{prefix}-{str(counter).zfill(8)}",
                        customer_name=customer_input if customer_input else fake.name(),
                        date=random.choice(valid_dates),
                        exempt_total=round(ex, 2), taxed15_total=round(gr, 2),
                        isv15_total=round(iv, 2), grand_total=round(ex + gr + iv, 2),
                        branch_id=target_branch_id
                    )
                    for item in invoice_items: new_inv.items.append(item)

                    current_session.add(new_inv)
                    counter += 1
                    gen_count += 1
                    progress_bar.progress(1.0 - (len(pool) / total_initial_items))

                current_session.commit()
                st.balloons()
                st.toast(_("Successfully generated {0} invoices!", gen_count), icon="⚡")
                time.sleep(2)
                st.rerun()

    finally:
        current_session.close()

render_generate_view()