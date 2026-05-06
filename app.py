
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

def temizle(text):

    text = str(text)

    degisim = {
        "İ":"I","ı":"i",
        "Ş":"S","ş":"s",
        "Ğ":"G","ğ":"g",
        "Ü":"U","ü":"u",
        "Ö":"O","ö":"o",
        "Ç":"C","ç":"c"
    }

    for k,v in degisim.items():
        text = text.replace(k,v)

    return text

st.set_page_config(
    page_title="COSHH",
    layout="wide"
)

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(FILE, sheet_name="DB")

df.columns = df.columns.astype(str)

st.title("COSHH Risk Sistemi")

kimyasallar = df["Kimyasal Adı"].dropna().unique()

secili = st.selectbox(
    "Kimyasal Seç",
    sorted(kimyasallar)
)

satir = df[df["Kimyasal Adı"] == secili].iloc[0]

cas = str(satir.get("CAS No","-"))
hkod = str(satir.get("H Kodları","-"))
fiziksel = str(satir.get("Fiziksel Hal","-"))

st.write("CAS:", cas)
st.write("H Kodları:", hkod)

st.divider()

islem = st.selectbox(
    "İşlem",
    [
        "Karıştırma",
        "Transfer",
        "Püskürtme",
        "Isıtma"
    ]
)

sure = st.slider(
    "Süre",
    0,
    8,
    1
)

havalandirma = st.checkbox(
    "Havalandırma Var"
)

resp = st.checkbox(
    "Respiratör Kullanılıyor"
)

if st.button("COSHH Değerlendir"):

    risk = 0

    if "H350" in hkod:
        risk += 5

    if "H340" in hkod:
        risk += 5

    if islem == "Püskürtme":
        risk += 3

    if sure >= 4:
        risk += 2

    if not havalandirma:
        risk += 2

    if not resp:
        risk += 2

    if risk <= 3:
        sonuc = "DUSUK RISK"

    elif risk <= 7:
        sonuc = "ORTA RISK"

    else:
        sonuc = "YUKSEK RISK"

    st.header(sonuc)

    oneriler = []

    if not havalandirma:
        oneriler.append("Lokal havalandirma onerilir")

    if not resp:
        oneriler.append("Respirator onerilir")

    for o in oneriler:
        st.write("•", o)

    # PDF

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Helvetica", size=14)

    pdf.cell(190,10,"COSHH REPORT",ln=True)

    pdf.cell(190,10,f"Date: {datetime.now()}",ln=True)

    pdf.ln(5)

    pdf.multi_cell(
        190,
        10,
        f"Chemical: {temizle(secili)}"
    )

    pdf.multi_cell(
        190,
        10,
        f"CAS: {temizle(cas)}"
    )

    pdf.multi_cell(
        190,
        10,
        f"H Codes: {temizle(hkod)}"
    )

    pdf.multi_cell(
        190,
        10,
        f"Risk: {temizle(sonuc)}"
    )

    pdf.ln(5)

    pdf.cell(190,10,"Recommendations",ln=True)

    for o in oneriler:

        pdf.multi_cell(
            190,
            10,
            temizle(o)
        )

    filename = "COSHH_REPORT.pdf"

    pdf.output(filename)

    with open(filename,"rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )

