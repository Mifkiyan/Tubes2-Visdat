import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Page Configuration
st.set_page_config(
    page_title="IMDb Movie Trends Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
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
        height: 100%;
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

# Load and prepare data
@st.cache_data
def load_data():
    """Load and prepare the IMDb dataset"""
    # Read the CSV file
    df = pd.read_csv('IMDb_Data_final.csv')
    
    # Add decade column
    df['Decade'] = (df['ReleaseYear'] // 10) * 10
    df['Decade_Label'] = df['Decade'].astype(str) + 's'
    
    # Clean duration column with error handling
    def clean_duration(duration_str):
        """Clean duration string and convert to int, handling errors"""
        if pd.isna(duration_str):
            return None
        
        # Convert to string if not already
        duration_str = str(duration_str)
        
        # Remove 'min' and strip whitespace
        cleaned = duration_str.replace('min', '').strip()
        
        # Try to convert to int
        try:
            return int(cleaned)
        except ValueError:
            # If conversion fails, return None
            st.warning(f"Found invalid duration value: {duration_str}")
            return None
    
    df['Duration_Clean'] = df['Duration'].apply(clean_duration)
    
    # Process genres - create a row for each genre
    genres_expanded = []
    for idx, row in df.iterrows():
        if pd.notna(row['Category']):
            genres = row['Category'].split(',')
            for genre in genres:
                new_row = row.copy()
                new_row['Genre'] = genre.strip()
                genres_expanded.append(new_row)
    
    df_expanded = pd.DataFrame(genres_expanded)
    
    # Remove rows with invalid duration if needed
    df_expanded = df_expanded.dropna(subset=['Duration_Clean'])
    
    return df, df_expanded

# Header
st.markdown("""
<div class="main-header">
    <h1 style="color: #000; margin: 0;">🎬 IMDb Movie Genre Trends Dashboard</h1>
    <p style="color: #333; margin: 0;">Analyzing 100 Years of Cinema Evolution (1920-2022)</p>
</div>
""", unsafe_allow_html=True)

# Load data
df, df_expanded = load_data()

# Sidebar filters
with st.sidebar:
    st.header("🎯 Dashboard Filters")
    
    # Time period filter
    time_period = st.selectbox(
        "Select Time Period",
        ["All Time (1920-2022)", "Classic Era (1920-1969)", 
         "Modern Era (1970-1999)", "Contemporary (2000-2022)"],
        index=0
    )
    
    # Parse time period
    if time_period.startswith("All"):
        year_range = (1920, 2022)
    elif time_period.startswith("Classic"):
        year_range = (1920, 1969)
    elif time_period.startswith("Modern"):
        year_range = (1970, 1999)
    else:
        year_range = (2000, 2022)
    
    # Genre filter
    all_genres = sorted(df_expanded['Genre'].unique())
    selected_genres = st.multiselect(
        "Select Genres",
        all_genres,
        default=all_genres[:7]  # Default to top 7 genres
    )
    
    # Rating filter
    min_rating = st.slider(
        "Minimum IMDb Rating",
        min_value=7.6,
        max_value=9.0,
        value=7.6,
        step=0.1
    )
    
    # Apply filters
    df_filtered = df_expanded[
        (df_expanded['ReleaseYear'] >= year_range[0]) &
        (df_expanded['ReleaseYear'] <= year_range[1]) &
        (df_expanded['Genre'].isin(selected_genres)) &
        (df_expanded['IMDb-Rating'] >= min_rating)
    ]

# KPI Section
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_films = df_filtered['Title'].nunique()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_films:,}</div>
        <div class="kpi-label">Total Films</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    unique_genres = df_filtered['Genre'].nunique()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{unique_genres}</div>
        <div class="kpi-label">Unique Genres</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_rating = df_filtered['IMDb-Rating'].mean()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_rating:.1f}</div>
        <div class="kpi-label">Avg Rating</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    year_span = df_filtered['ReleaseYear'].max() - df_filtered['ReleaseYear'].min()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{year_span}</div>
        <div class="kpi-label">Years Covered</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Visualization 1: Genre Evolution Line Race
st.subheader("📊 Genre Popularity Evolution: The Great Race")
st.write("Track how different genres compete for dominance across decades.")

# Prepare data for line chart
genre_decade_rank = df_filtered.groupby(['Decade_Label', 'Genre']).agg({
    'Title': 'count',
    'IMDb-Rating': 'mean'
}).reset_index()

# Calculate rankings within each decade
genre_decade_rank['Rank'] = genre_decade_rank.groupby('Decade_Label')['Title'].rank(
    method='dense', ascending=False
)

# Create line chart for top genres
top_genres_overall = genre_decade_rank.groupby('Genre')['Title'].sum().nlargest(7).index

fig_evolution = px.line(
    genre_decade_rank[genre_decade_rank['Genre'].isin(top_genres_overall)],
    x='Decade_Label',
    y='Rank',
    color='Genre',
    markers=True,
    title='Genre Ranking Evolution Over Decades',
    color_discrete_map={
        'Drama': '#FF6B6B',
        'Action': '#4ECDC4',
        'Comedy': '#45B7D1',
        'Crime': '#96CEB4',
        'Thriller': '#FECA57',
        'Romance': '#FF9FF3',
        'Adventure': '#54A0FF'
    }
)

