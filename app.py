"""
Dashboard Visualisasi Data Multivariat & Geospasial P0 & P1 Per Kabupaten/Kota: Analisis PCA, K-Means Clustering, & Disparitas Pembangunan Indonesia
Sumber Data: PCA_Visdat (4).ipynb & kumpulan data.xlsx (Sheet Persentase_P0, Kedalaman_P1, Hasil_PCA, dll)
"""

import json
import os
import re
import urllib.request
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# -----------------------------------------------------------------------------
# Koordinat Geospasial Resmi 38 Provinsi Indonesia
# -----------------------------------------------------------------------------
PROVINCE_COORDS = {
    'ACEH': {'lat': 4.6951, 'lon': 96.7494},
    'SUMATERA UTARA': {'lat': 2.1154, 'lon': 99.5451},
    'SUMATERA BARAT': {'lat': -0.7399, 'lon': 100.8000},
    'RIAU': {'lat': 0.2933, 'lon': 101.7068},
    'KEPULAUAN RIAU': {'lat': 3.9456, 'lon': 108.1428},
    'JAMBI': {'lat': -1.4852, 'lon': 103.6160},
    'SUMATERA SELATAN': {'lat': -3.3199, 'lon': 104.9147},
    'KEPULAUAN BANGKA BELITUNG': {'lat': -2.7411, 'lon': 106.4406},
    'BENGKULU': {'lat': -3.8004, 'lon': 102.2655},
    'LAMPUNG': {'lat': -4.5586, 'lon': 105.4068},
    'DKI JAKARTA': {'lat': -6.2088, 'lon': 106.8456},
    'JAWA BARAT': {'lat': -6.9175, 'lon': 107.6191},
    'JAWA TENGAH': {'lat': -7.1510, 'lon': 110.1403},
    'DI YOGYAKARTA': {'lat': -7.7956, 'lon': 110.3695},
    'JAWA TIMUR': {'lat': -7.5360, 'lon': 112.2384},
    'BANTEN': {'lat': -6.4058, 'lon': 106.0640},
    'BALI': {'lat': -8.4095, 'lon': 115.1889},
    'NUSA TENGGARA BARAT': {'lat': -8.6529, 'lon': 117.3616},
    'NUSA TENGGARA TIMUR': {'lat': -8.6574, 'lon': 121.0794},
    'KALIMANTAN BARAT': {'lat': -0.2787, 'lon': 111.4753},
    'KALIMANTAN TENGAH': {'lat': -1.6815, 'lon': 113.3824},
    'KALIMANTAN SELATAN': {'lat': -3.0926, 'lon': 115.2838},
    'KALIMANTAN TIMUR': {'lat': 0.5387, 'lon': 116.4194},
    'KALIMANTAN UTARA': {'lat': 3.0731, 'lon': 116.0414},
    'SULAWESI UTARA': {'lat': 0.6247, 'lon': 123.9750},
    'SULAWESI TENGAH': {'lat': -1.4300, 'lon': 121.4456},
    'SULAWESI SELATAN': {'lat': -3.6687, 'lon': 119.9741},
    'SULAWESI TENGGARA': {'lat': -4.1449, 'lon': 122.1746},
    'GORONTALO': {'lat': 0.6999, 'lon': 122.4467},
    'SULAWESI BARAT': {'lat': -2.8441, 'lon': 119.2321},
    'MALUKU': {'lat': -3.2385, 'lon': 130.1453},
    'MALUKU UTARA': {'lat': 1.5709, 'lon': 127.8087},
    'PAPUA BARAT': {'lat': -1.3361, 'lon': 133.1747},
    'PAPUA': {'lat': -2.5337, 'lon': 140.7181},
    'PAPUA SELATAN': {'lat': -7.5000, 'lon': 139.5000},
    'PAPUA TENGAH': {'lat': -3.8000, 'lon': 136.5000},
    'PAPUA PEGUNUNGAN': {'lat': -4.1000, 'lon': 138.9000},
    'PAPUA BARAT DAYA': {'lat': -1.1500, 'lon': 131.2500},
}

