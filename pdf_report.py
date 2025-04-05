from fpdf import FPDF

class PDFReport(FPDF):
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_title(title)

    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, self.title, border=False, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_section(self, heading: str, content: str):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, heading, ln=True)
        self.ln(5)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 10, content)
        self.ln(10)

# Example usage
if __name__ == "__main__":
    pdf = PDFReport("Sample Report")
    pdf.add_section("Introduction", "This is a sample PDF report generated using FPDF.")
    pdf.add_section("Details", "Here are some details about the report.")
    pdf.output("report.pdf")
