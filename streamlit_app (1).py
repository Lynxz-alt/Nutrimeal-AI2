!pip install fpdf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime


st.set_page_config(page_title="NutriMeal AI", page_icon="🥗", layout="centered")

@st.cache_data
def load_data():
    df = pd.read_csv("foods.csv")
    df['Calories'] = df['Energy (kJ)'] * 0.239006
    df.rename(columns={
        'Menu': 'Food',
        'Carbohydrates (g)': 'Carbs'
    }, inplace=True)
    df.drop(columns=['Unnamed: 0', 'Energy (kJ)'], inplace=True)
    return df

def export_menu_to_pdf(menu_df, filename="Menu_Rekomendasi.pdf"):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="NutriMeal AI - Rekomendasi Menu", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True, align='C')
    pdf.ln(10)

    for index, row in menu_df.iterrows():
        line = f"{row['Food']} - {row['Calories']:.0f} kcal, Protein: {row['Protein (g)']}g, Lemak: {row['Fat (g)']}g, Karbo: {row['Carbs']}g"
        pdf.multi_cell(0, 10, txt=line)

    path = f"Menu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(path)
    return path

df = load_data()

# Init session state
if "riwayat_menu" not in st.session_state:
    st.session_state["riwayat_menu"] = []

# Sidebar
st.sidebar.header("🧍 Profil Kamu")
goal = st.sidebar.selectbox("🎯 Tujuan Gizi", ["Diet", "Bulking", "Maintain"])
max_cal = st.sidebar.slider("🔥 Batas Kalori Maksimum", 100, 1500, 500, step=50)
min_protein = st.sidebar.slider("💪 Minimal Protein (gram)", 0, 100, 20)

df_filtered = df[(df['Calories'] <= max_cal) & (df['Protein (g)'] >= min_protein)]

# Tab menu dan riwayat
tab1, tab2 = st.tabs(["🍽️ Rekomendasi Menu", "📜 Riwayat Menu"])

with tab1:
    st.subheader("Rekomendasi Menu Harian")
    if st.button("Tampilkan Rekomendasi"):
        if df_filtered.empty:
            st.warning("Tidak ada makanan yang sesuai dengan filter kamu. Coba ubah filter!")
        else:
            st.success(f"Menampilkan {len(df_filtered)} makanan yang sesuai:")
            st.dataframe(df_filtered[["Food", "Calories", "Protein (g)", "Fat (g)", "Carbs"]])

            # Simpan ke riwayat
            st.session_state["last_menu"] = df_filtered.copy()
            st.session_state["riwayat_menu"].append(df_filtered.copy())

    if "last_menu" in st.session_state:
        if st.download_button("💾 Export Menu ke PDF", data=open(export_menu_to_pdf(st.session_state["last_menu"]), "rb"), file_name="Menu_Rekomendasi.pdf"):
            st.toast("PDF berhasil disiapkan!", icon="✅")

        # Pie chart
        st.subheader("📊 Komposisi Gizi Rata-rata")
        avg_nutrients = st.session_state["last_menu"][["Protein (g)", "Fat (g)", "Carbs"]].mean()
        fig, ax = plt.subplots()
        ax.pie(avg_nutrients, labels=avg_nutrients.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

with tab2:
    st.subheader("Riwayat Menu yang Pernah Direkomendasikan")
    if len(st.session_state["riwayat_menu"]) == 0:
        st.info("Belum ada riwayat menu.")
    else:
        for i, m in enumerate(reversed(st.session_state["riwayat_menu"][-5:])):
            st.markdown(f"**Riwayat #{len(st.session_state['riwayat_menu']) - i}**")
            st.dataframe(m[["Food", "Calories", "Protein (g)", "Fat (g)", "Carbs"]])

# Tips
st.markdown("---")
st.subheader("💡 Tips Gizi Harian")
st.info("Minumlah air putih minimal 8 gelas per hari untuk membantu metabolisme dan menjaga hidrasi tubuh.")

st.markdown("---")
st.caption("Dibuat oleh NutriMeal AI · 2025")