# -----------------------------------------------------------------------------
# Konfigurasi Halaman Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Disparitas Pembangunan & Peta Geospasial Kab/Kota Indonesia",
    page_icon="🇮🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom CSS Styling (Modern, Clean, Glassmorphic Dashboard Design)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%);
        color: white;
        padding: 2.2rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .main-header p {
        font-size: 1.05rem;
        color: #cbd5e1;
        max-width: 900px;
        line-height: 1.5;
        margin: 0;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-caption {
        font-size: 0.8rem;
        color: #0284c7;
        font-weight: 500;
        margin-top: 0.3rem;
    }

    .story-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        border-radius: 12px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .story-card h4 {
        margin-top: 0;
        font-weight: 700;
        color: #0f172a;
        font-size: 1.15rem;
    }
    .story-card p, .story-card li {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .badge-c0 {
        background-color: #fef3c7;
        color: #b45309;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-c1 {
        background-color: #ffedd5;
        color: #c2410c;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-c2 {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-outlier {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px 8px 0 0;
        padding-left: 18px;
        padding-right: 18px;
        font-weight: 600;
        font-size: 0.92rem;
    }

    /* Responsivitas Layar Kecil (Mobile & Tablet) */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
        .main-header {
            padding: 1.2rem 1rem !important;
            border-radius: 12px !important;
        }
        .main-header h1 {
            font-size: 1.4rem !important;
        }
        .main-header p {
            font-size: 0.88rem !important;
        }
        .story-card {
            padding: 1rem !important;
        }
        .metric-card {
            padding: 0.8rem 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        .metric-value {
            font-size: 1.35rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px !important;
            font-size: 0.8rem !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loader: Membaca Langsung dari PCA_Visdat (4).ipynb dan kumpulan data.xlsx
# -----------------------------------------------------------------------------
@st.cache_data
def load_geojson():
    geojson_path = "indonesia_adm2.geojson"
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_data
def load_hierarki_data():
    xlsx_hierarki = "hierarki_tingkat.xlsx"
    if not os.path.exists(xlsx_hierarki):
        xlsx_hierarki = "kemiskinan_hierarki.xlsx"
    
    if os.path.exists(xlsx_hierarki):
        df_k = pd.read_excel(xlsx_hierarki, sheet_name="Kab_Kota")
        df_p = pd.read_excel(xlsx_hierarki, sheet_name="Provinsi")
        df_is = pd.read_excel(xlsx_hierarki, sheet_name="Pulau")
        
        df_k['Jumlah Penduduk Miskin (Ribu Jiwa)'] = pd.to_numeric(df_k['Jumlah Penduduk Miskin (Ribu Jiwa)'], errors='coerce')
        df_k['P0'] = pd.to_numeric(df_k['P0'], errors='coerce')
        df_k['P1'] = pd.to_numeric(df_k['P1'], errors='coerce')
        df_k['P2'] = pd.to_numeric(df_k['P2'], errors='coerce')
        
        return df_k, df_p, df_is
    return None, None, None

@st.cache_data
def generate_hierarchical_figure(fig_type, color_scale='Viridis'):
    df_kab_h, df_prov_h, df_pulau_h = load_hierarki_data()
    if df_kab_h is None:
        return None

    kab_dict = {}
    for _, r in df_kab_h.iterrows():
        p_name = r['Pulau']
        pr_name = r['Provinsi']
        k_name = r['Kabupaten/Kota']
        node_id = f"{p_name}/{pr_name}/{k_name}"
        kab_dict[node_id] = {
            'name': k_name,
            'level': 'Kabupaten/Kota',
            'pop': r['Jumlah Penduduk Miskin (Ribu Jiwa)'],
            'p0': r['P0'],
            'p1': r['P1'],
            'p2': r['P2']
        }

    prov_agg = df_kab_h.groupby(['Pulau', 'Provinsi']).agg({
        'Jumlah Penduduk Miskin (Ribu Jiwa)': 'sum',
        'P0': 'mean',
        'P1': 'mean',
        'P2': 'mean'
    }).reset_index()

    prov_dict = {}
    for _, r in prov_agg.iterrows():
        p_name = r['Pulau']
        pr_name = r['Provinsi']
        node_id = f"{p_name}/{pr_name}"
        prov_sheet_row = df_prov_h[df_prov_h['Provinsi'] == pr_name] if df_prov_h is not None else pd.DataFrame()
        p0_val = r['P0']
        p1_val = r['P1']
        p2_val = r['P2']
        if not prov_sheet_row.empty and not pd.isna(prov_sheet_row.iloc[0]['P0']):
            p0_val = prov_sheet_row.iloc[0]['P0']
            p1_val = prov_sheet_row.iloc[0]['P1']
            p2_val = prov_sheet_row.iloc[0]['P2']
        
        prov_dict[node_id] = {
            'name': pr_name,
            'level': 'Provinsi',
            'pop': r['Jumlah Penduduk Miskin (Ribu Jiwa)'],
            'p0': p0_val,
            'p1': p1_val,
            'p2': p2_val
        }

    pulau_agg = df_kab_h.groupby('Pulau').agg({
        'Jumlah Penduduk Miskin (Ribu Jiwa)': 'sum',
        'P0': 'mean',
        'P1': 'mean',
        'P2': 'mean'
    }).reset_index()

    pulau_dict = {}
    for _, r in pulau_agg.iterrows():
        p_name = r['Pulau']
        node_id = p_name
        pulau_dict[node_id] = {
            'name': p_name,
            'level': 'Pulau',
            'pop': r['Jumlah Penduduk Miskin (Ribu Jiwa)'],
            'p0': r['P0'],
            'p1': r['P1'],
            'p2': r['P2']
        }

    all_nodes = {**kab_dict, **prov_dict, **pulau_dict}

    if fig_type == 'treemap':
        fig = px.treemap(
            df_kab_h,
            path=['Pulau', 'Provinsi', 'Kabupaten/Kota'],
            values='Jumlah Penduduk Miskin (Ribu Jiwa)',
            color='P0',
            color_continuous_scale=color_scale,
            title="Treemap Hierarki Kemiskinan Indonesia (Pulau → Provinsi → Kabupaten/Kota)<br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>"
        )
    else:
        fig = px.sunburst(
            df_kab_h,
            path=['Pulau', 'Provinsi', 'Kabupaten/Kota'],
            values='Jumlah Penduduk Miskin (Ribu Jiwa)',
            color='P0',
            color_continuous_scale=color_scale,
            title="Sunburst Hierarki Kemiskinan Indonesia (Pulau → Provinsi → Kabupaten/Kota)<br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>"
        )

    tr = fig.data[0]
    customdata_list = []
    colors_list = []

    for node_id in tr.ids:
        if node_id in all_nodes:
            info = all_nodes[node_id]
            pop_val = info['pop']
            pop_str = f"{pop_val:,.2f} Ribu Jiwa ({int(round(pop_val * 1000)):,} Jiwa)"
            customdata_list.append([
                info['name'],
                info['level'],
                pop_str,
                f"{info['p0']:.2f}%",
                f"{info['p1']:.2f}",
                f"{info['p2']:.2f}"
            ])
            colors_list.append(info['p0'])
        else:
            customdata_list.append(['-', '-', '-', '-', '-', '-'])
            colors_list.append(0)

    tr.customdata = np.array(customdata_list, dtype=object)
    tr.marker.colors = np.array(colors_list)

    tr.hovertemplate = (
        "<b>%{customdata[0]}</b><br>"
        "Level Hierarki: <b>%{customdata[1]}</b><br>"
        "Total Penduduk Kemiskinan: <b>%{customdata[2]}</b><br>"
        "P0 (Persentase Kemiskinan): <b>%{customdata[3]}</b><br>"
        "P1 (Indeks Kedalaman): <b>%{customdata[4]}</b><br>"
        "P2 (Indeks Keparahan): <b>%{customdata[5]}</b>"
        "<extra></extra>"
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{'Treemap' if fig_type == 'treemap' else 'Sunburst'} Hierarki Kemiskinan Indonesia (Pulau → Provinsi → Kabupaten/Kota)</b><br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>",
            font=dict(size=16, color='#0f172a')
        ),
        height=650,
        margin=dict(l=15, r=15, t=65, b=20),
        coloraxis_colorbar=dict(
            title="Persentase Kemiskinan (P0)",
            ticksuffix="%"
        )
    )

    return fig

def norm_name(s):
    s = str(s).upper()
    for prefix in ["KABUPATEN ADM. ", "KABUPATEN ADM ", "KABUPATEN ", "KOTA ADM. ", "KOTA ADM ", "KOTA ", "KAB. ", "KAB "]:
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s.replace(".", "").replace("-", " ").replace("  ", " ").strip()

@st.cache_data
def load_and_process_data():
    nb_path = "PCA_Visdat (4).ipynb"
    xlsx_path = "kumpulan data.xlsx"

    features = []
    df_features = None

    # 1. Membaca dimensi dan data langsung dari output cell 17 / cell 31 di notebook jika tersedia
    if os.path.exists(nb_path):
        try:
            with open(nb_path, "r", encoding="utf-8") as f:
                nb = json.load(f)

            for cell in nb.get("cells", []):
                for out in cell.get("outputs", []):
                    html_data = out.get("data", {}).get("text/html", [])
                    html_str = "".join(html_data) if isinstance(html_data, list) else str(html_data)
                    needle = "Plotly.newPlot("
                    pos = html_str.find(needle)
                    if pos != -1 and ("parcoords" in html_str or "dimensions" in html_str):
                        call_str = html_str[pos + len(needle):]
                        first_comma = call_str.find(",")
                        after_id = call_str[first_comma + 1:].strip()
                        decoder = json.JSONDecoder()
                        fig_data, _ = decoder.raw_decode(after_id)
                        if isinstance(fig_data, list) and len(fig_data) > 0 and "dimensions" in fig_data[0]:
                            dims = fig_data[0]["dimensions"]
                            features = [d["label"] for d in dims]
                            data_dict = {d["label"]: d["values"] for d in dims}
                            df_features = pd.DataFrame(data_dict)
                            break
                if df_features is not None:
                    break
        except Exception as e:
            df_features = None

    # 2. Sinkronisasi dengan 38 Nama Resmi Provinsi & Sheet Indikator
    prov_alpha = sorted(PROVINCE_COORDS.keys())

    try:
        df_hasil_pca = pd.read_excel(xlsx_path, sheet_name="Hasil_PCA")
    except Exception:
        sheets_map = {
            'IPM': 'IPM', 'Kedalaman_P1': 'Kedalaman_P1', 'Kematian_Bayi': 'Kematian_Bayi',
            'Sanitasi': 'Sanitasi', 'Gini': 'Gini', 'TPT': 'TPT', 'PDRB_Kapita': 'PDRB_Kapita',
            'Pekerja_Formal': 'Pekerja_Formal', 'APK_PT': 'APK_PT', 'Internet': 'Internet_BlankSpot'
        }
        df_final = None
        for s_name, var_name in sheets_map.items():
            df_s = pd.read_excel(xlsx_path, sheet_name=s_name)
            df_s.columns = df_s.columns.str.strip()
            prov_col = [col for col in df_s.columns if 'prov' in col.lower()][0]
            val_col = [col for col in df_s.columns if col != prov_col][0]
            df_temp = df_s[[prov_col, val_col]].copy()
            df_temp.columns = ['Provinsi', var_name]
            df_temp['Provinsi'] = df_temp['Provinsi'].astype(str).str.strip().str.upper()
            df_temp['Provinsi'] = df_temp['Provinsi'].replace({
                'KEP. BANGKA BELITUNG': 'KEPULAUAN BANGKA BELITUNG',
                'D I YOGYAKARTA': 'DI YOGYAKARTA',
                'D.I. YOGYAKARTA': 'DI YOGYAKARTA'
            })
            df_temp[var_name] = pd.to_numeric(df_temp[var_name], errors='coerce')
            df_final = df_temp if df_final is None else pd.merge(df_final, df_temp, on='Provinsi', how='outer')

        df_final = df_final[df_final['Provinsi'].isin(prov_alpha)].drop_duplicates(subset=['Provinsi']).sort_values('Provinsi').reset_index(drop=True)
        for col in df_final.columns:
            if col != 'Provinsi':
                df_final[col] = df_final[col].fillna(df_final[col].median())

        features_temp = [c for c in df_final.columns if c != 'Provinsi']
        scaler_p = StandardScaler()
        X_p = scaler_p.fit_transform(df_final[features_temp])
        pca_p = PCA(n_components=2, random_state=42)
        pcs_p = pca_p.fit_transform(X_p)
        kmeans_p = KMeans(n_clusters=3, random_state=42)
        clusters_p = kmeans_p.fit_predict(X_p)
        iso_p = IsolationForest(contamination=0.1, random_state=42)
        outliers_p = iso_p.fit_predict(X_p)

        df_hasil_pca = pd.DataFrame({
            'Provinsi': df_final['Provinsi'],
            'PC1': pcs_p[:, 0],
            'PC2': pcs_p[:, 1],
            'Cluster': clusters_p.astype(str),
            'Status_Outlier': ['Outlier' if o == -1 else 'Normal' for o in outliers_p]
        })

    if df_features is None or len(df_features) != 38:
        # Fallback langsung dari kumpulan data.xlsx jika notebook tidak terbaca
        sheets_map = {
            'IPM': 'IPM', 'Kedalaman_P1': 'Kedalaman_P1', 'Kematian_Bayi': 'Kematian_Bayi',
            'Sanitasi': 'Sanitasi', 'Gini': 'Gini', 'TPT': 'TPT', 'PDRB_Kapita': 'PDRB_Kapita',
            'Pekerja_Formal': 'Pekerja_Formal', 'APK_PT': 'APK_PT', 'Internet': 'Internet_BlankSpot'
        }
        df_final = None
        for s_name, var_name in sheets_map.items():
            df_s = pd.read_excel(xlsx_path, sheet_name=s_name)
            df_s.columns = df_s.columns.str.strip()
            prov_col = [col for col in df_s.columns if 'prov' in col.lower()][0]
            val_col = [col for col in df_s.columns if col != prov_col][0]
            df_temp = df_s[[prov_col, val_col]].copy()
            df_temp.columns = ['Provinsi', var_name]
            df_temp['Provinsi'] = df_temp['Provinsi'].astype(str).str.strip().str.upper()
            df_temp['Provinsi'] = df_temp['Provinsi'].replace({
                'KEP. BANGKA BELITUNG': 'KEPULAUAN BANGKA BELITUNG',
                'D I YOGYAKARTA': 'DI YOGYAKARTA',
                'D.I. YOGYAKARTA': 'DI YOGYAKARTA'
            })
            df_temp[var_name] = pd.to_numeric(df_temp[var_name], errors='coerce')
            df_final = df_temp if df_final is None else pd.merge(df_final, df_temp, on='Provinsi', how='outer')

        df_final = df_final[df_final['Provinsi'].isin(prov_alpha)].drop_duplicates(subset=['Provinsi']).sort_values('Provinsi').reset_index(drop=True)
        for col in df_final.columns:
            if col != 'Provinsi':
                df_final[col] = df_final[col].fillna(df_final[col].median())
        features = [c for c in df_final.columns if c != 'Provinsi']
        df_features = df_final[features].copy()

    df_features['Provinsi'] = prov_alpha

    # 3. Ekstraksi Data Persentase Kemiskinan (P0) Provinsi
    df_p0 = pd.read_excel(xlsx_path, sheet_name="Persentase_P0").iloc[:, :2]
    df_p0.columns = ["Prov_Raw", "P0_Val"]
    df_p0["Prov_Clean"] = df_p0["Prov_Raw"].astype(str).str.strip().str.upper()
    df_p0["Prov_Clean"] = df_p0["Prov_Clean"].replace({
        "KEP. BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
        "D I YOGYAKARTA": "DI YOGYAKARTA"
    })
    df_p0["P0_Kemiskinan"] = pd.to_numeric(df_p0["P0_Val"], errors="coerce")
    df_p0_prov = df_p0[df_p0["Prov_Clean"].isin(prov_alpha)].drop_duplicates(subset=["Prov_Clean"]).copy()
    df_p0_prov["Provinsi"] = df_p0_prov["Prov_Clean"]

    # Menggabungkan dengan skor PCA, Cluster, Outlier, dan P0 Kemiskinan
    df_merged = pd.merge(
        df_features,
        df_hasil_pca[['Provinsi', 'PC1', 'PC2', 'Cluster', 'Status_Outlier']],
        on='Provinsi'
    )
    df_merged = pd.merge(
        df_merged,
        df_p0_prov[['Provinsi', 'P0_Kemiskinan']],
        on='Provinsi',
        how='left'
    )
    df_merged['Cluster'] = df_merged['Cluster'].astype(str)

    # Tambahkan koordinat latitude & longitude tingkat Provinsi
    df_merged['lat'] = df_merged['Provinsi'].map(lambda p: PROVINCE_COORDS[p]['lat'] if p in PROVINCE_COORDS else -2.5)
    df_merged['lon'] = df_merged['Provinsi'].map(lambda p: PROVINCE_COORDS[p]['lon'] if p in PROVINCE_COORDS else 118.0)

    # 4. Ekstraksi Data SELURUH 514 KABUPATEN/KOTA se-Indonesia untuk P0 & P1
    df_p1 = pd.read_excel(xlsx_path, sheet_name="Kedalaman_P1")
    prov_match_list = list(PROVINCE_COORDS.keys()) + ['KEP. BANGKA BELITUNG', 'D I YOGYAKARTA', 'INDONESIA']

    def parse_kabkota(df_in, val_col_name):
        c0 = df_in.columns[0]
        c1 = df_in.columns[1]
        curr_p = "UNKNOWN"
        kab_rows = []
        for _, r in df_in.iterrows():
            raw_name = str(r[c0]).strip()
            val = pd.to_numeric(r[c1], errors="coerce")
            if raw_name.isupper() and (raw_name in prov_match_list or raw_name.replace('.','').replace(' ','').isalpha()):
                curr_p = raw_name
                if curr_p == 'KEP. BANGKA BELITUNG': curr_p = 'KEPULAUAN BANGKA BELITUNG'
                if curr_p == 'D I YOGYAKARTA': curr_p = 'DI YOGYAKARTA'
            else:
                if not pd.isna(val) and raw_name not in ('nan', '2025'):
                    kab_rows.append({
                        'Kabupaten_Kota': raw_name,
                        'Provinsi': curr_p,
                        val_col_name: val
                    })
        return pd.DataFrame(kab_rows)

    df_kab_p0 = parse_kabkota(df_p0, "P0_Kemiskinan")
    df_kab_p1 = parse_kabkota(df_p1, "P1_Kedalaman")

    df_kab = pd.merge(df_kab_p0, df_kab_p1, on=["Kabupaten_Kota", "Provinsi"], how="inner")

    # Mapping shapeName & Centroid Geospasial Presisi per Kabupaten/Kota
    # Membedakan 'Kabupaten X' vs 'Kota X' (misal Kabupaten Bandung vs Kota Bandung)
    geojson_data = load_geojson()

    def norm_exact(name):
        name = str(name).strip()
        is_city = name.lower().startswith('kota')
        clean = re.sub(r'^(kabupaten|kota|kab\.?)\s+', '', name, flags=re.IGNORECASE).strip()
        clean = re.sub(r'\s+', ' ', clean).upper()
        return ('KOTA' if is_city else 'KAB', clean)

    def calc_centroid(coords):
        pts = []
        def rec(c):
            if not c: return
            if isinstance(c[0], (int, float)): pts.append(c)
            else:
                for sub in c: rec(sub)
        rec(coords)
        if not pts: return None, None
        return float(np.mean([p[1] for p in pts])), float(np.mean([p[0] for p in pts]))

    ALIASES = {
        ('KAB', 'KARANGASEM'): 'Karang Asem',
        ('KAB', 'MAHAKAM ULU'): 'Mahakam Hulu'
    }

    geo_dict = {}
    centroids = {}

    if geojson_data:
        for feat in geojson_data.get('features', []):
            sn = feat.get('properties', {}).get('shapeName', '')
            k = norm_exact(sn)
            geo_dict[k] = sn
            c_lat, c_lon = calc_centroid(feat.get('geometry', {}).get('coordinates', []))
            if c_lat is not None:
                centroids[sn] = {'lat': c_lat, 'lon': c_lon}

    mapped_shapes, lats, lons = [], [], []
    for idx, row in df_kab.iterrows():
        name = row['Kabupaten_Kota']
        p = row['Provinsi']
        k = norm_exact(name)
        if k in ALIASES:
            sn = ALIASES[k]
        elif k in geo_dict:
            sn = geo_dict[k]
        else:
            sn = name

        mapped_shapes.append(sn)
        if sn in centroids:
            lats.append(centroids[sn]['lat'])
            lons.append(centroids[sn]['lon'])
        else:
            coords = PROVINCE_COORDS.get(p, {'lat': -2.5, 'lon': 118.0})
            lats.append(coords['lat'])
            lons.append(coords['lon'])

    df_kab['shapeName'] = mapped_shapes
    df_kab['lat'] = lats
    df_kab['lon'] = lons

    # Menghitung Standardisasi Z-Score dan Model PCA Dinamis
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_merged[features])
    df_scaled = pd.DataFrame(X_scaled, columns=features, index=df_merged['Provinsi'])

    pca_model = PCA(n_components=2, random_state=42)
    pca_model.fit(X_scaled)

    # Matrix Loading
    loadings_matrix = pca_model.components_
    df_loadings = pd.DataFrame(
        loadings_matrix.T,
        index=features,
        columns=['PC1_Loading', 'PC2_Loading']
    )

    # Hitung Variansi
    exp_var_pct = pca_model.explained_variance_ratio_ * 100
    cum_var_pct = np.cumsum(exp_var_pct)

    return df_merged, df_scaled, df_kab, features, pca_model, df_loadings, exp_var_pct, cum_var_pct

# Eksekusi Pemrosesan Data
df_main, df_scaled, df_kab, features, pca_model, df_loadings, exp_var_pct, cum_var_pct = load_and_process_data()

# -----------------------------------------------------------------------------
# Header Dashboard & Ringkasan Metrik Utama
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div style="display:flex; align-items:center; gap: 10px; margin-bottom: 8px;">
        <span style="background: rgba(255,255,255,0.15); padding: 4px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
            Visualisasi Data Multivariat & Geospasial Kab/Kota • OpenStreetMap
        </span>
    </div>
    <h1>Struktur Polarisasi Sosial-Ekonomi & Disparitas 38 Provinsi</h1>
    <p>
        Menyingkap anatomi kesenjangan wilayah di Indonesia melalui sintesis 10 indikator multidimensi menggunakan 
        <b>Principal Component Analysis (PCA)</b>, <b>K-Means Clustering</b>, <b>Isolation Forest</b>, serta 
        <b>Peta Geospasial P0 & P1 untuk 514 Kabupaten/Kota se-Indonesia</b>.
    </p>
</div>
""", unsafe_allow_html=True)

# Kartu Metrik Ringkasan
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Cakupan Wilayah</div>
        <div class="metric-value">{len(df_kab)}</div>
        <div class="metric-caption">Kabupaten/Kota (38 Provinsi)</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Dimensi Indikator</div>
        <div class="metric-value">10</div>
        <div class="metric-caption">Kesehatan, Ekonomi, P0, P1</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Variansi Terjelaskan</div>
        <div class="metric-value">{cum_var_pct[1]:.2f}%</div>
        <div class="metric-caption">PC1 ({exp_var_pct[0]:.1f}%) + PC2 ({exp_var_pct[1]:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    mean_p0_kab = df_kab['P0_Kemiskinan'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Rata-Rata P0 Kab/Kota</div>
        <div class="metric-value">{mean_p0_kab:.2f}%</div>
        <div class="metric-caption">Rentang 1,5% s.d. 41,5%</div>
    </div>
    """, unsafe_allow_html=True)

with col_m5:
    mean_p1_kab = df_kab['P1_Kedalaman'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Rata-Rata P1 Kedalaman</div>
        <div class="metric-value">{mean_p1_kab:.2f}</div>
        <div class="metric-caption">Indeks Kedalaman Kemiskinan</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# Sidebar: Kontrol Eksplorasi & Filter
# -----------------------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/b3/Coat_of_arms_of_Indonesia.svg", width=65)
st.sidebar.markdown("### 🎛️ Panel Kontrol & Filter")
st.sidebar.markdown("Atur visualisasi dan filter data secara dinamis:")

# Filter Klaster
selected_clusters = st.sidebar.multiselect(
    "Pilih Klaster untuk Ditampilkan (Tingkat Provinsi):",
    options=['0', '1', '2'],
    default=['0', '1', '2'],
    format_func=lambda x: f"Klaster {x} ({'Maju' if x=='2' else 'Berkembang' if x=='0' else 'Rentan / Tertinggal'})"
)

# Highlight Outlier
highlight_outlier = st.sidebar.checkbox("Tandai Provinsi Pencilan (Outlier)", value=True)

# Skala Panah Loading PCA
arrow_scale = st.sidebar.slider("Faktor Skala Panah Loading Biplot:", min_value=3.0, max_value=12.0, value=8.0, step=0.5)

# Mode Tampilan Grafik
render_engine = st.sidebar.radio(
    "Mesin Visualisasi PCA Biplot:",
    ["Plotly Interaktif (Zoom, Pan, Tooltip)", "Matplotlib & Seaborn Orisinil Notebook"],
    index=0
)

# Filter dataframe berdasarkan pilihan klaster
filtered_df = df_main[df_main['Cluster'].isin(selected_clusters)].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Keterangan Warna Klaster (Palet Ramah Buta Warna):**
- <span style="color:#0072B2; font-weight:bold;">● Klaster 2</span>: Wilayah Maju (22 Provinsi)
- <span style="color:#E69F00; font-weight:bold;">● Klaster 0</span>: Wilayah Berkembang (14 Provinsi)
- <span style="color:#D55E00; font-weight:bold;">● Klaster 1</span>: Wilayah Rentan Ekstrem (2 Provinsi)
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Tab Utama Storytelling & Visualisasi
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧭 1. PCA Biplot (Indikator & Sebaran)",
    "🗺️ 2. Clustered Heatmap (Hierarki)",
    "📈 3. Parallel Coordinates (Profil)",
    "🔍 4. Investigasi Pencilan (Outliers)",
    "📊 5. Hierarki Kemiskinan (Treemap & Sunburst)",
    "🌐 6. Peta Geospasial P0 & P1 Kab/Kota"
])

