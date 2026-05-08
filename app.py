# =====================================================
# IMPORTS
# =====================================================

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random

# =====================================================
# TURKCE KARAKTER TEMIZLEME
# =====================================================

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
        "ç": "c"
    }

    for k, v in degisim.items():

        text = text.replace(k, v)

    return text

# =====================================================
# SAYFA
# =====================================================

st.set_page_config(
    page_title="COSHH Professional",
    layout="wide"
)

st.title("COSHH Professional Risk Assessment")

# =====================================================
# EXCEL
# =====================================================

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(
    FILE,
    sheet_name="DB"
)

df.columns = df.columns.astype(str)

# =====================================================
# KIMYASAL SECIM
# =====================================================

kimyasallar = df["Kimyasal Adı"].dropna().unique()

secili = st.selectbox(
    "Kimyasal Seç",
    sorted(kimyasallar)
)

satir = df[
    df["Kimyasal Adı"] == secili
].iloc[0]

cas = str(
    satir.get("CAS No", "-")
)

hkod = str(
    satir.get("H Kodları", "-")
)

fiziksel = str(
    satir.get("Fiziksel Hal", "-")
)

# =====================================================
# SDS GEREKIR TEMIZLE
# =====================================================

if "SDS gerekir" in hkod:

    hkod = ""

# =====================================================
# OTOMATIK H KOD
# =====================================================

otomatik_h = {

    "AKRILONITRIL":
    "H350 H340 H330",

    "FORMALDEHIT":
    "H350 H341 H314",

    "BENZEN":
    "H350 H340",

    "TOLUEN":
    "H373",

    "KSILEN":
    "H373",

    "METANOL":
    "H301 H311 H331",

    "ASETON":
    "H225 H319"

}

if hkod == "":

    buyuk = temizle(
        secili
    ).upper()

    if buyuk in otomatik_h:

        hkod = otomatik_h[
            buyuk
        ]

# =====================================================
# FORM
# =====================================================

st.subheader(
    "Çalışma Bilgileri"
)

islem = st.selectbox(
    "İşlem Türü",
    [
        "Karıştırma",
        "Transfer",
        "Püskürtme",
        "Isıtma",
        "Dolum",
        "Temizlik"
    ]
)

sure = st.slider(
    "Çalışma Süresi",
    1,
    12,
    1
)

miktar = st.number_input(
    "Miktar",
    min_value=0.0,
    value=1.0
)

maruziyet = st.selectbox(
    "Maruziyet",
    [
        "Düşük",
        "Orta",
        "Yüksek"
    ]
)

# =====================================================
# ORTAM
# =====================================================

st.subheader(
    "Çalışma Ortamı"
)

kapali_alan = st.checkbox(
    "Kapalı Alan"
)

lev = st.checkbox(
    "LEV Sistemi"
)

sicak_islem = st.checkbox(
    "Sıcak İşlem"
)

# =====================================================
# PPE
# =====================================================

st.subheader(
    "Kullanılan PPE"
)

resp = st.checkbox(
    "Respiratör"
)

eldiven = st.checkbox(
    "Kimyasal Eldiven"
)

gozluk = st.checkbox(
    "Koruyucu Gözlük"
)

# =====================================================
# INFO
# =====================================================

st.divider()

st.write(
    "CAS:",
    cas
)

st.write(
    "H Kodları:",
    hkod
)

st.write(
    "Fiziksel Hal:",
    fiziksel
)

# =====================================================
# BUTTON
# =====================================================

