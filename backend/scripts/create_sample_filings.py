from pathlib import Path
from fpdf import FPDF

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FILINGS = [
    {
        "filename": "AAPL_10K_2024.pdf",
        "pages": [
            (
                "Item 1A. Risk Factors",
                "Apple Inc. Form 10-K (Fiscal Year Ended September 28, 2024)\\n"
                "Section: Item 1A. Risk Factors\\n\\n"
                "Macroeconomic and Industry Risks: Apple operations and performance depend significantly on "
                "global and regional economic conditions. Adverse macroeconomic conditions, including inflation, "
                "slower growth, and currency fluctuations, have impacted and may continue to impact consumer "
                "spending on iPhone, Mac, and iPad hardware products.\\n\\n"
                "Supply Chain and Manufacturing Concentration: Substantially all of Apple hardware products "
                "are manufactured by outsourcing partners located primarily in Asia, including China, India, "
                "and Vietnam. A significant concentration of manufacturing creates supply chain disruption "
                "risks from geopolitical tensions, trade restrictions, tariffs, or natural disasters.\\n\\n"
                "Legal and Regulatory Compliance Risks: Apple is subject to complex and changing laws "
                "worldwide, including the European Union Digital Markets Act (DMA) and antitrust litigation, "
                "which may require modifications to the App Store business model and reduce Services fee revenue."
            ),
            (
                "Item 7. MD&A - Operating Results",
                "Apple Inc. Form 10-K (Fiscal Year Ended September 28, 2024)\\n"
                "Section: Item 7. Management Discussion and Analysis of Financial Condition\\n\\n"
                "Consolidated Financial Highlights (in billions, except percentages):\\n"
                "- Fiscal 2024 Total Net Sales (Revenue): $391.04 billion\\n"
                "- Fiscal 2023 Total Net Sales (Revenue): $383.29 billion\\n"
                "- Fiscal 2024 Operating Income: $123.22 billion\\n"
                "- Fiscal 2023 Operating Income: $114.30 billion\\n"
                "- Fiscal 2024 Net Income: $93.74 billion\\n\\n"
                "Commentary on Revenue and Margins: Total net sales increased 2.02% year-over-year in FY2024, "
                "driven primarily by strong growth in Services revenue ($96.17 billion in FY2024 vs $85.20 billion "
                "in FY2023, up 12.88%). Gross margin percentage increased to 46.21% in FY2024 compared to 44.13% "
                "in FY2023 due to a favorable shift mix toward higher-margin Services and cost savings, partially "
                "offset by foreign exchange headwinds."
            ),
        ],
    },
    {
        "filename": "MSFT_10K_2024.pdf",
        "pages": [
            (
                "Item 1A. Risk Factors",
                "Microsoft Corporation Form 10-K (Fiscal Year Ended June 30, 2024)\\n"
                "Section: Item 1A. Risk Factors\\n\\n"
                "Cloud Infrastructure and AI Investment Risks: Microsoft is making massive capital expenditures "
                "in cloud datacenters, GPUs, and artificial intelligence infrastructure. If customer adoption "
                "of Azure AI services grows slower than anticipated, or if energy and chip supply constraints "
                "limit datacenter expansion, operating margins may be compressed by higher depreciation expenses.\\n\\n"
                "Cybersecurity and Platform Reliability Risks: As a leading cloud provider, Microsoft faces "
                "persistent nation-state and criminal cyberattacks. Any significant security breach or service "
                "outage across Azure or Microsoft 365 could harm enterprise customer trust and result in "
                "regulatory penalties.\\n\\n"
                "Competition and Antitrust Scrutiny: Intense competition in cloud computing, productivity "
                "software, and generative AI, alongside regulatory scrutiny of partnerships and acquisitions "
                "(such as Activision Blizzard and OpenAI investments), may restrict strategic flexibility."
            ),
            (
                "Item 7. MD&A - Operating Results",
                "Microsoft Corporation Form 10-K (Fiscal Year Ended June 30, 2024)\\n"
                "Section: Item 7. Management Discussion and Analysis of Financial Condition\\n\\n"
                "Consolidated Financial Highlights (in billions, except percentages):\\n"
                "- Fiscal 2024 Total Revenue: $245.12 billion\\n"
                "- Fiscal 2023 Total Revenue: $211.92 billion\\n"
                "- Fiscal 2024 Operating Income: $109.43 billion\\n"
                "- Fiscal 2023 Operating Income: $88.52 billion\\n"
                "- Fiscal 2024 Net Income: $88.14 billion\\n\\n"
                "Commentary on Revenue and Margins: Total revenue increased 15.67% year-over-year in FY2024, "
                "led by Intelligent Cloud revenue growth and Azure AI adoption. Operating income increased "
                "23.62% as cloud scale efficiencies outpaced increased capital expenditure depreciation from "
                "AI infrastructure investments."
            ),
        ],
    },
]


def generate_pdfs() -> None:
    for filing in FILINGS:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        for section_title, body in filing["pages"]:
            pdf.add_page()
            pdf.set_font("Helvetica", style="B", size=13)
            pdf.cell(0, 10, section_title, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 7, body)
        out_path = DATA_DIR / filing["filename"]
        pdf.output(str(out_path))
        print(f"Created {out_path.name} ({len(filing['pages'])} pages)")


if __name__ == "__main__":
    generate_pdfs()