# Palet warna ramah buta warna (Okabe-Ito Palette)
CLUSTER_COLORS = {'0': '#E69F00', '1': '#D55E00', '2': '#0072B2'}
CLUSTER_NAMES = {'0': 'Klaster 0 (Berkembang)', '1': 'Klaster 1 (Rentan)', '2': 'Klaster 2 (Maju)'}

# =============================================================================
# TAB 1: PCA Biplot
# =============================================================================
with tab1:
    st.markdown("""
    <div class="story-card">
        <h4>🧭 Narasi Bab 1: Mengurai Dimensi Ruang Pembangunan Indonesia</h4>
        <p>
            Dari 10 indikator sosial-ekonomi yang kompleks dan saling berkorelasi, <b>Principal Component Analysis (PCA)</b> 
            berhasil mengekstraksi dua dimensi laten utama yang merangkum <b>63,21% variabilitas total data</b>:
        </p>
        <ul>
            <li>
                <b>PC1 (Sumbu Horizontal - 48,46% Variansi) — "Indeks Kesejahteraan & Layanan Dasar":</b><br>
                Vektor panah merah menunjukkan arah indikator. Indikator <code>IPM</code>, <code>Sanitasi</code>, <code>Pekerja_Formal</code>, 
                serta <code>Kematian_Bayi</code> dan <code>Kedalaman_P1</code> (setelah penyesuaian arah polaritas) mengarah kuat ke arah 
                <b>PC1 Positif (Kanan)</b>. Provinsi yang berada di kuadran kanan menikmati capaian kesehatan dan infrastruktur dasar yang mapan, 
                sedangkan provinsi di ujung kiri mengalami defisit kesejahteraan akut.
            </li>
            <li>
                <b>PC2 (Sumbu Vertikal - 14,75% Variansi) — "Dinamika Ketenagakerjaan vs Skala Ekonomi & Digital":</b><br>
                Sumbu ini memisahkan daerah berdasarkan dinamika penyerapan tenaga kerja. Bagian atas didorong oleh angka pengangguran terdaftar, 
                sedangkan bagian bawah ditarik oleh <code>PDRB_Kapita</code> raksasa dan konektivitas sinyal internet.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.subheader('Visualisasi 1: "Standardized PCA Biplot: Sebaran Provinsi & Kontribusi Indikator"')

    if render_engine.startswith("Plotly"):
        # Plotly Interactive Biplot
        fig_biplot = go.Figure()

        # Tambahkan scatter plot per klaster
        for c in sorted(df_main['Cluster'].unique()):
            sub = filtered_df[filtered_df['Cluster'] == c]
            if len(sub) == 0:
                continue
            fig_biplot.add_trace(go.Scatter(
                x=sub['PC1'],
                y=sub['PC2'],
                mode='markers+text',
                name=CLUSTER_NAMES.get(c, f"Cluster {c}"),
                marker=dict(
                    size=12,
                    color=CLUSTER_COLORS.get(c, '#7f7f7f'),
                    opacity=0.85,
                    line=dict(width=1, color='white')
                ),
                text=[row['Provinsi'] if (row['Status_Outlier'] == 'Outlier' or abs(row['PC1']) > 2.5 or abs(row['PC2']) > 1.8) else '' for _, row in sub.iterrows()],
                textposition='top right',
                textfont=dict(size=10, family='Plus Jakarta Sans', color='#1e293b'),
                customdata=np.stack((
                    sub['Provinsi'],
                    sub['Cluster'],
                    sub['Status_Outlier'],
                    sub['IPM'],
                    sub['Sanitasi'],
                    sub['PDRB Kapita'] if 'PDRB Kapita' in sub.columns else sub['PDRB_Kapita'],
                    sub['Pekerja Formal'] if 'Pekerja Formal' in sub.columns else sub['Pekerja_Formal']
                ), axis=-1),
                hovertemplate="<b>%{customdata[0]}</b><br>" +
                              "Klaster: %{customdata[1]} | Status: %{customdata[2]}<br>" +
                              "PC1: %{x:.2f} | PC2: %{y:.2f}<br>" +
                              "IPM: %{customdata[3]:.2f}<br>" +
                              "Akses Sanitasi: %{customdata[4]:.1f}%<br>" +
                              "PDRB Kapita: Rp %{customdata[5]:,.0f}<br>" +
                              "Pekerja Formal: %{customdata[6]:.1f}%<extra></extra>"
            ))

        # Sorot Outlier dengan cincin merah
        if highlight_outlier:
            outliers = filtered_df[filtered_df['Status_Outlier'] == 'Outlier']
            if len(outliers) > 0:
                fig_biplot.add_trace(go.Scatter(
                    x=outliers['PC1'],
                    y=outliers['PC2'],
                    mode='markers',
                    name='Pencilan (Outlier)',
                    marker=dict(
                        size=24,
                        color='rgba(0,0,0,0)',
                        line=dict(color='#dc2626', width=2.5)
                    ),
                    hoverinfo='skip'
                ))

        # Gambar Vektor Panah Loading
        loadings = pca_model.components_
        for i, feat in enumerate(features):
            vx = loadings[0, i] * arrow_scale
            vy = loadings[1, i] * arrow_scale
            fig_biplot.add_annotation(
                ax=0, ay=0,
                x=vx, y=vy,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1.2,
                arrowwidth=2,
                arrowcolor='#dc2626'
            )
            fig_biplot.add_annotation(
                x=vx * 1.12, y=vy * 1.12,
                text=f"<b>{feat.replace('_', ' ')}</b>",
                showarrow=False,
                font=dict(color='#991b1b', size=11, family='Plus Jakarta Sans'),
                bgcolor='rgba(255,255,255,0.7)'
            )

        # Garis Sumbu 0
        fig_biplot.add_hline(y=0, line_dash='dash', line_color='#94a3b8', line_width=1)
        fig_biplot.add_vline(x=0, line_dash='dash', line_color='#94a3b8', line_width=1)

        fig_biplot.update_layout(
            title=dict(
                text="<b>Standardized PCA Biplot: Sebaran Provinsi & Kontribusi Indikator</b><br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>",
                font=dict(size=17, color='#0f172a')
            ),
            xaxis=dict(
                title=f"PC1 ({exp_var_pct[0]:.2f}% Explained Variance) — Indeks Kesejahteraan & Layanan Dasar",
                gridcolor='#f1f5f9',
                zeroline=False
            ),
            yaxis=dict(
                title=f"PC2 ({exp_var_pct[1]:.2f}% Explained Variance) — Ketenagakerjaan vs Skala Ekonomi",
                gridcolor='#f1f5f9',
                zeroline=False
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            height=680,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1,
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#e2e8f0',
                borderwidth=1
            ),
            margin=dict(l=50, r=50, t=90, b=50)
        )
        st.plotly_chart(fig_biplot, use_container_width=True)
        st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")

    else:
        # Matplotlib Orisinil Notebook
        fig, ax = plt.subplots(figsize=(13, 9), facecolor='white')
        for c in sorted(df_main['Cluster'].unique()):
            sub = filtered_df[filtered_df['Cluster'] == c]
            if len(sub) == 0:
                continue
            ax.scatter(
                sub['PC1'], sub['PC2'],
                label=f'Cluster {c}',
                color=CLUSTER_COLORS.get(c, '#7f7f7f'),
                s=110,
                alpha=0.85,
                edgecolors='none'
            )

        if highlight_outlier:
            outliers = filtered_df[filtered_df['Status_Outlier'] == 'Outlier']
            if len(outliers) > 0:
                ax.scatter(
                    outliers['PC1'], outliers['PC2'],
                    edgecolors='red',
                    facecolors='none',
                    s=250,
                    linewidths=2.5,
                    label='Pencilan (Outlier)'
                )

        for i, row in filtered_df.iterrows():
            if row['Status_Outlier'] == 'Outlier' or abs(row['PC1']) > 3.0 or abs(row['PC2']) > 1.5:
                ax.annotate(
                    row['Provinsi'],
                    (row['PC1'], row['PC2']),
                    xytext=(6, 6),
                    textcoords='offset points',
                    fontsize=9,
                    weight='bold'
                )

        loadings = pca_model.components_
        for i, feature in enumerate(features):
            ax.arrow(
                0, 0,
                loadings[0, i] * arrow_scale,
                loadings[1, i] * arrow_scale,
                color='#d62728',
                alpha=0.9,
                head_width=0.15,
                length_includes_head=True,
                linewidth=1.8
            )
            ax.text(
                loadings[0, i] * arrow_scale * 1.12,
                loadings[1, i] * arrow_scale * 1.12,
                feature,
                color='darkred',
                ha='center',
                va='center',
                fontsize=9.5,
                weight='bold'
            )

        ax.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.7)
        ax.axvline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.7)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_xlabel(f"PC1 ({exp_var_pct[0]:.2f}% Explained Variance)", fontsize=12)
        ax.set_ylabel(f"PC2 ({exp_var_pct[1]:.2f}% Explained Variance)", fontsize=12)
        ax.set_title("Standardized PCA Biplot: Sebaran Provinsi & Kontribusi Indikator\nSumber: BPS (Badan Pusat Statistik)", fontsize=13, weight='bold', pad=15)
        ax.legend(loc='upper right', frameon=True, shadow=True)
        plt.tight_layout()
        st.pyplot(fig)
        st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")
        plt.close(fig)

    # Tabel Loading Indikator
    with st.expander("📊 Lihat Tabel Bobot (Loading Matrix) PC1 & PC2"):
        df_loadings_display = df_loadings.copy()
        df_loadings_display.columns = [f'PC1 ({exp_var_pct[0]:.1f}%)', f'PC2 ({exp_var_pct[1]:.1f}%)']
        st.dataframe(df_loadings_display.style.background_gradient(cmap='coolwarm', axis=0).format('{:.4f}'), use_container_width=True)

# =============================================================================
# TAB 2: Clustered Heatmap
# =============================================================================
with tab2:
    st.markdown("""
    <div class="story-card">
        <h4>🗺️ Narasi Bab 2: Hierarki Spasial & Kovariansi Indikator Multidimensi</h4>
        <p>
            <b>Clustered Heatmap</b> menyusun ulang baris (38 Provinsi) dan kolom (10 Indikator) berdasarkan kesamaan profil numerik 
            menggunakan algoritma <i>Hierarchical Agglomerative Clustering (Dendrogram)</i>:
        </p>
        <ul>
            <li>
                <b>Pengelompokan Indikator (Dendrogram Atas):</b><br>
                Terbentuk blok korelasi yang sangat kuat antara <code>IPM</code>, <code>Sanitasi</code>, <code>Pekerja_Formal</code>, 
                dan indikator kesehatan dasar (angka kematian bayi & kedalaman kemiskinan). Hal ini membuktikan bahwa wilayah yang maju 
                tidak hanya unggul pada satu aspek, melainkan menikmati <i>keuntungan terpadu</i> di seluruh spektrum layanan dasar.
            </li>
            <li>
                <b>Pemisahan Wilayah (Dendrogram Kiri):</b><br>
                Warna merah hangat melambangkan nilai Z-score di atas rata-rata nasional, sedangkan warna biru dingin menunjukkan 
                keterbelakangan. Blok biru tua yang pekat pada bagian bawah merepresentasikan klaster Papua (khususnya Papua Pegunungan 
                dan Papua Tengah), di mana akses sanitasi layak dan porsi tenaga kerja formal anjlok drastis di bawah 3 standar deviasi.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.subheader('Visualisasi 2: "Clustered Heatmap: Pengelompokan Hierarki Provinsi & Variabel"')

    col_h1, col_h2 = st.columns([3, 1])
    with col_h2:
        st.markdown("##### 📌 Interpretasi Skala Z-Score:")
        st.markdown("""
        - <span style="color:#d73027; font-weight:bold;">Merah / Oranye (Z > 0):</span><br>Capaian indikator berada di atas rata-rata nasional.
        - <span style="color:#ffffbf; font-weight:bold;">Kuning (Z ≈ 0):</span><br>Mendekati rata-rata nasional.
        - <span style="color:#4575b4; font-weight:bold;">Biru (Z < 0):</span><br>Capaian indikator tertinggal di bawah rata-rata nasional.
        - <span style="font-weight:600;">Garis Batang Warna Samping (Ramah Buta Warna):</span><br>
          <span style="color:#0072B2;">■</span> Klaster 2 (Maju)<br>
          <span style="color:#E69F00;">■</span> Klaster 0 (Berkembang)<br>
          <span style="color:#D55E00;">■</span> Klaster 1 (Rentan)
        """, unsafe_allow_html=True)

    with col_h1:
        # Clustered Heatmap Seaborn dari Notebook Cell 16
        row_colors = df_main.set_index('Provinsi')['Cluster'].map(CLUSTER_COLORS)
        df_hm = df_scaled.copy()

        g = sns.clustermap(
            df_hm,
            cmap='RdYlBu_r',
            center=0,
            row_colors=row_colors,
            linewidths=.15,
            figsize=(11, 13),
            cbar_kws={'label': 'Z-Score (Standarisasi)'}
        )
        g.figure.suptitle("Clustered Heatmap: Pengelompokan Hierarki Provinsi & Variabel\nSumber: BPS (Badan Pusat Statistik)", y=1.02, fontsize=13, weight='bold')
        st.pyplot(g.figure)
        st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")
        plt.close('all')

# =============================================================================
# TAB 3: Parallel Coordinates Plot
# =============================================================================
with tab3:
    st.markdown("""
    <div class="story-card">
        <h4>📈 Narasi Bab 3: Menelusuri Trajektori Profil Multidimensi Antar-Klaster</h4>
        <p>
            <b>Parallel Coordinates Plot</b> memproyeksikan profil setiap provinsi melintasi seluruh 10 indikator secara bersamaan. 
            Garis-garis yang menghubungkan antar-sumbu vertikal memperlihatkan <i>sidik jari pembangunan</i> yang sangat kontras antar ketiga klaster:
        </p>
        <ul>
            <li>
                <span class="badge-c2">Klaster 2 (Garis Biru - Maju):</span><br>
                Memiliki trajektori stabil di posisi atas pada IPM (rata-rata 74,67), sanitasi layak (87,60%), dan serapan tenaga kerja formal (44,26%). 
                Kelompok ini didominasi provinsi-provinsi di Pulau Jawa, Bali, dan Kalimantan Timur.
            </li>
            <li>
                <span class="badge-c0">Klaster 0 (Garis Oranye - Berkembang):</span><br>
                Kelompok transisi dengan IPM moderat (70,96). Garis-garisnya terkonsentrasi di pita tengah, menunjukkan fondasi dasar 
                yang cukup namun masih membutuhkan akselerasi industrialisasi dan pendidikan tinggi.
            </li>
            <li>
                <span class="badge-c1">Klaster 1 (Garis Merah/Vermilion - Rentan Ekstrem):</span><br>
                Menukik tajam ke dasar grafik pada variabel sanitasi (hanya 28,04%) dan pekerja formal (hanya 9,99%), serta melonjak 
                pada kedalaman kemiskinan dan blank spot sinyal.
            </li>
        </ul>
        <p style="font-size:0.88rem; color:#64748b; margin-top:8px;">
            💡 <i>Tips Interaktif: Anda dapat menarik kursor pada garis sumbu vertikal mana pun untuk menyaring (brushing) provinsi dengan rentang nilai tertentu!</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader('Visualisasi 3: "Parallel Coordinates Plot: Profil Multidimensi 38 Provinsi Berdasarkan Klaster"')

    df_parallel = filtered_df.copy()
    df_parallel['Cluster_Code'] = df_parallel['Cluster'].astype(int)

    fig_parallel = px.parallel_coordinates(
        df_parallel,
        dimensions=features,
        color='Cluster_Code',
        color_continuous_scale=[
            (0.0, '#E69F00'),  # Cluster 0 (Berkembang)
            (0.5, '#D55E00'),  # Cluster 1 (Rentan)
            (1.0, '#0072B2')   # Cluster 2 (Maju)
        ],
        labels={col: col.replace('_', ' ') for col in features}
    )

    fig_parallel.update_layout(
        title=dict(
            text="<b>Parallel Coordinates Plot: Profil Multidimensi 38 Provinsi Berdasarkan Klaster</b><br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>",
            font=dict(size=16, color='#0f172a')
        ),
        margin=dict(l=60, r=60, t=80, b=40),
        coloraxis_colorbar=dict(
            title="Klaster",
            tickvals=[0, 1, 2],
            ticktext=["Klaster 0 (Berkembang)", "Klaster 1 (Rentan)", "Klaster 2 (Maju)"]
        )
    )

    st.plotly_chart(fig_parallel, use_container_width=True)
    st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")

    # Ringkasan Profil Rata-Rata Klaster
    st.markdown("#### 📋 Tabel Profil Rata-Rata & Median Tiap Klaster")
    profile_mean = df_main.groupby('Cluster')[features].mean()
    profile_median = df_main.groupby('Cluster')[features].median()

    tab_p1, tab_p2 = st.tabs(["Rata-Rata (Mean)", "Nilai Tengah (Median)"])
    with tab_p1:
        st.dataframe(profile_mean.style.format('{:.2f}').background_gradient(cmap='YlGnBu', axis=0), use_container_width=True)
    with tab_p2:
        st.dataframe(profile_median.style.format('{:.2f}').background_gradient(cmap='YlGnBu', axis=0), use_container_width=True)

# =============================================================================
# TAB 4: Investigasi Pencilan (Outliers)
# =============================================================================
with tab4:
    st.markdown("""
    <div class="story-card">
        <h4>🔍 Narasi Bab 4: Anomali Spasial & Potret Daerah Pencilan (Isolation Forest)</h4>
        <p>
            Model <i>Isolation Forest</i> dengan laju kontaminasi terkalibrasi secara matematis mengidentifikasi 
            <b>empat provinsi pencilan (outliers)</b> yang memiliki konfigurasi indikator sangat unik di dalam ruang geometris PCA:
        </p>
    </div>
    """, unsafe_allow_html=True)

    outliers_df = df_main[df_main['Status_Outlier'] == 'Outlier'].copy()

    col_o1, col_o2 = st.columns([1, 1])

    with col_o1:
        st.markdown("##### 📌 Tabel Daftar Provinsi Pencilan:")
        st.dataframe(
            outliers_df[['Provinsi', 'PC1', 'PC2', 'Cluster', 'IPM', 'Sanitasi', 'P0_Kemiskinan', 'PDRB Kapita' if 'PDRB Kapita' in outliers_df.columns else 'PDRB_Kapita']]
            .style.format({'PC1': '{:.2f}', 'PC2': '{:.2f}', 'IPM': '{:.2f}', 'Sanitasi': '{:.1f}%', 'P0_Kemiskinan': '{:.2f}%'}),
            use_container_width=True
        )

        st.markdown("""
        <div style="background:#f8fafc; border-radius:12px; padding:1.2rem; border:1px solid #e2e8f0; margin-top:1rem;">
            <h5 style="color:#0f172a; margin-top:0;">💡 Mengapa Wilayah Ini Terisolasi?</h5>
            <ol style="font-size:0.92rem; color:#334155; line-height:1.6; padding-left:1.2rem;">
                <li><b>DKI JAKARTA (PC1: 4.46, PC2: -2.78):</b><br>
                Menempati kuadran kanan bawah karena skala ekonominya yang sangat masif (PDRB per kapita > Rp 200 juta dan sanitasi 95%+), 
                namun dibayangi friksi pengangguran terbuka perkotaan yang tinggi.</li>
                <li><b>PAPUA PEGUNUNGAN (PC1: -7.64, PC2: 1.64) & PAPUA TENGAH (PC1: -6.06, PC2: -1.33):</b><br>
                Terlempar ke ujung kiri terjauh ruang PCA akibat kombinasi keterisolasian topografi, kemiskinan ekstrem (P0 > 28%), 
                dan infrastruktur sanitasi yang belum menjangkau mayoritas penduduk.</li>
                <li><b>PAPUA BARAT DAYA (PC1: -1.71, PC2: -2.49):</b><br>
                Memiliki PDRB per kapita sektor ekstraktif yang cukup tinggi namun penyerapan kerja formalnya masih rendah.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col_o2:
        # Scatter komparasi Outlier di ruang PCA
        fig_out = px.scatter(
            df_main,
            x='PC1',
            y='PC2',
            color='Status_Outlier',
            color_discrete_map={'Normal': '#0072B2', 'Outlier': '#D55E00'},
            symbol='Status_Outlier',
            symbol_map={'Normal': 'circle', 'Outlier': 'diamond'},
            size=[20 if s == 'Outlier' else 9 for s in df_main['Status_Outlier']],
            text='Provinsi'
        )
        fig_out.update_traces(textposition='top center', textfont=dict(size=9))
        fig_out.update_layout(
            title=dict(
                text="<b>Posisi Geometris Pencilan dalam Ruang Koordinat PCA</b><br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>",
                font=dict(size=15, color='#0f172a')
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            height=480,
            margin=dict(l=40, r=40, t=65, b=40)
        )
        st.plotly_chart(fig_out, use_container_width=True)
        st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")

# =============================================================================
# TAB 5: Visualisasi Hierarki Kemiskinan (Treemap & Sunburst)
# =============================================================================
with tab5:
    df_kab_h, df_prov_h, df_pulau_h = load_hierarki_data()
    st.markdown("""
    <div class="story-card">
        <h4>📊 Narasi Bab 5: Visualisasi Hierarki Multilevel Kemiskinan Indonesia (Treemap & Sunburst)</h4>
        <p>
            Visualisasi hierarki ini memetakan konsentrasi kemiskinan secara sistematis melintasi 3 tingkatan wilayah administratif: 
            <b>Level 1: Pulau</b> (6 Wilayah) &rarr; <b>Level 2: Provinsi</b> (38 Provinsi) &rarr; <b>Level 3: Kabupaten / Kota</b> (514 Daerah).
        </p>
        <ul>
            <li>
                <b>Luas Area / Ukuran Sektor (Size = Total Penduduk Kemiskinan):</b><br>
                Besar-kecilnya kotak pada Treemap dan sektor/radius pada Sunburst mencerminkan <b>Jumlah Total Penduduk Miskin (Ribu Jiwa)</b>. 
                Semakin luas suatu kotak atau sektor, semakin masif jumlah jiwa penduduk miskin yang berada di wilayah tersebut (di-SUM dari level di bawahnya).
            </li>
            <li>
                <b>Intensitas Warna (Color = P0 Persentase Penduduk Miskin):</b><br>
                Gradasi warna sekensial merah (<i>Reds</i>) menunjukkan <b>Tingkat Persentase Kemiskinan (P0)</b>. 
                Semakin gelap/pekat warna merah, semakin tinggi persentase proporsi penduduk miskin di wilayah tersebut.
            </li>
            <li>
                <b>Navigasi Interaktif (Drill-down & Zoom):</b><br>
                Klik pada sektor <b>Pulau</b> untuk melakukan drill-down ke level <b>Provinsi</b>, dan klik pada <b>Provinsi</b> untuk mendalami level <b>Kabupaten/Kota</b>. 
                Gunakan navigasi breadcrumb di bagian atas atau klik area tengah untuk kembali ke level root sebelumnya.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_h1, col_h2 = st.columns([3, 1])
    with col_h2:
        color_scheme_h = st.selectbox("🎨 Skala Warna Gradasi P0 (Ramah Buta Warna):", ["Viridis", "Cividis", "YlOrRd", "YlGnBu", "Plasma", "Reds", "OrRd"], index=0)
        st.markdown("""
        <div style="background:#fff7ed; border:1px solid #fed7aa; border-radius:10px; padding:12px; margin-top:10px;">
            <h6 style="color:#c2410c; margin:0 0 6px 0; font-weight:700;">💡 Panduan Membaca Hierarki</h6>
            <p style="font-size:0.83rem; color:#431407; margin:0; line-height:1.5;">
                • <b>Ukuran/Luas:</b> Total Penduduk Miskin (Jiwa)<br>
                • <b>Warna:</b> Persentase Kemiskinan P0 (%)<br>
                • <b>Drill-Down:</b> Klik sektor untuk memperbesar level
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h1:
        tab_tree, tab_sun = st.tabs(["🌳 Treemap Interaktif (Drill-Down)", "☀️ Sunburst Interaktif (Radial Zoom)"])
        
        with tab_tree:
            fig_tree = generate_hierarchical_figure('treemap', color_scale=color_scheme_h)
            if fig_tree:
                st.plotly_chart(fig_tree, use_container_width=True)
                st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")
            else:
                st.error("Data hierarki_tingkat.xlsx tidak ditemukan.")
                
        with tab_sun:
            fig_sun = generate_hierarchical_figure('sunburst', color_scale=color_scheme_h)
            if fig_sun:
                st.plotly_chart(fig_sun, use_container_width=True)
                st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")
            else:
                st.error("Data hierarki_tingkat.xlsx tidak ditemukan.")

# =============================================================================
# TAB 6: Peta Geospasial P0 & P1 Per Kabupaten/Kota (514 Kabupaten/Kota)
# =============================================================================
with tab6:
    geojson_data = load_geojson()
    st.markdown("""
    <div class="story-card">
        <h4>🌐 Narasi Bab 6: Visualisasi Geospasial Kemiskinan Tingkat Kabupaten / Kota se-Indonesia (514 Daerah)</h4>
        <p>
            Visualisasi peta geospasial interaktif berbasis <b>OpenStreetMap</b> ini memetakan data detail tingkat <b>Kabupaten / Kota (514 Daerah)</b> 
            menggunakan dua visualisasi dengan <i>visual encoding</i> yang berbeda dan disesuaikan secara tepat dengan karakteristik indikatornya:
        </p>
        <ul>
            <li>
                <b>Peta 1: Choropleth Persentase Penduduk Miskin (P0):</b><br>
                P0 menunjukkan proporsi penduduk miskin di setiap kabupaten/kota sehingga sangat cocok divisualisasikan dengan <b>Choropleth Map</b> 
                (gradasi warna pada polygon wilayah) untuk mengamati pola spasial dan konsentrasi wilayah kemiskinan secara komprehensif. 
                Semakin pekat warna merah, semakin tinggi persentase penduduk miskin di daerah tersebut.
            </li>
            <li>
                <b>Peta 2: Proportional Symbol Indeks Kedalaman Kemiskinan (P1):</b><br>
                P1 menunjukkan kedalaman kemiskinan (jarak rata-rata pengeluaran penduduk miskin terhadap Garis Kemiskinan), sehingga 
                <b>Proportional Symbol Map</b> (ukuran lingkaran) digunakan untuk menonjolkan perbedaan tingkat kedalaman secara visual melalui variasi ukuran simbol. 
                Semakin besar lingkaran, semakin parah dan dalam tingkat kemiskinan di kabupaten/kota tersebut.
            </li>
        </ul>
        <p style="font-size:0.88rem; color:#64748b; margin-top:8px;">
            💡 <i>Dengan demikian, kedua peta memiliki encoding visual yang berbeda (gradasi polygon vs ukuran simbol) dan disesuaikan secara tepat dengan karakteristik indikator masing-masing.</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Filter Provinsi khusus untuk Peta Kabupaten/Kota
    prov_options = ["SEMUA PROVINSI (514 Kab/Kota)"] + sorted(df_kab['Provinsi'].unique())
    selected_prov_filter = st.selectbox("🎯 Filter Wilayah Provinsi untuk Peta Kabupaten/Kota:", options=prov_options, index=0)

    if selected_prov_filter != "SEMUA PROVINSI (514 Kab/Kota)":
        df_kab_filtered = df_kab[df_kab['Provinsi'] == selected_prov_filter].copy()
    else:
        df_kab_filtered = df_kab.copy()

    st.markdown("---")
    st.subheader('🗺️ Peta 1: Choropleth Persentase Penduduk Miskin (P0)')

    col_map1_c1, col_map1_c2 = st.columns([3, 1])
    with col_map1_c2:
        color_scheme_p0 = st.selectbox("Skala Warna P0 (Ramah Buta Warna):", ["Viridis", "Cividis", "YlOrRd", "YlGnBu", "Reds"], index=0)
        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px; margin-top:10px;">
            <h6 style="color:#0f172a; margin:0 0 6px 0; font-weight:700;">🎨 Legenda Peta 1 (P0 Choropleth)</h6>
            <p style="font-size:0.83rem; color:#334155; margin:0; line-height:1.5;">
                • <b>Polygon Fill:</b> Setiap polygon kabupaten/kota diberi warna berdasarkan nilai P0.<br>
                • <b>Skala Berurutan (Sequential):</b> Warna semakin pekat menandakan P0 (%) semakin tinggi.<br>
                • <b>Tanpa Simbol/Lingkaran:</b> Peta P0 merepresentasikan wilayah secara murni melalui polygon.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_map1_c1:
        if geojson_data:
            fig_map_p0 = px.choropleth_map(
                df_kab_filtered,
                geojson=geojson_data,
                locations='shapeName',
                featureidkey='properties.shapeName',
                color='P0_Kemiskinan',
                color_continuous_scale=color_scheme_p0,
                zoom=3.8 if selected_prov_filter == "SEMUA PROVINSI (514 Kab/Kota)" else 6.5,
                center={'lat': df_kab_filtered['lat'].mean(), 'lon': df_kab_filtered['lon'].mean()},
                map_style='open-street-map',
                hover_name='Kabupaten_Kota',
                hover_data={
                    'Provinsi': True,
                    'P0_Kemiskinan': ':.2f%',
                    'shapeName': False,
                    'lat': False,
                    'lon': False
                },
                labels={'P0_Kemiskinan': 'Persentase Penduduk Miskin (P0)', 'Provinsi': 'Provinsi', 'Kabupaten_Kota': 'Kabupaten/Kota'}
            )
            fig_map_p0.update_traces(marker_opacity=0.75, marker_line_width=0.6, marker_line_color='#475569')
        else:
            fig_map_p0 = px.scatter_map(
                df_kab_filtered,
                lat='lat',
                lon='lon',
                color='P0_Kemiskinan',
                color_continuous_scale=color_scheme_p0,
                zoom=3.8 if selected_prov_filter == "SEMUA PROVINSI (514 Kab/Kota)" else 6.5,
                center={'lat': df_kab_filtered['lat'].mean(), 'lon': df_kab_filtered['lon'].mean()},
                map_style='open-street-map',
                hover_name='Kabupaten_Kota',
                hover_data={
                    'Provinsi': True,
                    'P0_Kemiskinan': ':.2f%',
                    'lat': False,
                    'lon': False
                },
                labels={'P0_Kemiskinan': 'Persentase Penduduk Miskin (P0)', 'Provinsi': 'Provinsi', 'Kabupaten_Kota': 'Kabupaten/Kota'}
            )
        fig_map_p0.update_layout(
            title=dict(
                text=f'<b>Peta Choropleth P0 — Persentase Penduduk Miskin ({len(df_kab_filtered)} Kabupaten/Kota)</b><br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>',
                font=dict(size=16, color='#0f172a')
            ),
            height=580,
            margin=dict(l=10, r=10, t=65, b=10),
            coloraxis_colorbar=dict(title="Persentase Penduduk Miskin (P0)", ticksuffix="%")
        )
        st.plotly_chart(fig_map_p0, use_container_width=True)
        st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")

    st.markdown("---")
    st.subheader('🔴 Peta 2: Proportional Symbol Indeks Kedalaman Kemiskinan (P1)')

    col_map2_c1, col_map2_c2 = st.columns([3, 1])
    with col_map2_c2:
        size_p1 = st.slider("Ukuran Maksimum Simbol P1:", min_value=12, max_value=45, value=30, step=2)
        st.markdown("""
        <div style="background:#fff7ed; border:1px solid #fed7aa; border-radius:10px; padding:12px; margin-top:10px;">
            <h6 style="color:#c2410c; margin:0 0 6px 0; font-weight:700;">⭕ Legenda Ukuran Simbol P1</h6>
            <p style="font-size:0.83rem; color:#431407; margin:0; line-height:1.5;">
                • <b>Ukuran Lingkaran:</b> Proporsional terhadap nilai Indeks P1.<br>
                • <b>Semakin Besar:</b> Kedalaman kemiskinan semakin parah.<br>
                • <b>Semakin Kecil:</b> Kedalaman kemiskinan semakin rendah.<br>
                • <b>Warna Kontras:</b> Basemap netral dengan simbol oranye kontras.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_map2_c1:
        fig_map_p1 = px.scatter_map(
            df_kab_filtered,
            lat='lat',
            lon='lon',
            size='P1_Kedalaman',
            size_max=size_p1,
            color_discrete_sequence=['#D55E00'],
            zoom=3.8 if selected_prov_filter == "SEMUA PROVINSI (514 Kab/Kota)" else 6.5,
            center={'lat': df_kab_filtered['lat'].mean(), 'lon': df_kab_filtered['lon'].mean()},
            map_style='open-street-map',
            hover_name='Kabupaten_Kota',
            hover_data={
                'Provinsi': True,
                'P1_Kedalaman': ':.2f',
                'lat': False,
                'lon': False
            },
            labels={'P1_Kedalaman': 'Indeks Kedalaman Kemiskinan (P1)', 'Provinsi': 'Provinsi', 'Kabupaten_Kota': 'Kabupaten/Kota'}
        )
        fig_map_p1.update_traces(marker=dict(opacity=0.85))
        fig_map_p1.update_layout(
            title=dict(
                text=f'<b>Peta Proportional Symbol P1 — Indeks Kedalaman Kemiskinan ({len(df_kab_filtered)} Kabupaten/Kota)</b><br><sup>Sumber: BPS (Badan Pusat Statistik)</sup>',
                font=dict(size=16, color='#0f172a')
            ),
            height=580,
            margin=dict(l=10, r=10, t=65, b=10)
        )
        st.plotly_chart(fig_map_p1, use_container_width=True)
        st.caption("📌 *Sumber Data: BPS (Badan Pusat Statistik)*")

    # 📊 Ringkasan Peringkat Kabupaten/Kota
    st.markdown("#### 🏆 Peringkat Ekstrem Kabupaten / Kota (514 Daerah)")
    col_rk1, col_rk2, col_rk3 = st.columns(3)

    with col_rk1:
        st.markdown("##### 🚨 5 Kab/Kota P0 Kemiskinan Tertinggi:")
        top_p0 = df_kab.sort_values(by='P0_Kemiskinan', ascending=False).head(5)
        st.dataframe(top_p0[['Kabupaten_Kota', 'Provinsi', 'P0_Kemiskinan', 'P1_Kedalaman']].style.format({'P0_Kemiskinan': '{:.2f}%', 'P1_Kedalaman': '{:.2f}'}), use_container_width=True)

    with col_rk2:
        st.markdown("##### 🚨 5 Kab/Kota Indeks P1 (Kedalaman) Terparah:")
        top_p1 = df_kab.sort_values(by='P1_Kedalaman', ascending=False).head(5)
        st.dataframe(top_p1[['Kabupaten_Kota', 'Provinsi', 'P1_Kedalaman', 'P0_Kemiskinan']].style.format({'P1_Kedalaman': '{:.2f}', 'P0_Kemiskinan': '{:.2f}%'}), use_container_width=True)

    with col_rk3:
        st.markdown("##### ❇️ 5 Kab/Kota P0 Kemiskinan Terendah:")
        bot_p0 = df_kab.sort_values(by='P0_Kemiskinan', ascending=True).head(5)
        st.dataframe(bot_p0[['Kabupaten_Kota', 'Provinsi', 'P0_Kemiskinan', 'P1_Kedalaman']].style.format({'P0_Kemiskinan': '{:.2f}%', 'P1_Kedalaman': '{:.2f}'}), use_container_width=True)



st.markdown("""
<hr style="margin:2.5rem 0 1rem 0; border:none; border-top:1px solid #e2e8f0;">
<div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.85rem;">
    <span>UAS Visualisasi Data • Analisis Disparitas Pembangunan & Peta Geospasial P0/P1 514 Kab/Kota</span>
    <span>Dibangun dengan Streamlit, Plotly (OpenStreetMap), Seaborn, & Scikit-Learn</span>
</div>
""", unsafe_allow_html=True)
