from fpdf import FPDF
import pandas as pd

# Lista global para nombres de meses en español
SPANISH_MONTHS = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

class DecomonsPDF(FPDF):
    def draw_invoice_page(self, invoice_obj, branch_name, month_index, year_val):
        self.add_page()
        
        # --- HEADER SECTION ---
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, f"{branch_name.upper()}", ln=True, align="C")
        
        # Period Display (Spanish Months)
        self.set_font("Arial", "B", 12)
        month_name = SPANISH_MONTHS[month_index]
        self.cell(0, 7, f"Periodo: {month_name} {year_val}", ln=True, align="C")
        
        self.set_font("Arial", "I", 10)
        self.cell(0, 5, "Comprobante de Venta Detallado", ln=True, align="C")
        self.ln(10)

        # --- INVOICE INFO SECTION ---
        self.set_fill_color(245, 245, 245)
        self.set_font("Arial", "B", 10)
        
        # Row 1: Invoice No & Date
        formatted_date = pd.to_datetime(invoice_obj.date).strftime('%d/%m/%Y')
        self.cell(95, 8, f"  Factura No: {invoice_obj.invoice_no}", border=1, fill=True)
        self.cell(95, 8, f"  Fecha: {formatted_date}", border=1, ln=True, fill=True)
        
        # Row 2: Customer Name
        self.set_font("Arial", "", 10)
        self.cell(190, 10, f"  Señor(a): {invoice_obj.customer_name}", border=1, ln=True)
        self.ln(5)

        # --- PRODUCT TABLE SECTION ---
        # Table Headers
        self.set_font("Arial", "B", 10)
        self.set_fill_color(230, 230, 230)
        self.cell(20, 8, "Cant.", border=1, align="C", fill=True)
        self.cell(100, 8, "Descripción", border=1, align="C", fill=True)
        self.cell(35, 8, "P. Unitario", border=1, align="C", fill=True)
        self.cell(35, 8, "Total", border=1, ln=True, align="C", fill=True)

        # Table Body
        self.set_font("Arial", "", 10)
        for item in invoice_obj.items:
            # Display unit price including tax if applicable (15%)
            display_unit_price = item.unit_price
            if item.tax_pct == 15:
                display_unit_price = round(item.unit_price * 1.15, 2)
            
            line_total = round(item.quantity * display_unit_price, 2)

            self.cell(20, 8, str(item.quantity), border=1, align="C")
            self.cell(100, 8, f" {item.description}", border=1)
            self.cell(35, 8, f"L. {display_unit_price:,.2f}", border=1, align="R")
            self.cell(35, 8, f"L. {line_total:,.2f}", border=1, ln=True, align="R")

        # Visual Padding (Empty rows to make it look like a real invoice pad)
        for _ in range(max(0, 10 - len(invoice_obj.items))):
            self.cell(20, 8, "", border=1)
            self.cell(100, 8, "", border=1)
            self.cell(35, 8, "", border=1)
            self.cell(35, 8, "", border=1, ln=True)

        # --- TOTALS SECTION ---
        self.ln(5)
        self.set_x(130)
        self.set_font("Arial", "B", 10)
        
        self.cell(35, 7, "Importe Exento:", border=0)
        self.cell(35, 7, f"L. {invoice_obj.exempt_total:,.2f}", border=0, ln=True, align="R")
        
        self.set_x(130)
        self.cell(35, 7, "Importe Gravado:", border=0)
        self.cell(35, 7, f"L. {invoice_obj.taxed15_total:,.2f}", border=0, ln=True, align="R")
        
        self.set_x(130)
        self.cell(35, 7, "I.S.V. 15%:", border=0)
        self.cell(35, 7, f"L. {invoice_obj.isv15_total:,.2f}", border=0, ln=True, align="R")
        
        self.set_x(130)
        self.set_font("Arial", "B", 12)
        self.set_fill_color(255, 255, 200) # Soft yellow for grand total
        self.cell(35, 10, "TOTAL L.", border="T", fill=True)
        self.cell(35, 10, f"{invoice_obj.grand_total:,.2f}", border="T", ln=True, align="R", fill=True)

def get_invoices_pdf_bytes(invoices_list, branch_name, month_index, year_val):
    """Main function to generate the PDF byte stream."""
    pdf_engine = DecomonsPDF()
    for inv in invoices_list:
        pdf_engine.draw_invoice_page(inv, branch_name, month_index, year_val)
    return pdf_engine.output()