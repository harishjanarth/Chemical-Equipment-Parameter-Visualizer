import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# CSV ANALYSIS FUNCTION

def analyze_equipment_csv(path):
    df = pd.read_csv(path)

    total = len(df)
    avg_flow = df["Flowrate"].mean()
    avg_pressure = df["Pressure"].mean()
    avg_temp = df["Temperature"].mean()

    # Type distribution
    type_dist = df["Type"].value_counts().to_dict()

     #Correlation Matrix
    corr = df[["Flowrate", "Pressure", "Temperature"]].corr()
    corr_matrix = corr.round(3).to_dict()

    #Outlier Detection using Z-score
    df["z_flow"] = (df["Flowrate"] - avg_flow) / df["Flowrate"].std()
    df["z_pressure"] = (df["Pressure"] - avg_pressure) / df["Pressure"].std()
    df["z_temp"] = (df["Temperature"] - avg_temp) / df["Temperature"].std()

    outliers = df[
        (df["z_flow"].abs() >= 2) |
        (df["z_pressure"].abs() >= 2) |
        (df["z_temp"].abs() >= 2)
    ]

    outlier_rows = outliers.to_dict(orient="records")

    # Type-wise averages
    typewise = (
        df.groupby("Type")[["Flowrate", "Pressure", "Temperature"]]
        .mean()
        .round(2)
        .to_dict(orient="index")
    )

    summary = {
        "total_equipment": int(total),
        "avg_flowrate": float(avg_flow),
        "avg_pressure": float(avg_pressure),
        "avg_temperature": float(avg_temp),
        "type_distribution": type_dist,

        "correlation": corr_matrix,
        "outliers": outlier_rows,
        "typewise_averages": typewise,
    }

    return summary, df


#pie chart
def generate_pie_chart(type_distribution):
    labels = list(type_distribution.keys())
    values = list(type_distribution.values())

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    ax.set_title("Equipment Type Distribution")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    buffer.seek(0)
    plt.close(fig)

    return buffer


#pdf generation
def generate_pdf_report(summary):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 80

    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(width / 2, y, "Equipment Summary Report")
    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Key Statistics:")
    y -= 25
    pdf.setFont("Helvetica", 12)

    stats = [
        ("Total Equipment", summary.get("total_equipment")),
        ("Average Flowrate", round(summary.get("avg_flowrate"), 2)),
        ("Average Pressure", round(summary.get("avg_pressure"), 2)),
        ("Average Temperature", round(summary.get("avg_temperature"), 2)),
    ]

    for title, val in stats:
        pdf.drawString(70, y, f"{title}: {val}")
        y -= 20

    y -= 20
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Equipment Type Distribution:")
    y -= 25
    pdf.setFont("Helvetica", 12)

    type_distribution = summary.get("type_distribution", {})
    for k, v in type_distribution.items():
        pdf.drawString(70, y, f"{k}: {v}")
        y -= 18

   
    y -= 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Type Distribution Pie Chart:")
    y -= 20

    pie_buffer = generate_pie_chart(type_distribution)
    pie_img = ImageReader(pie_buffer)

    pdf.drawImage(pie_img, 150, y - 250, width=250, height=250)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
