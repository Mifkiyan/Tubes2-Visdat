import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import time
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Dashboard Tren Genre Film IMDb",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Sidebar styling */
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
    
    /* Main header styling */
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

    /* KPI card styling */
    .kpi-card {
        background-color: #1a1a1a;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #333;
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #f5c518;
        margin-bottom: 0.2rem;
        line-height: 1.3;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .kpi-label {
        color: #aaa;
        font-size: 0.65rem;
        text-transform: uppercase;
    }
    
    /* Subheader styling */
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

    /* Container utama Streamlit */
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

    /* Styling untuk detail film terbaik di dalam expander */
    .film-detail-expander-card {
        padding: 10px; 
        border-left-width: 4px;
        border-left-style: solid;
        background-color: #282c34; 
        border-radius: 4px; 
        color: #e0e0e0; 
        font-size: 0.9rem;
    }
    .film-detail-expander-card strong {
        color: #f5c518; 
    }
    .film-detail-expander-card hr {
        border-top: 1px solid #444;
        margin-top: 6px;
        margin-bottom: 6px;
    }
    /* Styling untuk st.expander agar lebih compact */
    .stExpander {
        border: 1px solid #333 !important;
        border-radius: 5px !important;
        margin-bottom: 8px !important;
    }
    .stExpander header {
        padding: 0.4rem 0.6rem !important;
        background-color: #2a2a2a !important;
        color: #f0f0f0 !important;
        font-size: 0.95rem !important;
    }
    .stExpander header:hover {
        background-color: #383838 !important;
    }

</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Memuat dan menyiapkan dataset IMDb"""
    try:
        df = pd.read_csv('data_final.csv')
        
        df = df.rename(columns={
            'Name': 'Title',
            'Directors': 'Director',
            'Actors': 'Stars',
            'Rating': 'IMDb-Rating',
            'Genres': 'Category',
            'Year': 'ReleaseYear'
        })
        
        if 'Censor-board-rating' not in df.columns:
            df['Censor-board-rating'] = 'Not Rated' 
            
    except FileNotFoundError:
        try:
            df = pd.read_csv('IMDb_Data_final.csv')
        except FileNotFoundError:
            st.error("File 'data_final.csv' atau 'IMDb_Data_final.csv' tidak ditemukan.")
            return pd.DataFrame(), pd.DataFrame()

    df['ReleaseYear'] = pd.to_numeric(df['ReleaseYear'], errors='coerce')
    df.dropna(subset=['ReleaseYear'], inplace=True)
    
    if df['ReleaseYear'].empty:
        st.warning("Kolom 'ReleaseYear' tidak memiliki data numerik yang valid setelah dibersihkan.")
        return pd.DataFrame(), pd.DataFrame()

    df['ReleaseYear'] = df['ReleaseYear'].astype(int)
    df['Decade'] = (df['ReleaseYear'] // 10) * 10
    df['Decade_Label'] = df['Decade'].astype(str) + 's'

    def clean_duration(duration_str):
        if pd.isna(duration_str):
            return None
        if isinstance(duration_str, (int, float)):
            return duration_str
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
            for genre_item in genres:
                new_row = row.copy()
                new_row['Genre'] = genre_item.strip()
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

    if 'IMDb-Rating' in df_expanded.columns:
        df_expanded['IMDb-Rating'] = pd.to_numeric(df_expanded['IMDb-Rating'], errors='coerce')

    return df, df_expanded


df_original, df_expanded = load_data()

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
        st.header("Filter Dashboard")
        st.info("Filter akan diterapkan ke seluruh visualisasi dan statistik dalam dashboard ini.")

        if 'slider_year_range' not in st.session_state:
            st.session_state.slider_year_range = (min_year_data_available, max_year_data_available)
        if 'start_year_input' not in st.session_state:
            st.session_state.start_year_input = min_year_data_available
        if 'end_year_input' not in st.session_state:
            st.session_state.end_year_input = max_year_data_available
        
        def sync_slider_to_inputs():
            st.session_state.start_year_input = st.session_state.year_slider[0]
            st.session_state.end_year_input = st.session_state.year_slider[1]

        def sync_inputs_to_slider():
            start_val = st.session_state.start_year_num_input
            end_val = st.session_state.end_year_num_input
            if start_val <= end_val:
                valid_start = max(min_year_data_available, min(start_val, max_year_data_available))
                valid_end = min(max_year_data_available, max(end_val, min_year_data_available))
                if valid_start <= valid_end:
                    st.session_state.slider_year_range = (valid_start, valid_end)
                    st.session_state.start_year_input = valid_start 
                    st.session_state.end_year_input = valid_end   

        col_start_year, col_end_year = st.columns(2)
        with col_start_year:
            start_year_input_val = st.number_input(
                "Tahun Awal:", min_value=min_year_data_available, max_value=max_year_data_available,
                value=st.session_state.start_year_input, step=1, key="start_year_num_input",
                on_change=sync_inputs_to_slider,
                help=f"Tahun paling awal data: {min_year_data_available}"
            )
        with col_end_year:
            end_year_input_val = st.number_input(
                "Tahun Akhir:", min_value=min_year_data_available, max_value=max_year_data_available,
                value=st.session_state.end_year_input, step=1, key="end_year_num_input",
                on_change=sync_inputs_to_slider,
                help=f"Tahun paling akhir data: {max_year_data_available}"
            )

        if start_year_input_val > end_year_input_val:
            st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir.")
        else:
            st.session_state.start_year_input = start_year_input_val
            st.session_state.end_year_input = end_year_input_val
            st.session_state.slider_year_range = (start_year_input_val, end_year_input_val)

        selected_year_range_slider = st.slider(
            "Rentang Tahun Rilis:", 
            min_value=min_year_data_available, 
            max_value=max_year_data_available,
            value=st.session_state.slider_year_range, 
            key="year_slider",
            on_change=sync_slider_to_inputs 
        )
        
        if selected_year_range_slider != st.session_state.slider_year_range:
            st.session_state.slider_year_range = selected_year_range_slider
            st.session_state.start_year_input = selected_year_range_slider[0]
            st.session_state.end_year_input = selected_year_range_slider[1]
            st.rerun() 

        selected_year_range = st.session_state.slider_year_range

        st.markdown("##### Pilih Genre")
        if 'Genre' in df_expanded.columns:
            all_genres_list = sorted(list(df_expanded['Genre'].unique()))

            st.markdown("""
                        <style>
                        div[data-baseweb="select"] span{
                            color: #0e1117 !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)

            top_5_genres_overall = df_expanded['Genre'].value_counts().nlargest(5).index.tolist() \
                                    if not df_expanded.empty else []
            valid_top_5_genres = [g for g in top_5_genres_overall if g in all_genres_list]
            if not valid_top_5_genres and all_genres_list:
                valid_top_5_genres = all_genres_list[:min(5, len(all_genres_list))]

            selected_genres_filter = st.multiselect(
                "Genre yang ditampilkan:",
                options=all_genres_list,
                default=valid_top_5_genres,
                key="genre_multiselect"
            )
        else:
            selected_genres_filter = []
            st.warning("Kolom 'Genre' tidak ditemukan dalam data.")

    st.markdown(f"""
    <div class="main-header">
        <h1>🎬 Dashboard Tren Genre Film IMDb</h1>
    </div>
    """, unsafe_allow_html=True)
        # <p>Menganalisis Evolusi Sinema ({selected_year_range[0]}–{selected_year_range[1]})</p>

    df_filtered = df_expanded[
        (df_expanded['ReleaseYear'] >= selected_year_range[0]) &
        (df_expanded['ReleaseYear'] <= selected_year_range[1])
    ]
    if selected_genres_filter: 
        df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres_filter)]
    elif not selected_genres_filter and 'Genre' in df_expanded.columns: 
        st.sidebar.info("Anda belum memilih genre. Menampilkan data untuk semua genre yang tersedia dalam rentang tahun terpilih.")

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
        top_rated_film_title = "N/A"
        top_rated_film_rating = ""
        top_rated_film_year = ""
        if not df_filtered.empty and 'IMDb-Rating' in df_filtered.columns and 'Title' in df_filtered.columns:
            df_temp_rating = df_filtered.copy()
            df_temp_rating['IMDb-Rating'] = pd.to_numeric(df_temp_rating['IMDb-Rating'], errors='coerce')
            df_temp_rating.dropna(subset=['IMDb-Rating', 'Title'], inplace=True)

            if not df_temp_rating.empty:
                top_film_series = df_temp_rating.sort_values(
                    by=['IMDb-Rating', 'Title'], 
                    ascending=[False, True]
                ).drop_duplicates(subset=['Title'], keep='first')
                
                if not top_film_series.empty:
                    highest_rated_film = top_film_series.loc[top_film_series['IMDb-Rating'].idxmax()]
                    top_rated_film_title = highest_rated_film['Title']
                    top_rated_film_year = f"{highest_rated_film['ReleaseYear']}"
        
        display_value = top_rated_film_title
        if top_rated_film_year and top_rated_film_title != "N/A":
            display_value = f"{top_rated_film_title} ({top_rated_film_year})"
        
        font_size_style = "font-size:1.1rem;" if len(top_rated_film_title) < 25 else "font-size:0.9rem;"

        st.markdown(
            f'<div class="kpi-card">'
            f'  <div class="kpi-value" style="{font_size_style} white-space:normal; line-height:1.2;">{display_value}</div>' 
            f'  <div class="kpi-label">Film Rating Tertinggi</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr style='margin-top:0.5rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)

    if df_filtered.empty:
        st.info("Tidak ada data yang cocok dengan filter yang dipilih. Silakan sesuaikan filter Anda.")
        st.stop() 

    # st.subheader("📊 Analisis Produksi & Popularitas Genre Film")

    col1_container = st.container()
    with col1_container:
        vis_row1_col1, vis_row1_col2 = st.columns([1, 1]) 

    with vis_row1_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True) 
        st.write("##### 📈 Produksi Film Tahunan")
        st.write("Klik genre untuk melakukan filter · Klik 2x untuk filter genre")
        if 'ReleaseYear' in df_filtered.columns and 'Genre' in df_filtered.columns:
            movies_per_year_genre = df_filtered.groupby(['ReleaseYear', 'Genre']).size().reset_index(name='Jumlah Film')
            if not movies_per_year_genre.empty:
                fig_stacked_bar = px.bar(
                    movies_per_year_genre,
                    x='ReleaseYear', y='Jumlah Film', color='Genre', custom_data=['Genre'],
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
                fig_stacked_bar.update_traces(
                    hovertemplate=
                        'Genre = %{customdata[0]}<br>'
                        'Tahun Rilis = %{x}<br>'
                        'Jumlah Film Diproduksi = %{y:.0f}'
                        '<extra></extra>'
                )
                st.plotly_chart(fig_stacked_bar, use_container_width=True)
            else:
                st.info("Tidak ada data produksi film per tahun untuk filter yang dipilih.")
        else:
            st.info("Tidak cukup data (kolom 'ReleaseYear' atau 'Genre' hilang) untuk menampilkan grafik produksi film per tahun.")
        st.markdown('</div>', unsafe_allow_html=True)

    with vis_row1_col2:
        st.markdown('<div class="chart-container-right">', unsafe_allow_html=True) 
        st.write("##### 🎥 Total Produksi Film (Top 10)")
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
                    yaxis={'categoryorder':'total ascending'}, 
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False, 
                    margin=dict(l=20, r=10, t=30, b=10) 
                )
                fig_bar_genre_h.update_traces(
                    hovertemplate=
                        # 'Genre = %{y}<br>'
                        'Jumlah Film = %{x:.0f}'
                        '<extra></extra>'
                )
                st.plotly_chart(fig_bar_genre_h, use_container_width=True)
            else:
                st.info("Tidak ada data genre untuk ditampilkan dengan filter yang dipilih.")
        else:
            st.info("Kolom 'Genre' tidak ditemukan untuk membuat grafik top genre.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin-top:0.5rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)

    col2_container = st.container()
    with col2_container:
        vis_row2_col1, vis_row2_col2 = st.columns([1, 1]) 

    with vis_row2_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("⭐ Distribusi Rating IMDb")
        st.write("Klik genre untuk melakukan filter · Klik 2x untuk filter genre")
        if 'Genre' in df_filtered.columns and 'IMDb-Rating' in df_filtered.columns:
            df_filtered_rating = df_filtered.copy()
            df_filtered_rating['IMDb-Rating'] = pd.to_numeric(df_filtered_rating['IMDb-Rating'], errors='coerce')
            df_filtered_rating.dropna(subset=['IMDb-Rating'], inplace=True)

            hist_data_ratings = []
            group_labels_ratings = []
            plot_colors_ratings = []
            
            genres_in_filtered_data_rating = sorted(list(df_filtered_rating['Genre'].unique()))

            for genre_item_rating in genres_in_filtered_data_rating: # Ganti nama variabel
                genre_ratings = df_filtered_rating[df_filtered_rating['Genre'] == genre_item_rating]['IMDb-Rating']
                if len(genre_ratings) > 1: 
                    hist_data_ratings.append(genre_ratings.tolist())
                    group_labels_ratings.append(genre_item_rating)
                    plot_colors_ratings.append(genre_color_map.get(genre_item_rating, '#CCCCCC')) 

            if hist_data_ratings and group_labels_ratings:
                try:
                    fig_dist_rating = ff.create_distplot(
                        hist_data_ratings, group_labels_ratings, colors=plot_colors_ratings,
                        show_hist=False, show_rug=False, bin_size=0.2 
                    )
                    fig_dist_rating.update_layout(
                        xaxis_title='Rating IMDb', 
                        yaxis_title='Kepadatan',
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgba(0,0,0,0)',
                        legend_title_text='Genre',
                        height=300,
                        margin=dict(l=10, r=20, t=10, b=10), 
                        legend=dict(font=dict(size=10))
                    )
                    st.plotly_chart(fig_dist_rating, use_container_width=True)
                except Exception as e:
                    st.warning(f"Tidak dapat membuat density plot: {e}. Pastikan data rating cukup beragam.")
            else:
                st.info("Tidak cukup data rating yang beragam (perlu >1 film per genre) untuk membuat density plot.")
        else:
            st.info("Tidak cukup data (kolom 'Genre' atau 'IMDb-Rating' hilang/kosong) untuk menampilkan distribusi rating.")
        st.markdown('</div>', unsafe_allow_html=True)

    with vis_row2_col2:
        st.markdown('<div class="chart-container-right">', unsafe_allow_html=True)
        st.subheader("🏆 Film Terbaik per Genre")
        st.write("Klik pada nama genre untuk melihat detail film terbaiknya.")

        unique_genres_in_filtered_data = sorted(list(df_filtered['Genre'].unique()))

        if not unique_genres_in_filtered_data:
            st.info("Tidak ada genre spesifik dalam data yang difilter untuk menampilkan film terbaik.")
        else:
            # Case 1: <= 4 genres
            if len(unique_genres_in_filtered_data) <= 4:
                for current_genre in unique_genres_in_filtered_data:
                    with st.expander(f"{current_genre}"):
                        genre_films_df = df_filtered[df_filtered['Genre'] == current_genre].copy()
                        genre_films_df['IMDb-Rating'] = pd.to_numeric(genre_films_df['IMDb-Rating'], errors='coerce')
                        genre_films_df['ReleaseYear'] = pd.to_numeric(genre_films_df['ReleaseYear'], errors='coerce')
                        genre_films_df.dropna(subset=['IMDb-Rating', 'Title', 'ReleaseYear'], inplace=True)

                        top_film = genre_films_df.sort_values(
                            by=['IMDb-Rating', 'Title'], 
                            ascending=[False, True]
                        ).head(1)
                        if not top_film.empty:
                            film_row = top_film.iloc[0]
                            title = film_row.get('Title', 'N/A')
                            release_year = film_row.get('ReleaseYear', 'N/A')
                            rating_val = film_row.get('IMDb-Rating', 'N/A')
                            director = film_row.get('Director', 'N/A')
                            stars = film_row.get('Stars', 'N/A')

                            title_display = f"{title} ({int(release_year)})" if pd.notna(release_year) else title
                            rating_display = f"{rating_val:.1f}" if pd.notna(rating_val) else "N/A"
                            current_genre_color = genre_color_map.get(current_genre, '#FAFAFA')

                            st.markdown(f"""
                                <div style="padding: 5px 10px; margin: 5px 0; border-left: 5px solid {current_genre_color}; background-color: #262730;">
                                    <strong>Judul:</strong> {title_display}<br>
                                    <strong>Rating IMDb:</strong> {rating_display} ⭐<br>
                                    <strong>Sutradara:</strong> {director}<br>
                                    <strong>Pemain Utama:</strong> {stars}
                                </div>
                            """, unsafe_allow_html=True)

            # Case 2: > 4 genres
            else:
                scroll_html = """
                    <div style='
                        max-height: 320px;
                        overflow-y: auto;
                        padding: 10px;
                        border: 3px solid #333;
                        border-radius: 10px;
                        margin-top: 10px;
                        box-sizing: border-box;
                    '>
                """

                for idx, current_genre in enumerate(unique_genres_in_filtered_data):
                    scroll_html += f"<details><summary>{current_genre}</summary>"

                    genre_films_df = df_filtered[df_filtered['Genre'] == current_genre].copy()
                    genre_films_df['IMDb-Rating'] = pd.to_numeric(genre_films_df['IMDb-Rating'], errors='coerce')
                    genre_films_df['ReleaseYear'] = pd.to_numeric(genre_films_df['ReleaseYear'], errors='coerce')
                    genre_films_df.dropna(subset=['IMDb-Rating', 'Title', 'ReleaseYear'], inplace=True)

                    top_film = genre_films_df.sort_values(by='IMDb-Rating', ascending=False).head(1)
                    if not top_film.empty:
                        film_row = top_film.iloc[0]
                        title = film_row.get('Title', 'N/A')
                        release_year = film_row.get('ReleaseYear', 'N/A')
                        rating_val = film_row.get('IMDb-Rating', 'N/A')
                        director = film_row.get('Director', 'N/A')
                        stars = film_row.get('Stars', 'N/A')

                        title_display = f"{title} ({int(release_year)})" if pd.notna(release_year) else title
                        rating_display = f"{rating_val:.1f}" if pd.notna(rating_val) else "N/A"
                        current_genre_color = genre_color_map.get(current_genre, '#FAFAFA')

                        film_card_html = f"""
                            <div style="padding: 5px 10px; margin: 5px 0; border-left: 5px solid {current_genre_color}; background-color: #262730;">
                                <strong>Judul:</strong> {title_display}<br>
                                <strong>Rating IMDb:</strong> {rating_display} ⭐<br>
                                <strong>Sutradara:</strong> {director}<br>
                                <strong>Pemain Utama:</strong> {stars}
                            </div>
                        """
                        scroll_html += film_card_html

                    scroll_html += "</details>"
                    if idx < len(unique_genres_in_filtered_data) - 1:
                        scroll_html += "<hr>"

                scroll_html += "</div>"
                st.markdown(scroll_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin-top:0.5rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #666; padding-bottom: 0.5rem; font-size: 0.8rem;">
    <p>Sumber Data: https://www.imdb.com/ | Dashboard interaktif ini dibuat oleh Kelompok 11.</p>
    <p>IF4061 Visualisasi Data.</p>
</div>
""", unsafe_allow_html=True)
