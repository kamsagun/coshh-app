import os
import random
from datetime import datetime

import pandas as pd
import streamlit as st
from fpdf import FPDF


FILE = "020526 COSHH MAKRO.xlsm"
LOW_RISK_THRESHOLD = 10
MEDIUM_RISK_THRESHOLD = 20
GHS_COLUMNS = 5
QUANTITY_RISK_THRESHOLD = 100
DEMO_RECORDS = [
    {"Kimyasal Adı": "Aseton", "CAS No": "67-64-1", "H Kodları": "H225 H319", "Fiziksel Hal": "Sıvı"},
    {"Kimyasal Adı": "Metanol", "CAS No": "67-56-1", "H Kodları": "H301 H311 H331", "Fiziksel Hal": "Sıvı"},
    {"Kimyasal Adı": "Benzen", "CAS No": "71-43-2", "H Kodları": "H350 H340", "Fiziksel Hal": "Sıvı"},
    {"Kimyasal Adı": "Formaldehit", "CAS No": "50-00-0", "H Kodları": "H350 H341 H314", "Fiziksel Hal": "Sıvı"},
]


def temizle(text):
    if text is None:
        return ""
    text = str(text)
    degisim = {
        "İ": "I",
        "ı": "i",
        "Ş": "S",
        "ş": "s",
        "Ğ": "G",
        "ğ": "g",
        "Ü": "U",
        "ü": "u",
        "Ö": "O",
        "ö": "o",
        "Ç": "C",
        "ç": "c",
    }
    for k, v in degisim.items():
        text = text.replace(k, v)
    return text


def load_data():
    if os.path.exists(FILE):
        try:
            db = pd.read_excel(FILE, sheet_name="DB")
            db.columns = db.columns.astype(str)
            needed = ["Kimyasal Adı", "CAS No", "H Kodları", "Fiziksel Hal"]
            if all(col in db.columns for col in needed):
                return db, "Excel verisi"
        except Exception:
            st.warning("Excel verisi okunamadı, demo verisine geçildi.")

    demo_df = pd.DataFrame(DEMO_RECORDS)
    demo_df.columns = demo_df.columns.astype(str)
    return demo_df, "Demo verisi"


def ghs_image_for_code(code):
    mapping = {
        "GHS02": "ghs02.png",
        "GHS05": "ghs05.png",
        "GHS06": "ghs06.png",
        "GHS07": "ghs07.png",
        "GHS08": "ghs08.png",
    }
    image = mapping.get(code)
    if image and os.path.exists(image):
        return image
    return None


st.set_page_config(page_title="COSHH Mobile Demo", layout="centered", initial_sidebar_state="collapsed")

st.title("COSHH Mobile Demo")
st.caption("Play Store önizlemesi için hızlı demo sürümü")

if os.path.exists("logo.png"):
    st.image("logo.png", width=140)

with st.sidebar:
    st.subheader("Demo Notu")
    st.write(
        "Bu sürüm, müşterilere mobil önizleme göstermek için hazırlanmıştır. "
        "Veritabanı geliştirmesi sonraki adımda yapılabilir."
    )


# DATA
df, data_source = load_data()
kimyasallar = df["Kimyasal Adı"].dropna().unique()

st.subheader("Firma ve Kimyasal")
customer_name = st.text_input("Müşteri / Firma", value="Demo Customer")
secili = st.selectbox("Kimyasal Seç", sorted(kimyasallar))

satir = df[df["Kimyasal Adı"] == secili].iloc[0]
cas = str(satir.get("CAS No", "-"))
hkod = str(satir.get("H Kodları", "-"))
fiziksel = str(satir.get("Fiziksel Hal", "-"))

if "SDS gerekir" in hkod:
    hkod = ""

otomatik_h = {
    "AKRILONITRIL": "H350 H340 H330",
    "FORMALDEHIT": "H350 H341 H314",
    "BENZEN": "H350 H340",
    "TOLUEN": "H373",
    "KSILEN": "H373",
    "METANOL": "H301 H311 H331",
    "ASETON": "H225 H319",
}

if not hkod.strip():
    buyuk = temizle(secili).upper()
    if buyuk in otomatik_h:
        hkod = otomatik_h[buyuk]

st.subheader("Çalışma Bilgileri")
islem = st.selectbox("İşlem Türü", ["Karıştırma", "Transfer", "Püskürtme", "Isıtma", "Dolum", "Temizlik"])
sure = st.slider("Çalışma Süresi (saat)", 1, 12, 1)
amount = st.number_input("Miktar", min_value=0.0, value=1.0)
maruziyet = st.selectbox("Maruziyet", ["Düşük", "Orta", "Yüksek"])

