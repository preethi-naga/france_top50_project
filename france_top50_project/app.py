import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="France Top 50 Analytics Dashboard",
    layout="wide"
)

# ---------------- CUSTOM UI ----------------
st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(135deg, #bfdbfe 0%, #ddd6fe 40%, #fbcfe8 100%);
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #ffffff 0%, #f3e8ff 100%);
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #c4b5fd 0%, #f9a8d4 100%);
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: black !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🎵 France Top 50 Playlist Analysis Dashboard")
st.subheader("Audience Sensitivity, Content Compliance & Format Preference")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.sidebar.file_uploader("Upload CSV Dataset", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # ---------------- PREPROCESSING ----------------
    df["date"] = pd.to_datetime(df["date"])
    df["duration_min"] = df["duration_ms"] / 60000
    df["album_type"] = df["album_type"].str.lower().str.strip()

    # ---------------- FILTERS ----------------
    st.sidebar.header("Filters")

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df["date"].min(), df["date"].max()]
    )

    rank_tier = st.sidebar.selectbox(
        "Rank Tier",
        ["Top 10", "Top 25", "Top 50"]
    )

    explicit_toggle = st.sidebar.selectbox(
        "Explicit Content",
        ["All", "Explicit Only", "Clean Only"]
    )

    album_filter = st.sidebar.multiselect(
        "Album Type",
        options=df["album_type"].unique(),
        default=list(df["album_type"].unique())
    )

    # ---------------- APPLY FILTERS ----------------
    filtered_df = df[
        (df["date"] >= pd.to_datetime(date_range[0])) &
        (df["date"] <= pd.to_datetime(date_range[1])) &
        (df["album_type"].isin(album_filter))
    ]

    if rank_tier == "Top 10":
        filtered_df = filtered_df[filtered_df["position"] <= 10]
    elif rank_tier == "Top 25":
        filtered_df = filtered_df[filtered_df["position"] <= 25]
    else:
        filtered_df = filtered_df[filtered_df["position"] <= 50]

    if explicit_toggle == "Explicit Only":
        filtered_df = filtered_df[filtered_df["is_explicit"] == True]
    elif explicit_toggle == "Clean Only":
        filtered_df = filtered_df[filtered_df["is_explicit"] == False]

    total = len(filtered_df)

    # ---------------- KPI CALCULATIONS ----------------
    explicit_share = round(filtered_df["is_explicit"].mean() * 100, 2) if total else 0
    clean_ratio = round((filtered_df["is_explicit"] == False).mean() * 100, 2) if total else 0
    single_ratio = round((filtered_df["album_type"] == "single").mean() * 100, 2) if total else 0
    avg_duration = round(filtered_df["duration_min"].mean(), 2) if total else 0

    if total > 1:
        album_corr = filtered_df[["total_tracks", "popularity"]].corr().iloc[0, 1]
        album_impact_index = round(album_corr, 2)
    else:
        album_impact_index = 0

    content_acceptance_score = round(
        ((100 - filtered_df["position"]).mean() + filtered_df["popularity"].mean()) / 2,
        2
    ) if total else 0

    # ---------------- KPI DISPLAY ----------------
    st.subheader("📊 Key Performance Indicators")

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    c1.metric("Explicit Content Share", f"{explicit_share}%")
    c2.metric("Clean Content Dominance Ratio", f"{clean_ratio}%")
    c3.metric("Single vs Album Ratio", f"{single_ratio}%")
    c4.metric("Average Song Duration", f"{avg_duration} min")
    c5.metric("Album Size Impact Index", album_impact_index)
    c6.metric("Content Acceptance Score", content_acceptance_score)

    st.markdown("---")

    # ---------------- TREND OVER TIME ----------------
    st.subheader("📈 Popularity Trend Over Time")

    trend_df = filtered_df.groupby("date")["popularity"].mean().reset_index()

    fig_trend = px.line(
        trend_df,
        x="date",
        y="popularity",
        title="Average Popularity Trend",
        markers=True
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    # ---------------- KEY INSIGHTS PANEL ----------------
    st.subheader("💡 Key Insights")

    insight_text = f"""
• Explicit content share is {explicit_share}%  
• Clean content dominance ratio is {clean_ratio}%  
• Singles account for {single_ratio}% of tracks  
• Average song duration is {avg_duration} minutes  
• Content acceptance score is {content_acceptance_score}
"""

    st.success(insight_text)

    # ---------------- BUSINESS RECOMMENDATIONS ----------------
    st.subheader("📌 Business Recommendations")

    recommendation = ""

    if explicit_share < 40:
        recommendation += "• Focus on clean content for better French audience acceptance.\n\n"
    else:
        recommendation += "• Explicit content is well accepted in this market.\n\n"

    if single_ratio > 60:
        recommendation += "• Prioritize single releases for playlist pitching.\n\n"
    else:
        recommendation += "• Album tracks also show strong performance.\n\n"

    if 2.5 <= avg_duration <= 3.5:
        recommendation += "• Maintain medium-duration songs (2.5–3.5 min).\n\n"
    else:
        recommendation += "• Optimize duration closer to 3 minutes.\n\n"

    st.warning(recommendation)

    # ---------------- CHARTS ----------------
    col1, col2 = st.columns(2)

    with col1:
        explicit_counts = filtered_df["is_explicit"].map(
            {True: "Explicit", False: "Clean"}
        ).value_counts()

        fig1 = px.pie(
            values=explicit_counts.values,
            names=explicit_counts.index,
            title="Explicit vs Clean Content",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        album_counts = filtered_df["album_type"].value_counts()

        album_df = album_counts.reset_index()
        album_df.columns = ["album_type", "count"]

        fig2 = px.bar(
            album_df,
            x="album_type",
            y="count",
            color="album_type",
            title="Album Format Distribution",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Song Duration Histogram
    fig3 = px.histogram(
        filtered_df,
        x="duration_min",
        nbins=20,
        title="Song Duration Distribution",
        color_discrete_sequence=["#8b5cf6"]
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Rank Tier Comparison
    tier_df = df.copy()
    tier_df["rank_tier"] = np.where(
        tier_df["position"] <= 10,
        "Top 10",
        np.where(tier_df["position"] <= 25, "Top 25", "Top 50")
    )

    tier_summary = tier_df.groupby("rank_tier").agg({
        "popularity": "mean",
        "duration_min": "mean",
        "is_explicit": "mean"
    }).reset_index()

    fig4 = px.bar(
        tier_summary,
        x="rank_tier",
        y="popularity",
        color="rank_tier",
        title="Rank Tier Comparison",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig4, use_container_width=True)

    # ---------------- SUMMARY ----------------
    st.subheader("📄 Dataset Preview")
    st.dataframe(filtered_df)

else:
    st.info("Please upload the CSV file to start the analysis.")