# Customize the chart
fig_evolution.update_layout(
    yaxis=dict(
        autorange='reversed',
        title='Ranking Position',
        ticktext=['#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9', '#10'],
        tickvals=list(range(1, 11))
    ),
    xaxis_title='Decade',
    height=600,
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

fig_evolution.update_traces(
    line=dict(width=3),
    marker=dict(size=10)
)

st.plotly_chart(fig_evolution, use_container_width=True)

# Visualization 2: Directors' Impact Bubble Chart
st.subheader("🎭 Directors' Universe: Impact & Influence")
st.write("Bubble size = number of films | Position = rating & genre diversity")

# Prepare directors data
directors_data = df_filtered.groupby('Director').agg({
    'Title': 'count',
    'IMDb-Rating': 'mean',
    'Genre': lambda x: len(x.unique())
}).reset_index()

# Filter directors with at least 3 films
directors_data = directors_data[directors_data['Title'] >= 3]
directors_data = directors_data.nlargest(15, 'Title')

# Create bubble chart
fig_bubble = px.scatter(
    directors_data,
    x='IMDb-Rating',
    y='Genre',
    size='Title',
    hover_data={
        'Director': True,
        'Title': True,
        'IMDb-Rating': ':.2f',
        'Genre': True
    },
    title='Directors by Average Rating and Genre Diversity',
    labels={
        'IMDb-Rating': 'Average IMDb Rating',
        'Genre': 'Number of Different Genres',
        'Title': 'Number of Films'
    },
    color='Title',
    color_continuous_scale='YlOrRd',
    size_max=50
)

# Add director names as text
fig_bubble.update_traces(
    text=directors_data['Director'].str.split().str[-1],  # Last name only
    textposition='middle center',
    textfont=dict(size=10, color='white')
)

fig_bubble.update_layout(
    height=600,
    xaxis=dict(range=[7.8, 8.5]),
    yaxis=dict(range=[0, 7]),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig_bubble, use_container_width=True)

# Visualization 3: Animated Bar Chart Race
st.subheader("📈 Genre Dominance Timeline: The Animated Story")
st.write("See which genres dominated each decade. Click Play to start!")

# Animation controls
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

with col1:
    play_button = st.button("▶️ Play", type="primary")
    
with col2:
    pause_button = st.button("⏸️ Pause")
    
with col3:
    reset_button = st.button("🔄 Reset")
    
with col4:
    speed = st.slider("Animation Speed", 0.5, 2.0, 1.0, 0.1)

# Prepare data for bar race
genre_decade_count = df_filtered.groupby(['Decade_Label', 'Genre']).size().reset_index(name='Count')

# Create placeholder for animated chart
chart_placeholder = st.empty()

# Get unique decades
decades = sorted(genre_decade_count['Decade_Label'].unique())

# Animation state
if 'current_decade_idx' not in st.session_state:
    st.session_state.current_decade_idx = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# Handle button clicks
if play_button:
    st.session_state.is_playing = True
    
if pause_button:
    st.session_state.is_playing = False
    
if reset_button:
    st.session_state.current_decade_idx = 0
    st.session_state.is_playing = False

# Animation loop
if st.session_state.is_playing and st.session_state.current_decade_idx < len(decades):
    # Get data for current decade
    current_decade = decades[st.session_state.current_decade_idx]
    decade_data = genre_decade_count[genre_decade_count['Decade_Label'] == current_decade]
    decade_data = decade_data.nlargest(10, 'Count')
    
    # Create horizontal bar chart
    fig_bar = px.bar(
        decade_data,
        y='Genre',
        x='Count',
        orientation='h',
        title=f'Film Count by Genre - {current_decade}',
        color='Genre',
        color_discrete_map={
            'Drama': '#FF6B6B',
            'Action': '#4ECDC4',
            'Comedy': '#45B7D1',
            'Crime': '#96CEB4',
            'Thriller': '#FECA57',
            'Romance': '#FF9FF3',
            'Adventure': '#54A0FF',
            'Sci-Fi': '#48DBFB',
            'Horror': '#FF6348',
            'Western': '#DDA15E'
        }
    )
    
    fig_bar.update_layout(
        height=500,
        showlegend=False,
        xaxis_title='Number of Films',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Display chart
    chart_placeholder.plotly_chart(fig_bar, use_container_width=True)
    
    # Update decade index
    time.sleep(1.0 / speed)
    st.session_state.current_decade_idx += 1
    
    # Auto-rerun to continue animation
    if st.session_state.current_decade_idx < len(decades):
        st.rerun()
else:
    # Show static chart for current decade
    current_decade = decades[min(st.session_state.current_decade_idx, len(decades)-1)]
    decade_data = genre_decade_count[genre_decade_count['Decade_Label'] == current_decade]
    decade_data = decade_data.nlargest(10, 'Count')
    
    fig_bar = px.bar(
        decade_data,
        y='Genre',
        x='Count',
        orientation='h',
        title=f'Film Count by Genre - {current_decade}',
        color='Genre',
        color_discrete_map={
            'Drama': '#FF6B6B',
            'Action': '#4ECDC4',
            'Comedy': '#45B7D1',
            'Crime': '#96CEB4',
            'Thriller': '#FECA57',
            'Romance': '#FF9FF3',
            'Adventure': '#54A0FF',
            'Sci-Fi': '#48DBFB',
            'Horror': '#FF6348',
            'Western': '#DDA15E'
        }
    )
    
    fig_bar.update_layout(
        height=500,
        showlegend=False,
        xaxis_title='Number of Films',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    chart_placeholder.plotly_chart(fig_bar, use_container_width=True)
    
    # Reset if reached the end
    if st.session_state.current_decade_idx >= len(decades):
        st.session_state.is_playing = False

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Data Source: IMDb Top 1000 Films (1920-2022) | Dashboard created with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)