if st.button(
    "COSHH Değerlendir"
):

    # =====================================================
    # RAPOR NO
    # =====================================================

    rapor_no = (
        "COSHH-"
        +
        str(datetime.now().year)
        +
        "-"
        +
        str(
            random.randint(
                10000,
                99999
            )
        )
    )

    # =====================================================
    # RISK
    # =====================================================

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

    if miktar >= 100:

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

    # =====================================================
    # SONUC
    # =====================================================

    if risk <= 10:

        sonuc = "DUSUK RISK"

    elif risk <= 20:

        sonuc = "ORTA RISK"

    else:

        sonuc = "YUKSEK RISK"

    # =====================================================
    # HAZARD GROUP
    # =====================================================

    hazard_group = "A"

    if (
        "H350" in hkod
        or
        "H340" in hkod
    ):

        hazard_group = "E"

    elif "H330" in hkod:

        hazard_group = "D"

    elif "H314" in hkod:

        hazard_group = "C"

    elif "H373" in hkod:

        hazard_group = "B"

    # =====================================================
    # CONTROL APPROACH
    # =====================================================

    if hazard_group == "E":

        kontrol = "Control Approach 4"

    elif hazard_group == "D":

        kontrol = "Control Approach 3"

    elif hazard_group == "C":

        kontrol = "Control Approach 2"

    else:

        kontrol = "Control Approach 1"

    # =====================================================
    # GHS
    # =====================================================

    ghs = []

    if "H314" in hkod:

        ghs.append(
            "GHS05"
        )

    if (
        "H315" in hkod
        or
        "H319" in hkod
    ):

        ghs.append(
            "GHS07"
        )

    if "H330" in hkod:

        ghs.append(
            "GHS06"
        )

    if (
        "H340" in hkod
        or
        "H350" in hkod
        or
        "H373" in hkod
    ):

        ghs.append(
            "GHS08"
        )

    if "H225" in hkod:

        ghs.append(
            "GHS02"
        )

    # =====================================================
    # SONUC EKRAN
    # =====================================================

    if sonuc == "DUSUK RISK":

        st.success(
            sonuc
        )

    elif sonuc == "ORTA RISK":

        st.warning(
            sonuc
        )

    else:

        st.error(
            sonuc
        )

    st.subheader(
        "Hazard Group"
    )

    st.write(
        hazard_group
    )

    st.subheader(
        "Control Approach"
    )

    st.write(
        kontrol
    )

    # =====================================================
    # GHS GOSTER
    # =====================================================

    st.subheader(
        "GHS Pictograms"
    )

    cols = st.columns(5)

    for i, g in enumerate(ghs):

        if g == "GHS02":

            with cols[i % 5]:

                st.image(
                    "ghs02.png",
                    width=100
                )

        elif g == "GHS05":

            with cols[i % 5]:

                st.image(
                    "ghs05.png",
                    width=100
                )

        elif g == "GHS06":

            with cols[i % 5]:

                st.image(
                    "ghs06.png",
                    width=100
                )

        elif g == "GHS07":

            with cols[i % 5]:

                st.image(
                    "ghs07.png",
                    width=100
                )

        elif g == "GHS08":

            with cols[i % 5]:

                st.image(
                    "ghs08.png",
                    width=100
                )

    # =====================================================
    # PDF
    # =====================================================

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.set_font(
        "Helvetica",
        "B",
        18
    )

    pdf.cell(
        190,
        12,
        temizle(
            "COSHH PROFESSIONAL REPORT"
        ),
        0,
        1,
        "C"
    )

    pdf.ln(10)

    bilgiler = [

        (
            "Report No",
            rapor_no
        ),

        (
            "Chemical",
            secili
        ),

        (
            "CAS No",
            cas
        ),

        (
            "H Codes",
            hkod
        ),

        (
            "Physical State",
            fiziksel
        ),

        (
            "Process",
            islem
        ),

        (
            "Duration",
            str(sure)
        ),

        (
            "Amount",
            str(miktar)
        ),

        (
            "Exposure",
            maruziyet
        ),

        (
            "Hazard Group",
            hazard_group
        ),

        (
            "Risk Result",
            sonuc
        ),

        (
            "Control Approach",
            kontrol
        )

    ]

    for label, value in bilgiler:

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        pdf.cell(
            60,
            8,
            temizle(label + ":"),
            0,
            0
        )

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.cell(
            120,
            8,
            temizle(value),
            0,
            1
        )

    # =====================================================
    # PDF GHS
    # =====================================================

    pdf.ln(10)

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        190,
        10,
        temizle(
            "GHS Pictograms"
        ),
        0,
        1
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    for g in ghs:

        pdf.cell(
            190,
            8,
            temizle(g),
            0,
            1
        )

    # =====================================================
    # DATE
    # =====================================================

    pdf.ln(10)

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.cell(
        190,
        8,
        temizle(
            str(datetime.now())
        ),
        0,
        1
    )

    # =====================================================
    # SAVE PDF
    # =====================================================

    filename = (
        "COSHH_REPORT.pdf"
    )

    pdf.output(
        filename
    )

    with open(
        filename,
        "rb"
    ) as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
