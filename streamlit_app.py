import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------
# Page config + Custom CSS
# ----------------------------
st.set_page_config(page_title="Business Crawler Dashboard", layout="wide")
st.markdown("""
<style>
  /* App background & global text */
  .stApp {
    background-color: #1a1a1a;
    color: #FFFFFF !important;
    font-family: 'Segoe UI', sans-serif;
  }

  /* Force all links and inline text to white */
  a, a:visited, p, li, span {
    color: #FFFFFF !important;
  }

  /* KPI card panels */
  .kpi-card {
    background-color: #2a2a2a;
    border-radius: 8px;
    padding: 20px;
    margin: 5px;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.5);
  }
  .kpi-label {
    font-size: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #DDDDDD;
  }
  .kpi-value {
    font-size: 64px;
    font-weight: bold;
    color: #BB86FC;
  }

  /* Tabs: larger & bright */
  .stTabs [role="tablist"] [role="tab"] {
    font-size: 22px !important;
    font-weight: bold !important;
    color: #FFFFFF !important;
    padding: 0.5em 1em;
  }
  .stTabs [role="tablist"] [role="tab"][aria-selected="true"] {
    color: #BB86FC !important;
    border-bottom: 3px solid #BB86FC !important;
  }

  /* Section subtitles in purple */
  .stSubheader, h2, h3 {
    font-size: 24px !important;
    color: #BB86FC !important;
  }

  /* Footer */
  .footer {
    color: #888888;
    text-align: center;
    margin-top: 30px;
    font-size: 0.9em;
  }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------
st.markdown("<h1 style='text-align:center;'>Business Crawler Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Interactive insights from your web-scraping pipeline</p>", unsafe_allow_html=True)

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    main_path = 'output/_all_queries_merged.csv'
    stats_path = 'output/_domain_stats_summary.csv'
    df_main = pd.read_csv(main_path) if os.path.exists(main_path) else pd.DataFrame()
    df_stats = pd.read_csv(stats_path) if os.path.exists(stats_path) else pd.DataFrame()
    return df_main, df_stats

df, df_stats = load_data()

# ----------------------------
# Tabs Layout
# ----------------------------
tabs = st.tabs(["KPIs", "Visuals", "Raw Data"])

# ---- Tab 1: KPIs ----
with tabs[0]:
    st.subheader("Key Performance Indicators")
    if df.empty:
        st.warning("No data found. Please run the crawler first.")
    else:
        c1, c2, c3 = st.columns(3, gap="large")
        c1.markdown(f"""
          <div class="kpi-card">
            <div class="kpi-label">Total Articles</div>
            <div class="kpi-value">{len(df):,}</div>
          </div>
        """, unsafe_allow_html=True)
        c2.markdown(f"""
          <div class="kpi-card">
            <div class="kpi-label">Unique Domains</div>
            <div class="kpi-value">{df['domain'].nunique():,}</div>
          </div>
        """, unsafe_allow_html=True)
        avg_wc = int(df['content'].apply(lambda x: len(str(x).split())).mean()) if not df.empty else 0
        c3.markdown(f"""
          <div class="kpi-card">
            <div class="kpi-label">Avg. Word Count</div>
            <div class="kpi-value">{avg_wc:,}</div>
          </div>
        """, unsafe_allow_html=True)

# ---- Tab 2: Visuals ----
with tabs[1]:
    # 1) Doughnut
    st.subheader("Articles per Topic")
    if df.empty:
        st.warning("No data available.")
    else:
        topic_ct = df['topic'].value_counts().reset_index()
        topic_ct.columns = ['Topic', 'Count']
        fig1 = px.pie(
            topic_ct, names='Topic', values='Count', hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig1.update_traces(
            textinfo='percent+label',
            insidetextorientation='horizontal',
            textfont=dict(size=36, color='#FFFFFF')
        )
        fig1.update_layout(
            paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a',
            font=dict(size=16, color='#FFFFFF'),
            height=550, width=800,
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(font_size=14, font_color='#FFFFFF')
        )
        st.plotly_chart(fig1, use_container_width=True)

    # 2) Histogram
    st.subheader("Word Count Distribution")
    df['word_count'] = df['content'].apply(lambda x: len(str(x).split()))
    fig2 = px.histogram(df, x='word_count', nbins=40, opacity=0.8,
                        color_discrete_sequence=['#BB86FC'])
    fig2.update_layout(
        paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a',
        xaxis=dict(title_font=dict(size=18, color='#FFFFFF'),
                   tickfont=dict(size=14, color='#FFFFFF')),
        yaxis=dict(title_font=dict(size=18, color='#FFFFFF'),
                   tickfont=dict(size=14, color='#FFFFFF')),
        font=dict(size=16, color='#FFFFFF'),
        height=550, width=800,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3) Line Chart — Articles Over Time
    st.subheader("Articles Over Time")
    df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')
    timeline = (
        df['scraped_at']
          .dt.date
          .value_counts()
          .sort_index()
          .rename_axis('Date')
          .reset_index(name='Articles')
    )
    fig3 = px.line(
        timeline, x='Date', y='Articles', markers=True,
        color_discrete_sequence=['#03DAC6']
    )
    # Increase green marker size here:
    fig3.update_traces(marker=dict(size=14))
    fig3.update_layout(
        paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a',
        xaxis=dict(title_font=dict(size=18, color='#FFFFFF'),
                   tickfont=dict(size=14, color='#FFFFFF'),
                   tickformat='%b %d, %Y'),
        yaxis=dict(title_font=dict(size=18, color='#FFFFFF'),
                   tickfont=dict(size=14, color='#FFFFFF')),
        font=dict(size=16, color='#FFFFFF'),
        height=550, width=800,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

    # 4) Treemap
    st.subheader("Domain Contribution")
    domain_ct = df['domain'].value_counts().reset_index()
    domain_ct.columns = ['Domain', 'Count']
    fig4 = px.treemap(
        domain_ct, path=['Domain'], values='Count',
        color='Count', color_continuous_scale='Inferno'
    )
    fig4.update_layout(
        paper_bgcolor='#1a1a1a', plot_bgcolor='#1a1a1a',
        font=dict(size=16, color='#FFFFFF'),
        height=550, width=800,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig4, use_container_width=True)

    # 5) Sankey
    st.subheader("Domain → Topic Flow")
    flow = df[['domain', 'topic']].value_counts().reset_index()
    flow.columns = ['source', 'target', 'value']
    labels = pd.unique(flow[['source','target']].values.ravel()).tolist()
    src_idx = flow['source'].apply(lambda x: labels.index(x))
    tgt_idx = flow['target'].apply(lambda x: labels.index(x))
    fig5 = go.Figure(go.Sankey(
        node=dict(label=labels, pad=15, thickness=15,
                  color='#2C2C2C', line=dict(color='#444', width=0.5)),
        link=dict(source=src_idx, target=tgt_idx, value=flow['value'],
                  color='rgba(187,134,252,0.6)')
    ))
    fig5.update_layout(
        paper_bgcolor='#1a1a1a',
        font=dict(size=16, color='#FFFFFF'),
        height=550, width=900,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig5, use_container_width=True)

# ---- Tab 3: Raw Data ----
with tabs[2]:
    st.subheader("Raw Scraped Data")
    if df.empty:
        st.warning("No data to display.")
    else:
        st.dataframe(df, use_container_width=True, height=400)

# ----------------------------
# Footer
# ----------------------------
st.markdown("<div class='footer'>&copy; 2025 Gurpreet Badrain</div>", unsafe_allow_html=True)
