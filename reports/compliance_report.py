import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import datetime

def generate_excel_report(comparison_results):
    """
    Generates an Excel report from comparison_results.
    Returns the filename.
    """
    data = []

    for result in comparison_results:
        bank_num = result["bank_section_number"]
        status = result["compliance_status"]
        top_matches = result.get("top_matches", [])

        # Create a row for each Bank section
        row = {
            "Bank Section": bank_num,
            "Compliance Status": status,
        }

        # Include top 3 matches
        for i, match in enumerate(top_matches, start=1):
            row[f"Top {i} Vendor Section"] = match["vendor_para_number"]
            row[f"Top {i} Similarity Score"] = round(match["similarity_score"], 3)

        data.append(row)

    df = pd.DataFrame(data)

    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"compliance_report_{timestamp}.xlsx"

    # Create Excel writer
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Compliance Report")
        ws = writer.sheets["Compliance Report"]

        # Apply color coding based on Compliance Status
        for row_idx, status in enumerate(df["Compliance Status"], start=2):  # start=2 because header
            if status == "Fully Compliant":
                fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Green
            elif status == "Partially Compliant":
                fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # Yellow
            else:
                fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Red

            ws[f"B{row_idx}"].fill = fill  # Column B is Compliance Status

    return filename
