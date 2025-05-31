import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff 
import time

# Konfigurasi Halaman
st.set_page_config(
    page_title="Dasbor Tren Genre Film IMDb", 
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom untuk Styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #f5c518 0%, #e4b308 100%);
        padding: 1.5rem; /* Adjusted padding */
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem; /* Adjusted margin */
    }
    .main-header h1 {
        font-size: 2rem; /* Adjusted font size */
    }
    .main-header p {
        font-size: 1rem; /* Adjusted font size */
    }
    
    /* KPI card styling */
    .kpi-card {
        background-color: #1a1a1a;
        padding: 1rem; /* Adjusted padding */
        border-radius: 8px; /* Adjusted border-radius */
        text-align: center;
        border: 1px solid #333;
        height: 100%; 
    }
    
    .kpi-value {
        font-size: 2rem; /* Adjusted font size */
        font-weight: bold;
        color: #f5c518;
    }
    
    .kpi-label {
        color: #aaa;
        font-size: 0.8rem; /* Adjusted font size */
        text-transform: uppercase;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: #f5c518;
        color: #000;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.4rem 0.8rem; /* Adjusted padding */
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #e4b308;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Fungsi Muat dan Siapkan Data
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
        if pd.isna(duration_str): return None
        cleaned = str(duration_str).replace('min', '').strip()
        try: return int(cleaned)
        except ValueError: return None
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

# Palet Warna Genre yang Konsisten dan Mencolok, selaras dengan tema IMDb
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


if df_original.empty or df_expanded.empty or 'ReleaseYear' not in df_expanded.columns or df_expanded['ReleaseYear'].empty:
    st.warning("Gagal memuat atau memproses data, atau data tahun tidak tersedia. Tidak ada yang bisa ditampilkan.")
    st.markdown("""
    <div class="main-header">
        <h1 style="color: #000; margin: 0;">🎬 Dasbor Tren Genre Film IMDb</h1>
        <p style="color: #333; margin: 0;">Rentang tahun data tidak dapat ditentukan.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    min_year_data_available = int(df_expanded['ReleaseYear'].min())
    max_year_data_available = int(df_expanded['ReleaseYear'].max())

    with st.sidebar:
        st.header("🎯 Filter Dasbor")
        
        if 'slider_year_range' not in st.session_state:
            st.session_state.slider_year_range = (min_year_data_available, max_year_data_available)
        if 'start_year_input' not in st.session_state:
            st.session_state.start_year_input = min_year_data_available
        if 'end_year_input' not in st.session_state:
            st.session_state.end_year_input = max_year_data_available

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
        
        if start_year_input_val > end_year_input_val:
            st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir. Menggunakan nilai sebelumnya.")
            start_year_input_val = st.session_state.start_year_input
            end_year_input_val = st.session_state.end_year_input
        else:
            st.session_state.start_year_input = start_year_input_val
            st.session_state.end_year_input = end_year_input_val
            st.session_state.slider_year_range = (start_year_input_val, end_year_input_val)

        selected_year_range_slider = st.slider(
            "Pilih Rentang Tahun Rilis (Slider):", min_value=min_year_data_available, max_value=max_year_data_available,
            value=st.session_state.slider_year_range, key="year_slider"
        )

        if selected_year_range_slider != st.session_state.slider_year_range:
            st.session_state.slider_year_range = selected_year_range_slider
            st.session_state.start_year_input = selected_year_range_slider[0]
            st.session_state.end_year_input = selected_year_range_slider[1]
            st.rerun()
        
        selected_year_range = st.session_state.slider_year_range

        st.markdown("##### Pilih Genre")
        if 'Genre' in df_expanded.columns:
            all_genres = sorted(list(df_expanded['Genre'].unique()))
            for genre in all_genres:
                if genre not in genre_color_map: pass 

            top_5_genres_overall = df_expanded['Genre'].value_counts().nlargest(5).index.tolist() if not df_expanded.empty else []
            valid_top_5_genres = [genre for genre in top_5_genres_overall if genre in all_genres]
            if not valid_top_5_genres and all_genres: valid_top_5_genres = all_genres[:min(5, len(all_genres))]

            selected_genres = st.multiselect(
                "Genre yang ditampilkan:", options=all_genres, default=valid_top_5_genres, key="genre_multiselect"
            )
        else:
            selected_genres = [] 
            st.warning("Kolom 'Genre' tidak ditemukan dalam data.")

    st.markdown(f"""
    <div class="main-header">
        <h1>🎬 Dasbor Tren Genre Film IMDb</h1>
        <p>Menganalisis Evolusi Sinema ({selected_year_range[0]}-{selected_year_range[1]})</p>
    </div>
    """, unsafe_allow_html=True)
    
    df_filtered = df_expanded[
        (df_expanded['ReleaseYear'] >= selected_year_range[0]) &
        (df_expanded['ReleaseYear'] <= selected_year_range[1])
    ]
    if selected_genres: 
        df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
    elif not selected_genres and 'Genre' in df_expanded.columns: 
        st.sidebar.info("Anda belum memilih genre. Menampilkan data untuk semua genre yang lolos filter tahun.")

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4) 
    with kpi_col1:
        total_films = df_filtered['Title'].nunique() if not df_filtered.empty else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_films:,}</div><div class="kpi-label">Total Film</div></div>', unsafe_allow_html=True)
    with kpi_col2: 
        avg_rating_val = df_filtered['IMDb-Rating'].mean() if not df_filtered.empty and 'IMDb-Rating' in df_filtered.columns else 0
        avg_rating_display = f"{avg_rating_val:.1f}" if pd.notna(avg_rating_val) and avg_rating_val != 0 else "N/A"
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_rating_display}</div><div class="kpi-label">Rata-Rata Rating</div></div>', unsafe_allow_html=True)
    with kpi_col3:
        avg_duration_val = df_filtered['Duration_Clean'].mean() if not df_filtered.empty and 'Duration_Clean' in df_filtered.columns else 0
        avg_duration_display = f"{avg_duration_val:.0f} mnt" if pd.notna(avg_duration_val) and avg_duration_val != 0 else "N/A"
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_duration_display}</div><div class="kpi-label">Rata-Rata Durasi</div></div>', unsafe_allow_html=True)
    with kpi_col4: 
        top_director_name = "N/A"
        if not df_filtered.empty and 'Director' in df_filtered.columns:
            director_counts = df_filtered.groupby('Director')['Title'].nunique().sort_values(ascending=False)
            if not director_counts.empty: top_director_name = director_counts.index[0]
        st.markdown(f'<div class="kpi-card"><div class="kpi-value" style="font-size: 1.5rem; white-space: normal; overflow-wrap: break-word;">{top_director_name}</div><div class="kpi-label">Sutradara Terpopuler</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True) # Sedikit spasi

    if df_filtered.empty:
        st.info("Tidak ada data yang cocok dengan filter yang dipilih. Silakan sesuaikan filter Anda.")
    else:
        # --- Baris Visualisasi 1 ---
        st.subheader("📊 Analisis Produksi & Popularitas Genre Film")
        vis_row1_col1, vis_row1_col2 = st.columns(2)
        with vis_row1_col1:
            st.write("##### Produksi Film Tahunan") 
            if 'ReleaseYear' in df_filtered.columns and 'Genre' in df_filtered.columns:
                movies_per_year_genre = df_filtered.groupby(['ReleaseYear', 'Genre']).size().reset_index(name='Jumlah Film')
                if not movies_per_year_genre.empty:
                    fig_stacked_bar = px.bar( 
                        movies_per_year_genre, x='ReleaseYear', y='Jumlah Film', color='Genre',
                        labels={'ReleaseYear': 'Tahun Rilis', 'Jumlah Film': 'Jumlah Film Diproduksi'},
                        color_discrete_map=genre_color_map, height=450 # Adjusted height
                    )
                    fig_stacked_bar.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        legend_title_text='Genre', barmode='stack', margin=dict(l=20, r=20, t=50, b=20) # Adjusted margin
                    )
                    st.plotly_chart(fig_stacked_bar, use_container_width=True)
                else: st.info("Tidak ada data produksi film per tahun untuk filter yang dipilih.")
            else: st.info("Tidak cukup data untuk menampilkan grafik produksi film per tahun.")
        with vis_row1_col2:
            st.write("##### Genre Film Terpopuler")
            if 'Genre' in df_filtered.columns:
                top_10_genres_series = df_filtered['Genre'].value_counts().nlargest(10)
                if not top_10_genres_series.empty:
                    top_10_df = top_10_genres_series.reset_index(); top_10_df.columns = ['Genre', 'Jumlah Instance Genre']
                    fig_bar_genre_h = px.bar(
                        top_10_df, x='Jumlah Instance Genre', y='Genre', orientation='h',
                        labels={'Jumlah Instance Genre': 'Jumlah Film', 'Genre': 'Genre'},
                        color='Genre', color_discrete_map=genre_color_map, height=450 # Adjusted height
                    )
                    fig_bar_genre_h.update_layout(
                        yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(l=20, r=20, t=50, b=20) # Adjusted margin
                    )
                    st.plotly_chart(fig_bar_genre_h, use_container_width=True)
                else: st.info("Tidak ada data genre untuk ditampilkan dengan filter yang dipilih.")
            else: st.info("Kolom 'Genre' tidak ditemukan untuk membuat grafik top genre.")
        
        st.markdown("<hr style='margin-top:1rem; margin-bottom:1rem;'>", unsafe_allow_html=True) # Pemisah antar baris visualisasi

        # --- Baris Visualisasi 2 (Sebelumnya Grafik 3 dan 4) ---
        vis_row2_col1, vis_row2_col2 = st.columns(2)
        with vis_row2_col1:
            st.subheader("⭐ Distribusi Rating IMDb") # Judul disederhanakan
            st.write("Sebaran rating IMDb untuk genre yang dipilih.")
            if 'Genre' in df_filtered.columns and 'IMDb-Rating' in df_filtered.columns:
                hist_data_ratings, group_labels_ratings, plot_colors_ratings = [], [], []
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
                            title_text='Distribusi Kepadatan Rating IMDb', # Judul di dalam grafik
                            xaxis_title='Rating IMDb', yaxis_title='Kepadatan',
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            legend_title_text='Genre', height=450, margin=dict(l=20, r=20, t=50, b=20) # Adjusted height and margin
                        )
                        st.plotly_chart(fig_dist_rating, use_container_width=True)
                    except Exception as e: st.warning(f"Tidak dapat membuat density plot: {e}.")
                else: st.info("Tidak cukup data rating yang beragam untuk membuat density plot.")
            else: st.info("Tidak cukup data untuk menampilkan distribusi rating.")
        with vis_row2_col2:
            st.subheader("🎭 Semesta Sutradara") # Judul disederhanakan
            st.write("Ukuran titik sama | Warna = Jumlah Film Unik")
            if 'Director' in df_filtered.columns and 'IMDb-Rating' in df_filtered.columns:
                directors_data = df_filtered.groupby('Director').agg(
                    Title_Count=('Title', 'nunique'), Avg_IMDb_Rating=('IMDb-Rating', 'mean'),
                    Unique_Genres=('Genre', 'nunique')
                ).reset_index()
                directors_data = directors_data[directors_data['Title_Count'] >= 3].nlargest(15, 'Title_Count')
                if not directors_data.empty:
                    fig_bubble = px.scatter(
                        directors_data, x='Avg_IMDb_Rating', y='Unique_Genres', 
                        hover_data={'Director': True, 'Title_Count': True, 'Avg_IMDb_Rating': ':.2f', 'Unique_Genres': True},
                        title='Analisis Sutradara', # Judul di dalam grafik
                        labels={'Avg_IMDb_Rating': 'Rata-Rata Rating', 'Unique_Genres': 'Jml Genre', 'Title_Count': 'Jml Film'},
                        color='Title_Count', color_continuous_scale='YlOrRd', text='Director' 
                    )
                    fig_bubble.update_traces(
                        marker=dict(size=15), textposition='top center', 
                        textfont=dict(size=9, color='#FFFFFF') 
                    )
                    fig_bubble.update_layout(
                        height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', # Adjusted height
                        margin=dict(l=20, r=20, t=50, b=20) # Adjusted margin
                    )
                    st.plotly_chart(fig_bubble, use_container_width=True)
                else: st.info("Tidak cukup data sutradara (min. 3 film) untuk ditampilkan.")
            else: st.info("Kolom 'Director' atau 'IMDb-Rating' tidak ditemukan.")

    st.markdown("<hr style='margin-top:1rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #666; padding-bottom: 1rem;">
        <p>Sumber Data: Film IMDb | Dasbor dibuat dengan Streamlit & Plotly</p>
    </div>
    """, unsafe_allow_html=True)