st.subheader("Çalışma Ortamı")
kapali_alan = st.checkbox("Kapalı Alan")
lev = st.checkbox("LEV Sistemi")
sicak_islem = st.checkbox("Sıcak İşlem")

st.subheader("Kullanılan PPE")
resp = st.checkbox("Respiratör")
eldiven = st.checkbox("Kimyasal Eldiven")
gozluk = st.checkbox("Koruyucu Gözlük")

st.divider()
st.write("Veri Kaynağı:", data_source)
st.write("Müşteri:", customer_name)
st.write("CAS:", cas)
st.write("H Kodları:", hkod)
st.write("Fiziksel Hal:", fiziksel)

if st.button("COSHH Değerlendir", use_container_width=True):
    rapor_no = f"COSHH-{datetime.now().year}-{random.randint(10000, 99999)}"

    risk = 0
    if "H350" in hkod:
        risk += 6
    if "H340" in hkod:
        risk += 5
    if "H330" in hkod:
        risk += 5
    if "H314" in hkod:
        risk += 4
    if "H373" in hkod:
        risk += 3
    if "H225" in hkod:
        risk += 3
    if islem == "Püskürtme":
        risk += 4
    if sure >= 8:
        risk += 3
    if amount >= QUANTITY_RISK_THRESHOLD:
        risk += 3
    if maruziyet == "Yüksek":
        risk += 4
    if kapali_alan:
        risk += 3
    if not lev:
        risk += 2
    if sicak_islem:
        risk += 2
    if not resp:
        risk += 2

    if risk <= LOW_RISK_THRESHOLD:
        sonuc = "DUSUK RISK"
    elif risk <= MEDIUM_RISK_THRESHOLD:
        sonuc = "ORTA RISK"
    else:
        sonuc = "YUKSEK RISK"

    hazard_group = "A"
    if "H350" in hkod or "H340" in hkod:
        hazard_group = "E"
    elif "H330" in hkod:
        hazard_group = "D"
    elif "H314" in hkod:
        hazard_group = "C"
    elif "H373" in hkod:
        hazard_group = "B"

    if hazard_group == "E":
        kontrol = "Control Approach 4"
    elif hazard_group == "D":
        kontrol = "Control Approach 3"
    elif hazard_group == "C":
        kontrol = "Control Approach 2"
    else:
        kontrol = "Control Approach 1"

    ghs = []
    if "H314" in hkod:
        ghs.append("GHS05")
    if "H315" in hkod or "H319" in hkod:
        ghs.append("GHS07")
    if "H330" in hkod:
        ghs.append("GHS06")
    if "H340" in hkod or "H350" in hkod or "H373" in hkod:
        ghs.append("GHS08")
    if "H225" in hkod:
        ghs.append("GHS02")

    if sonuc == "DUSUK RISK":
        st.success(sonuc)
    elif sonuc == "ORTA RISK":
        st.warning(sonuc)
    else:
        st.error(sonuc)

    st.subheader("Hazard Group")
    st.write(hazard_group)
    st.subheader("Control Approach")
    st.write(kontrol)

    st.subheader("GHS Pictograms")
    cols = st.columns(GHS_COLUMNS)
    for i, g in enumerate(ghs):
        with cols[i % GHS_COLUMNS]:
            image_path = ghs_image_for_code(g)
            if image_path:
                st.image(image_path, width=90)
            else:
                st.info(g)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(190, 12, temizle("COSHH PROFESSIONAL REPORT"), 0, 1, "C")
    pdf.ln(10)

    bilgiler = [
        ("Report No", rapor_no),
        ("Customer", customer_name),
        ("Chemical", secili),
        ("CAS No", cas),
        ("H Codes", hkod),
        ("Physical State", fiziksel),
        ("Process", islem),
        ("Duration", str(sure)),
        ("Amount", str(amount)),
        ("Exposure", maruziyet),
        ("Hazard Group", hazard_group),
        ("Risk Result", sonuc),
        ("Control Approach", kontrol),
        ("PPE - Respirator", "Yes" if resp else "No"),
        ("PPE - Gloves", "Yes" if eldiven else "No"),
        ("PPE - Goggles", "Yes" if gozluk else "No"),
    ]

    for label, value in bilgiler:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(60, 8, temizle(label + ":"), 0, 0)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(120, 8, temizle(value), 0, 1)

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(190, 10, temizle("GHS Pictograms"), 0, 1)
    pdf.set_font("Helvetica", "", 11)
    for g in ghs:
        pdf.cell(190, 8, temizle(g), 0, 1)

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 8, temizle(str(datetime.now())), 0, 1)

    filename = "COSHH_REPORT.pdf"
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button("PDF İndir", f, file_name=filename, use_container_width=True)
