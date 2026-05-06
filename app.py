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

miktar = st.number_input(
    "Kullanim Miktari (kg/L)",
    min_value=0.0,
    value=1.0
)

calisan = st.text_input(
    "Calisan Adi"
)

departman = st.text_input(
    "Departman"
)

degerlendiren = st.text_input(
    "Degerlendiren Kisi"
)

havalandirma = st.checkbox(
    "Havalandırma Var"
)

resp = st.checkbox(
    "Respiratör Kullanılıyor"
)
eldiven = st.checkbox(
    "Kimyasal Eldiven"
)

gozluk = st.checkbox(
    "Koruyucu Gozluk"
)

yuzsiperi = st.checkbox(
    "Yuz Siperi"
)

koruyucu = st.checkbox(
    "Koruyucu Kiyafet"
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

    if miktar >= 50:
        risk += 3

    elif miktar >= 10:
        risk += 2

    elif miktar >= 1:
        risk += 1

    if not havalandirma:
        risk += 2

    if not resp:
        risk += 2
    if not eldiven:
        risk += 1

    if not gozluk:
        risk += 1

    if not koruyucu:
        risk += 1
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

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(190, 12, "COSHH RISK REPORT", ln=True)

    pdf.ln(10)

    pdf.set_font("Helvetica", "", 12)

    pdf.cell(60,10,"Chemical:",0,0)
    pdf.cell(120,10,temizle(secili),0,1)

    pdf.cell(60,10,"CAS No:",0,0)
    pdf.cell(120,10,temizle(cas),0,1)

    pdf.cell(60,10,"H Codes:",0,0)
    pdf.cell(120,10,temizle(hkod),0,1)

    pdf.cell(60,10,"Process:",0,0)
    pdf.cell(120,10,temizle(islem),0,1)

    pdf.cell(60,10,"Duration:",0,0)
    pdf.cell(120,10,f"{sure} hours",0,1)

    pdf.cell(60,10,"Amount:",0,0)
    pdf.cell(120,10,f"{miktar}",0,1)

    pdf.cell(60,10,"Employee:",0,0)
    pdf.cell(120,10,temizle(calisan),0,1)

    pdf.cell(60,10,"Department:",0,0)
    pdf.cell(120,10,temizle(departman),0,1)

    pdf.cell(60,10,"Evaluator:",0,0)
    pdf.cell(120,10,temizle(degerlendiren),0,1)

    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(190,10,"PPE",ln=True)

    pdf.set_font("Helvetica","",12)

    pdf.cell(190,10,f"Respirator: {resp}",ln=True)

    pdf.cell(190,10,f"Gloves: {eldiven}",ln=True)

    pdf.cell(190,10,f"Goggles: {gozluk}",ln=True)

    pdf.cell(190,10,f"Face Shield: {yuzsiperi}",ln=True)

    pdf.cell(190,10,f"Protective Clothing: {koruyucu}",ln=True)

    pdf.ln(5)

    pdf.set_font("Helvetica","B",14)

    pdf.cell(190,10,"Risk Result",ln=True)

    pdf.set_font("Helvetica","",12)

    pdf.cell(190,10,temizle(sonuc),ln=True)

    pdf.ln(5)

    pdf.set_font("Helvetica","B",14)

    pdf.cell(190,10,"Recommendations",ln=True)

    pdf.set_font("Helvetica","",12)

    for o in oneriler:

        pdf.multi_cell(
            190,
            10,
            f"- {temizle(o)}"
        )

    filename = "COSHH_REPORT.pdf"

    pdf.output(filename)

    with open(filename,"rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
