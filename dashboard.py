import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff 
import time

# 1. Konfigurasi Halaman & CSS untuk Sidebar
st.set_page_config(
    page_title="Dashboard Tren Genre Film IMDb", 
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom untuk Styling dan Sidebar
st.markdown("""
<style>
    /* Sidebar styling - lebih compact */
    section[data-testid="stSidebar"] {
        width: 250px !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 0.85rem;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > label {
        font-size: 0.85rem;
    }
    
    section[data-testid="stSidebar"] h1 {
        font-size: 1.2rem !important;
    }
    
    section[data-testid="stSidebar"] h2 {
        font-size: 1.1rem !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        font-size: 1rem !important;
    }
    
    section[data-testid="stSidebar"] .stNumberInput > label {
        font-size: 0.85rem;
    }
    
    /* Customize sidebar toggle button */
    button[data-testid="collapsedControl"] {
        background-color: #f5c518;
        color: #000;
        padding: 0.5rem;
        border-radius: 0 5px 5px 0;
        width: auto;
    }
    
    button[data-testid="collapsedControl"]:hover {
        background-color: #e4b308;
    }
    
    button[data-testid="collapsedControl"]:after {
        content: " Menu";
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    /* Main header styling - lebih besar */
    .main-header {
        background: linear-gradient(135deg, #f5c518 0%, #e4b308 100%);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        color: #000000;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        font-size: 2.5rem !important;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.1rem;
        margin: 0;
    }

    /* KPI card styling - font lebih kecil */
    .kpi-card {
        background-color: #1a1a1a;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #333;
        height: 100%;
    }
    .kpi-value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #f5c518;
        margin-bottom: 0.2rem;
    }
    .kpi-label {
        color: #aaa;
        font-size: 0.65rem;
        text-transform: uppercase;
    }
    
    /* Subheader styling - lebih kecil dari judul utama */
    .stApp h2 {
        font-size: 1.3rem !important;
    }
    
    .stApp h3 {
        font-size: 1.1rem !important;
    }

    /* Custom button styling */
    .stButton > button {
        background-color: #f5c518;
        color: #000;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.3rem 0.6rem;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #e4b308;
        transform: translateY(-2px);
    }

    /* Container utama Streamlit: atur padding atas-bawah */
    .css-1lcbmhc.e1tzin5v0 {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    
    /* Vertical divider styling */
    .vertical-divider {
        border-left: 1px solid #333;
        height: 100%;
        margin: 0 1rem;
    }
    
    /* Column with border */
    .chart-container {
        padding-right: 1rem;
        border-right: 1px solid #333;
    }
    
    .chart-container-right {
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# 2. Fungsi Muat dan Siapkan Data
@st.cache_data
def load_data():
    """Memuat dan menyiapkan dataset IMDb"""
    try:
        df = pd.read_csv('IMDb_Data_final.csv')
    except FileNotFoundError:
        st.error("File 'IMDb_Data_final.csv' tidak ditemukan. Pastikan file berada di direktori yang sama dengan skrip.")
        return pd.DataFrame(), pd.DataFrame()

    df['ReleaseYear'] = pd.to_numeric(df['ReleaseYear'], errors='coerce')
    df.dropna(subset=['ReleaseYear'], inplace=True)
    if df['ReleaseYear'].empty:
        st.warning("Kolom 'ReleaseYear' tidak memiliki data numerik yang valid.")
        return pd.DataFrame(), pd.DataFrame()

    df['ReleaseYear'] = df['ReleaseYear'].astype(int)
    df['Decade'] = (df['ReleaseYear'] // 10) * 10
    df['Decade_Label'] = df['Decade'].astype(str) + 's'

    def clean_duration(duration_str):
        if pd.isna(duration_str):
            return None
        cleaned = str(duration_str).replace('min', '').strip()
        try:
            return int(cleaned)
        except ValueError:
            return None
    df['Duration_Clean'] = df['Duration'].apply(clean_duration)

    genres_expanded = []
    for idx, row in df.iterrows():
        if pd.notna(row['Category']):
            genres = str(row['Category']).split(',')
            for genre in genres:
                new_row = row.copy()
                new_row['Genre'] = genre.strip()
                if new_row['Genre']:
                    genres_expanded.append(new_row)
        else:
            new_row = row.copy()
            new_row['Genre'] = 'Unknown'
            genres_expanded.append(new_row)

    if not genres_expanded:
        df_expanded = pd.DataFrame(columns=list(df.columns) + ['Genre'])
    else:
        df_expanded = pd.DataFrame(genres_expanded)

    if 'Duration_Clean' in df_expanded.columns:
        df_expanded = df_expanded.dropna(subset=['Duration_Clean'])
    if 'Genre' in df_expanded.columns:
        df_expanded = df_expanded[df_expanded['Genre'] != '']

    return df, df_expanded


df_original, df_expanded = load_data()


# Palet Warna Genre (konsisten dengan tema IMDb)
genre_color_map = {
    'Drama': '#E53935', 'Action': '#1E88E5', 'Comedy': '#FFB300', 
    'Crime': '#546E7A', 'Thriller': '#8E24AA', 'Romance': '#D81B60', 
    'Adventure': '#43A047', 'Sci-Fi': '#039BE5', 'Horror': '#6D4C41', 
    'Western': '#A1887F', 'Animation': '#00ACC1', 'Family': '#7CB342', 
    'Mystery': '#3949AB', 'Fantasy': '#D500F9', 'Biography': '#757575', 
    'Music': '#F06292', 'War': '#556B2F', 'History': '#8D6E63', 
    'Sport': '#C0CA33', 'Musical': '#BA68C8', 'Film-Noir': '#37474F', 
    'Documentary': '#FF8F00', 'Short': '#64B5F6', 'Talk-Show': '#4DB6AC', 
    'News': '#9E9E9E', 'Reality-TV': '#795548', 'Adult': '#E91E63', 
    'Game-Show': '#AED581', 'Unknown': '#BDBDBD'
}


# 3. Cek Ketersediaan Data & Sidebar
if df_original.empty or df_expanded.empty or 'ReleaseYear' not in df_expanded.columns or df_expanded['ReleaseYear'].empty:
    st.warning("Gagal memuat atau memproses data, atau data tahun tidak tersedia. Tidak ada yang bisa ditampilkan.")
    st.markdown(f"""
    <div class="main-header">
        <h1>🎬 Dashboard Tren Genre Film IMDb</h1>
        <p>Rentang tahun data tidak dapat ditentukan.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
else:
    min_year_data_available = int(df_expanded['ReleaseYear'].min())
    max_year_data_available = int(df_expanded['ReleaseYear'].max())

    with st.sidebar:
        st.header("🎯 Filter Dashboard")

        # Inisialisasi session_state untuk slider dan inputs
        if 'slider_year_range' not in st.session_state:
            st.session_state.slider_year_range = (min_year_data_available, max_year_data_available)
        if 'start_year_input' not in st.session_state:
            st.session_state.start_year_input = min_year_data_available
        if 'end_year_input' not in st.session_state:
            st.session_state.end_year_input = max_year_data_available

        # Input angka Tahun Awal & Akhir
        col_start_year, col_end_year = st.columns(2)
        with col_start_year:
            start_year_input_val = st.number_input(
                "Tahun Awal:", min_value=min_year_data_available, max_value=max_year_data_available,
                value=st.session_state.start_year_input, step=1, key="start_year_num_input"
            )
        with col_end_year:
            end_year_input_val = st.number_input(
                "Tahun Akhir:", min_value=min_year_data_available, max_value=max_year_data_available,
                value=st.session_state.end_year_input, step=1, key="end_year_num_input"
            )

        # Validasi Tahun
        if start_year_input_val > end_year_input_val:
            st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir.")
            start_year_input_val = st.session_state.start_year_input
            end_year_input_val = st.session_state.end_year_input
        else:
            st.session_state.start_year_input = start_year_input_val
            st.session_state.end_year_input = end_year_input_val
            st.session_state.slider_year_range = (start_year_input_val, end_year_input_val)

        # Slider Rentang Tahun
        selected_year_range_slider = st.slider(
            "Rentang Tahun Rilis:", 
            min_value=min_year_data_available, 
            max_value=max_year_data_available,
            value=st.session_state.slider_year_range, 
            key="year_slider"
        )
        if selected_year_range_slider != st.session_state.slider_year_range:
            st.session_state.slider_year_range = selected_year_range_slider
            st.session_state.start_year_input = selected_year_range_slider[0]
            st.session_state.end_year_input = selected_year_range_slider[1]
            st.rerun()

        selected_year_range = st.session_state.slider_year_range

        # Pilih Genre
        st.markdown("##### Pilih Genre")
        if 'Genre' in df_expanded.columns:
            all_genres = sorted(list(df_expanded['Genre'].unique()))
            # Default top 5 genre
            top_5_genres_overall = df_expanded['Genre'].value_counts().nlargest(5).index.tolist() \
                                   if not df_expanded.empty else []
            valid_top_5_genres = [g for g in top_5_genres_overall if g in all_genres]
            if not valid_top_5_genres and all_genres:
                valid_top_5_genres = all_genres[:min(5, len(all_genres))]

            selected_genres = st.multiselect(
                "Genre yang ditampilkan:", 
                options=all_genres, 
                default=valid_top_5_genres, 
                key="genre_multiselect"
            )
        else:
            selected_genres = []
            st.warning("Kolom 'Genre' tidak ditemukan dalam data.")

# 4. Header Utama & Filter Data
st.markdown(f"""
<div class="main-header">
    <h1>🎬 Dashboard Tren Genre Film IMDb</h1>
    <p>Menganalisis Evolusi Sinema ({selected_year_range[0]}–{selected_year_range[1]})</p>
</div>
""", unsafe_allow_html=True)

df_filtered = df_expanded[
    (df_expanded['ReleaseYear'] >= selected_year_range[0]) &
    (df_expanded['ReleaseYear'] <= selected_year_range[1])
]
if selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
elif not selected_genres and 'Genre' in df_expanded.columns:
    st.sidebar.info("Anda belum memilih genre. Menampilkan data untuk semua genre.")

# 5. KPI Cards (Baris KPI)
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    total_films = df_filtered['Title'].nunique() if not df_filtered.empty else 0
    st.markdown(
        f'<div class="kpi-card">'
        f'  <div class="kpi-value">{total_films:,}</div>'
        f'  <div class="kpi-label">Total Film</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with kpi_col2:
    avg_rating_val = df_filtered['IMDb-Rating'].mean() if not df_filtered.empty and 'IMDb-Rating' in df_filtered.columns else 0
    avg_rating_display = f"{avg_rating_val:.1f}" if pd.notna(avg_rating_val) and avg_rating_val != 0 else "N/A"
    st.markdown(
        f'<div class="kpi-card">'
        f'  <div class="kpi-value">{avg_rating_display}</div>'
        f'  <div class="kpi-label">Rata-Rata Rating</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with kpi_col3:
    avg_duration_val = df_filtered['Duration_Clean'].mean() if not df_filtered.empty and 'Duration_Clean' in df_filtered.columns else 0
    avg_duration_display = f"{avg_duration_val:.0f} menit" if pd.notna(avg_duration_val) and avg_duration_val != 0 else "N/A"
    st.markdown(
        f'<div class="kpi-card">'
        f'  <div class="kpi-value">{avg_duration_display}</div>'
        f'  <div class="kpi-label">Rata-Rata Durasi</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with kpi_col4:
    top_director_name = "N/A"
    if not df_filtered.empty and 'Director' in df_filtered.columns:
        director_counts = df_filtered.groupby('Director')['Title'].nunique().sort_values(ascending=False)
        if not director_counts.empty:
            top_director_name = director_counts.index[0]
    st.markdown(
        f'<div class="kpi-card">'
        f'  <div class="kpi-value" style="font-size:1.2rem; white-space:normal;">{top_director_name}</div>'
        f'  <div class="kpi-label">Sutradara Terpopuler</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin-top:0.5rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)

if df_filtered.empty:
    st.info("Tidak ada data yang cocok dengan filter yang dipilih. Silakan sesuaikan filter Anda.")
    st.stop()


# 6. Baris Visualisasi 1: Produksi Film & Top Genre
st.subheader("📊 Analisis Produksi & Popularitas Genre Film")

# Menggunakan container untuk styling
col1_container = st.container()
with col1_container:
    vis_row1_col1, vis_row1_col2 = st.columns([1, 1])

# 6.1 Produksi Film Tahunan (Stacked Bar) - dengan border kanan
with vis_row1_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.write("##### Produksi Film Tahunan")
    if 'ReleaseYear' in df_filtered.columns and 'Genre' in df_filtered.columns:
        movies_per_year_genre = df_filtered.groupby(['ReleaseYear', 'Genre']).size().reset_index(name='Jumlah Film')
        if not movies_per_year_genre.empty:
            fig_stacked_bar = px.bar(
                movies_per_year_genre,
                x='ReleaseYear', y='Jumlah Film', color='Genre',
                labels={'ReleaseYear': 'Tahun Rilis', 'Jumlah Film': 'Jumlah Film Diproduksi'},
                color_discrete_map=genre_color_map,
                height=300
            )
            fig_stacked_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                legend_title_text='Genre', barmode='stack',
                margin=dict(l=10, r=20, t=30, b=10),
                legend=dict(font=dict(size=10))
            )
            st.plotly_chart(fig_stacked_bar, use_container_width=True)
        else:
            st.info("Tidak ada data produksi film per tahun untuk filter yang dipilih.")
    else:
        st.info("Tidak cukup data untuk menampilkan grafik produksi film per tahun.")
    st.markdown('</div>', unsafe_allow_html=True)

# 6.2 Genre Film Terpopuler (Horizontal Bar) - dengan padding kiri
with vis_row1_col2:
    st.markdown('<div class="chart-container-right">', unsafe_allow_html=True)
    st.write("##### Genre Film Terpopuler")
    if 'Genre' in df_filtered.columns:
        top_10_genres_series = df_filtered['Genre'].value_counts().nlargest(10)
        if not top_10_genres_series.empty:
            top_10_df = top_10_genres_series.reset_index()
            top_10_df.columns = ['Genre', 'Jumlah Instance Genre']
            fig_bar_genre_h = px.bar(
                top_10_df,
                x='Jumlah Instance Genre', y='Genre', orientation='h',
                labels={'Jumlah Instance Genre': 'Jumlah Film', 'Genre': 'Genre'},
                color='Genre', color_discrete_map=genre_color_map,
                height=300
            )
            fig_bar_genre_h.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_bar_genre_h, use_container_width=True)
        else:
            st.info("Tidak ada data genre untuk ditampilkan dengan filter yang dipilih.")
    else:
        st.info("Kolom 'Genre' tidak ditemukan untuk membuat grafik top genre.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr style='margin-top:0.5rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)


# 7. Baris Visualisasi 2: Distribusi Rating & Analisis Sutradara
col2_container = st.container()
with col2_container:
    vis_row2_col1, vis_row2_col2 = st.columns([1, 1])

# 7.1 Distribusi Rating IMDb (Density Plot) - dengan border kanan
with vis_row2_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("⭐ Distribusi Rating IMDb")
    st.write("Sebaran rating IMDb untuk genre yang dipilih.")
    if 'Genre' in df_filtered.columns and 'IMDb-Rating' in df_filtered.columns:
        hist_data_ratings = []
        group_labels_ratings = []
        plot_colors_ratings = []
        genres_in_filtered_data = sorted(list(df_filtered['Genre'].unique()))

        for genre in genres_in_filtered_data:
            genre_ratings = df_filtered[df_filtered['Genre'] == genre]['IMDb-Rating'].dropna()
            if len(genre_ratings) > 1:
                hist_data_ratings.append(genre_ratings.tolist())
                group_labels_ratings.append(genre)
                plot_colors_ratings.append(genre_color_map.get(genre, '#CCCCCC'))

        if hist_data_ratings and group_labels_ratings:
            try:
                fig_dist_rating = ff.create_distplot(
                    hist_data_ratings, group_labels_ratings, colors=plot_colors_ratings,
                    show_hist=False, show_rug=False, bin_size=0.2
                )
                fig_dist_rating.update_layout(
                    title_text='Distribusi Kepadatan Rating IMDb',
                    xaxis_title='Rating IMDb', yaxis_title='Kepadatan',
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    legend_title_text='Genre',
                    height=300,
                    margin=dict(l=10, r=20, t=30, b=10),
                    legend=dict(font=dict(size=10))
                )
                st.plotly_chart(fig_dist_rating, use_container_width=True)
            except Exception as e:
                st.warning(f"Tidak dapat membuat density plot: {e}.")
        else:
            st.info("Tidak cukup data rating yang beragam untuk membuat density plot.")
    else:
        st.info("Tidak cukup data untuk menampilkan distribusi rating.")
    st.markdown('</div>', unsafe_allow_html=True)

# 7.2 Semesta Sutradara (Bubble Chart) - dengan padding kiri
with vis_row2_col2:
    st.markdown('<div class="chart-container-right">', unsafe_allow_html=True)
    st.subheader("🎭 Semesta Sutradara")
    st.write("Ukuran titik sama | Warna = Jumlah Film")
    if 'Director' in df_filtered.columns and 'IMDb-Rating' in df_filtered.columns:
        directors_data = df_filtered.groupby('Director').agg(
            Title_Count=('Title', 'nunique'),
            Avg_IMDb_Rating=('IMDb-Rating', 'mean'),
            Unique_Genres=('Genre', 'nunique')
        ).reset_index()
        directors_data = directors_data[directors_data['Title_Count'] >= 3].nlargest(15, 'Title_Count')
        if not directors_data.empty:
            fig_bubble = px.scatter(
                directors_data,
                x='Avg_IMDb_Rating', y='Unique_Genres',
                hover_data={
                    'Director': True,
                    'Title_Count': True,
                    'Avg_IMDb_Rating': ':.2f',
                    'Unique_Genres': True
                },
                title='Analisis Sutradara',
                labels={'Avg_IMDb_Rating': 'Rata-Rata Rating', 'Unique_Genres': 'Jumlah Genre', 'Title_Count': 'Jumlah Film'},
                color='Title_Count', color_continuous_scale='YlOrRd',
                text='Director',
                height=300
            )
            fig_bubble.update_traces(
                marker=dict(size=12),
                textposition='top center',
                textfont=dict(size=8, color='#FFFFFF')
            )
            fig_bubble.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_bubble, use_container_width=True)
        else:
            st.info("Tidak cukup data sutradara (min. 3 film) untuk ditampilkan.")
    else:
        st.info("Kolom 'Director' atau 'IMDb-Rating' tidak ditemukan.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr style='margin-top:0.5rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)


# 8. Footer
st.markdown("""
<div style="text-align: center; color: #666; padding-bottom: 0.5rem;">
    <p>Sumber Data: Film IMDb | Dashboard dibuat dengan Streamlit</p>
</div>
""", unsafe_allow_html=True)