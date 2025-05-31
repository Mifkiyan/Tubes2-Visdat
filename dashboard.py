import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* KPI card styling */
    .kpi-card {
        background-color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #333;
        height: 100%; /* Ensure cards have same height */
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #f5c518;
    }
    
    .kpi-label {
        color: #aaa;
        font-size: 0.9rem;
        text-transform: uppercase;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: #f5c518;
        color: #000;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
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

# Palet Warna Genre yang Konsisten
genre_color_map = {
    'Drama': '#FF6B6B', 'Action': '#4ECDC4', 'Comedy': '#45B7D1',
    'Crime': '#96CEB4', 'Thriller': '#FECA57', 'Romance': '#FF9FF3',
    'Adventure': '#54A0FF', 'Sci-Fi': '#48DBFB', 'Horror': '#FF6348',
    'Western': '#DDA15E', 'Animation': '#FFD166', 'Family': '#06D6A0',
    'Mystery': '#7E57C2', 'Fantasy': '#BA68C8', 'Biography': '#E57373',
    'Music': '#F79256', 'War': '#708D81', 'History': '#C0A793',
    'Sport': '#84A98C', 'Musical': '#A5678E', 'Film-Noir': '#525252',
    'Unknown': '#BDBDBD' 
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

    # --- Sidebar Filters ---
    with st.sidebar:
        st.header("🎯 Filter Dasbor")
        selected_year_range = st.slider(
            "Pilih Rentang Tahun Rilis",
            min_value=min_year_data_available,
            max_value=max_year_data_available,
            value=(min_year_data_available, max_year_data_available) 
        )

        # Filter Genre dengan Checkbox (menggunakan st.multiselect)
        st.markdown("##### Pilih Genre")
        if 'Genre' in df_expanded.columns:
            all_genres = sorted(list(df_expanded['Genre'].unique()))
            # Hitung top 5 genre dari keseluruhan data df_expanded (sebelum filter tahun)
            # agar defaultnya konsisten
            if not df_expanded.empty:
                top_5_genres_overall = df_expanded['Genre'].value_counts().nlargest(5).index.tolist()
            else:
                top_5_genres_overall = []
            
            # Pastikan top_5_genres_overall ada di all_genres (jika ada perubahan data)
            valid_top_5_genres = [genre for genre in top_5_genres_overall if genre in all_genres]
            if not valid_top_5_genres and all_genres: # Jika top 5 tidak valid tapi ada genre lain
                valid_top_5_genres = all_genres[:min(5, len(all_genres))]


            selected_genres = st.multiselect(
                "Genre yang ditampilkan:",
                options=all_genres,
                default=valid_top_5_genres,
                key="genre_multiselect"
            )
        else:
            selected_genres = [] # Jika kolom Genre tidak ada
            st.warning("Kolom 'Genre' tidak ditemukan dalam data.")

    # --- END Sidebar ---

    # --- Main Header (Sekarang menggunakan selected_year_range) ---
    st.markdown(f"""
    <div class="main-header">
        <h1 style="color: #000; margin: 0;">🎬 Dasbor Tren Genre Film IMDb</h1>
        <p style="color: #333; margin: 0;">Menganalisis Evolusi Sinema ({selected_year_range[0]}-{selected_year_range[1]})</p>
    </div>
    """, unsafe_allow_html=True)
    # --- END Main Header ---
    
    # --- Terapkan Filter ke Data ---
    df_filtered = df_expanded[
        (df_expanded['ReleaseYear'] >= selected_year_range[0]) &
        (df_expanded['ReleaseYear'] <= selected_year_range[1])
    ]
    if selected_genres: # Hanya filter berdasarkan genre jika ada genre yang dipilih
        df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
    elif not selected_genres and 'Genre' in df_expanded.columns: # Jika pengguna menghapus semua pilihan genre
        st.sidebar.info("Anda belum memilih genre. Menampilkan data untuk semua genre yang lolos filter tahun.")
        # df_filtered tetap seperti hasil filter tahun saja
    # --- END Terapkan Filter ---

    # --- KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_films = df_filtered['Title'].nunique() if not df_filtered.empty else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_films:,}</div><div class="kpi-label">Total Film</div></div>', unsafe_allow_html=True)
    with col2:
        unique_genres_count = df_filtered['Genre'].nunique() if not df_filtered.empty else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{unique_genres_count}</div><div class="kpi-label">Genre Ditampilkan</div></div>', unsafe_allow_html=True)
    with col3:
        avg_rating_val = df_filtered['IMDb-Rating'].mean() if not df_filtered.empty and 'IMDb-Rating' in df_filtered.columns else 0
        avg_rating_display = f"{avg_rating_val:.1f}" if pd.notna(avg_rating_val) and avg_rating_val != 0 else "N/A"
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_rating_display}</div><div class="kpi-label">Rata-Rata Rating</div></div>', unsafe_allow_html=True)
    with col4:
        actual_year_range_display = "N/A"
        if not df_filtered.empty and 'ReleaseYear' in df_filtered.columns and df_filtered['ReleaseYear'].nunique() > 0:
            min_actual_year = df_filtered['ReleaseYear'].min()
            max_actual_year = df_filtered['ReleaseYear'].max()
            if min_actual_year == max_actual_year:
                actual_year_range_display = f"{min_actual_year}"
            else:
                actual_year_range_display = f"{min_actual_year} - {max_actual_year}"
        
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{actual_year_range_display}</div><div class="kpi-label">Rentang Tahun (Filter)</div></div>', unsafe_allow_html=True) # Label KPI diubah
    # --- END KPIs ---

    st.markdown("<br>", unsafe_allow_html=True)

    # st.subheader("📦 Dataset yang Digunakan (Sampel Setelah Pemrosesan Awal & Ekspansi Genre)")
    # st.caption(f"Menampilkan sampel hingga 100 baris dari total {len(df_expanded):,} baris data yang telah diproses dan diexpand per genre. Data ini adalah basis untuk filter dan visualisasi di bawah.")
    # st.dataframe(df_expanded.head(100))
    # st.markdown("---")


    if df_filtered.empty:
        st.info("Tidak ada data yang cocok dengan filter yang dipilih. Silakan sesuaikan filter Anda.")
    else:
        st.subheader("📊 Analisis Produksi & Popularitas Genre Film")
        
        col_vis1_left, col_vis1_right = st.columns(2)

        with col_vis1_left:
            st.write("##### Jumlah Film Diproduksi per Tahun (Berdasarkan Genre)")
            if not df_filtered.empty and 'ReleaseYear' in df_filtered.columns and 'Genre' in df_filtered.columns:
                movies_per_year_genre = df_filtered.groupby(['ReleaseYear', 'Genre']).size().reset_index(name='Jumlah Film')
                
                if not movies_per_year_genre.empty:
                    fig_stacked_area = px.area(
                        movies_per_year_genre, 
                        x='ReleaseYear',
                        y='Jumlah Film',
                        color='Genre',
                        title='Produksi Film Tahunan berdasarkan Genre', 
                        labels={'ReleaseYear': 'Tahun Rilis', 'Jumlah Film': 'Jumlah Film Diproduksi'},
                        color_discrete_map=genre_color_map,
                        height=500 
                    )
                    fig_stacked_area.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        legend_title_text='Genre'
                    )
                    st.plotly_chart(fig_stacked_area, use_container_width=True)
                else:
                    st.info("Tidak ada data produksi film per tahun untuk filter yang dipilih.")
            else:
                st.info("Tidak cukup data untuk menampilkan grafik produksi film per tahun.")

        with col_vis1_right:
            st.write("##### Top 10 Genre Film (Berdasarkan Jumlah Instance)")
            if not df_filtered.empty and 'Genre' in df_filtered.columns:
                # Top 10 genre dihitung dari df_filtered agar mencerminkan data yang sedang ditampilkan
                top_10_genres_series = df_filtered['Genre'].value_counts().nlargest(10)
                if not top_10_genres_series.empty:
                    top_10_df = top_10_genres_series.reset_index()
                    top_10_df.columns = ['Genre', 'Jumlah Instance Genre']
                    
                    fig_bar_genre_h = px.bar(
                        top_10_df, 
                        x='Jumlah Instance Genre', 
                        y='Genre', 
                        orientation='h',
                        title="Top 10 Genre Film Terpopuler (dari data terfilter)",
                        labels={'Jumlah Instance Genre': 'Jumlah Film (Instance Genre)', 'Genre': 'Genre'},
                        color='Genre', 
                        color_discrete_map=genre_color_map,
                        height=500
                    )
                    fig_bar_genre_h.update_layout(
                        yaxis={'categoryorder':'total ascending'},
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False 
                    )
                    st.plotly_chart(fig_bar_genre_h, use_container_width=True)
                else:
                    st.info("Tidak ada data genre untuk ditampilkan dengan filter yang dipilih.")
            else:
                st.info("Kolom 'Genre' tidak ditemukan untuk membuat grafik top genre.")
        
        st.markdown("---") 

        st.subheader("🎭 Semesta Sutradara: Dampak & Pengaruh")
        st.write("Ukuran bubble = jumlah film | Posisi = rating & keragaman genre")

        if not df_filtered.empty and 'Director' in df_filtered.columns and 'IMDb-Rating' in df_filtered.columns:
            directors_data = df_filtered.groupby('Director').agg(
                Title_Count=('Title', 'nunique'),
                Avg_IMDb_Rating=('IMDb-Rating', 'mean'),
                Unique_Genres=('Genre', 'nunique')
            ).reset_index()
            
            directors_data = directors_data[directors_data['Title_Count'] >= 3].nlargest(15, 'Title_Count')

            if not directors_data.empty:
                fig_bubble = px.scatter(
                    directors_data, x='Avg_IMDb_Rating', y='Unique_Genres', size='Title_Count',
                    hover_data={'Director': True, 'Title_Count': True, 'Avg_IMDb_Rating': ':.2f', 'Unique_Genres': True},
                    title='Sutradara berdasarkan Rata-Rata Rating dan Keragaman Genre',
                    labels={'Avg_IMDb_Rating': 'Rata-Rata Rating IMDb', 'Unique_Genres': 'Jumlah Genre Berbeda', 'Title_Count': 'Jumlah Film Unik'},
                    color='Title_Count', color_continuous_scale='YlOrRd', size_max=50,
                    text='Director' 
                )
                fig_bubble.update_traces(
                    textposition='top center', 
                    textfont=dict(size=9, color='#FFFFFF') 
                )
                fig_bubble.update_layout(height=600, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bubble, use_container_width=True)
            else:
                st.info("Tidak cukup data sutradara (min. 3 film) untuk ditampilkan dengan filter yang dipilih.")
        else:
            st.info("Kolom 'Director' atau 'IMDb-Rating' tidak ditemukan atau tidak ada data sutradara untuk ditampilkan.")


        st.subheader("📈 Linimasa Dominasi Genre: Kisah Animasi")
        st.write("Lihat genre mana yang mendominasi setiap dekade. Klik Mainkan untuk memulai!")

        col_anim1, col_anim2, col_anim3, col_anim4 = st.columns([1, 1, 1, 2])
        with col_anim1: play_button = st.button("▶️ Mainkan", type="primary", key="play_anim") 
        with col_anim2: pause_button = st.button("⏸️ Jeda", key="pause_anim") 
        with col_anim3: reset_button = st.button("🔄 Atur Ulang", key="reset_anim") 
        with col_anim4: speed = st.slider("Kecepatan Animasi", 0.5, 2.0, 1.0, 0.1, key="speed_anim") 

        if not df_filtered.empty and 'Decade_Label' in df_filtered.columns and 'Genre' in df_filtered.columns:
            genre_decade_count_anim = df_filtered.groupby(['Decade_Label', 'Genre']).size().reset_index(name='Count')
            chart_placeholder = st.empty()
            decades_anim = sorted(genre_decade_count_anim['Decade_Label'].unique())

            if not decades_anim:
                chart_placeholder.info("Tidak ada data dekade untuk animasi dengan filter yang dipilih.")
            else:
                if 'current_decade_idx' not in st.session_state: st.session_state.current_decade_idx = 0
                if 'is_playing' not in st.session_state: st.session_state.is_playing = False

                if play_button: st.session_state.is_playing = True
                if pause_button: st.session_state.is_playing = False
                if reset_button:
                    st.session_state.current_decade_idx = 0
                    st.session_state.is_playing = False
                
                def draw_animated_chart(decade_idx):
                    if not (0 <= decade_idx < len(decades_anim)): 
                        chart_placeholder.info("Indeks dekade animasi tidak valid.")
                        return

                    current_decade_anim = decades_anim[decade_idx]
                    decade_data_anim = genre_decade_count_anim[genre_decade_count_anim['Decade_Label'] == current_decade_anim]
                    decade_data_anim = decade_data_anim.nlargest(10, 'Count')

                    if not decade_data_anim.empty:
                        fig_bar_anim = px.bar(
                            decade_data_anim, y='Genre', x='Count', orientation='h',
                            title=f'Jumlah Film berdasarkan Genre - {current_decade_anim}',
                            color='Genre', color_discrete_map=genre_color_map
                        )
                        fig_bar_anim.update_layout(height=500, showlegend=False, xaxis_title='Jumlah Film', yaxis_title='',
                                               plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                        chart_placeholder.plotly_chart(fig_bar_anim, use_container_width=True)
                    else:
                        chart_placeholder.info(f"Tidak ada data film untuk dekade {current_decade_anim} dengan filter yang dipilih.")

                if st.session_state.is_playing and st.session_state.current_decade_idx < len(decades_anim):
                    draw_animated_chart(st.session_state.current_decade_idx)
                    time.sleep(1.0 / speed)
                    st.session_state.current_decade_idx += 1
                    if st.session_state.current_decade_idx < len(decades_anim):
                        st.rerun()
                    else: 
                        st.session_state.is_playing = False 
                        st.rerun() 
                else:
                    display_idx = min(st.session_state.current_decade_idx, len(decades_anim) -1)
                    if display_idx >= 0 and decades_anim : 
                         draw_animated_chart(display_idx)
                    elif not decades_anim: 
                         chart_placeholder.info("Tidak ada data dekade untuk animasi dengan filter yang dipilih.")
                    
                    if st.session_state.current_decade_idx >= len(decades_anim) and len(decades_anim)>0 : 
                         st.session_state.is_playing = False 
        else:
            st.info("Tidak cukup data (Decade_Label, Genre) untuk animasi dengan filter yang dipilih.")


    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Sumber Data: Film IMDb | Dasbor dibuat dengan Streamlit & Plotly</p>
    </div>
    """, unsafe_allow_html=True)
