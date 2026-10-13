
import streamlit as st
import pandas as pd
import requests

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="F1 Analytics Dashboard",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Analytics Dashboard")
st.caption("Formula 1 championship insights powered by historical data")

# ==========================================
# 2. FETCH DRIVER STANDINGS
# ==========================================
@st.cache_data(ttl=3600)
def get_standings(year):
    url = (
        f"https://api.jolpi.ca/ergast/f1/"
        f"{year}/driverStandings.json"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]

    if not standings:
        return pd.DataFrame()

    rows = []

    for driver in standings[0]["DriverStandings"]:
        rows.append({
            "Position": int(driver["position"]),
            "Driver": (
                driver["Driver"]["givenName"]
                + " "
                + driver["Driver"]["familyName"]
            ),
            "Team": driver["Constructors"][0]["name"],
            "Points": float(driver["points"]),
            "Wins": int(driver["wins"])
        })

    return pd.DataFrame(rows)


# ==========================================
# 3. SIDEBAR
# ==========================================
st.sidebar.header("⚙️ Dashboard Controls")

year = st.sidebar.selectbox(
    "Select season",
    [2025, 2024, 2023]
)

try:
    df = get_standings(year)

    if df.empty:
        st.warning("No standings data is available for this season.")

    else:
        # ==========================================
        # 4. CHAMPIONSHIP SUMMARY
        # ==========================================
        st.subheader(f"🏆 {year} Driver Championship")

        first, second, third = st.columns(3)

        leader = df.iloc[0]

        first.metric("Championship Leader", leader["Driver"])
        second.metric("Leader's Points", f'{leader["Points"]:g}')
        third.metric("Drivers Listed", len(df))

        st.divider()

        # ==========================================
        # 5. FULL STANDINGS TABLE
        # ==========================================
        st.subheader("🏁 Driver Standings")

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        # ==========================================
        # 6. DRIVER COMPARISON
        # ==========================================
        st.subheader("📊 Compare Drivers")

        selected_drivers = st.multiselect(
            "Choose drivers to compare",
            options=df["Driver"].tolist(),
            default=df["Driver"].head(3).tolist()
        )

        if selected_drivers:
            comparison = df[
                df["Driver"].isin(selected_drivers)
            ].sort_values("Points", ascending=False)

            chart_tab, table_tab = st.tabs(
                ["Points Chart", "Comparison Table"]
            )

            with chart_tab:
                st.bar_chart(
                    comparison,
                    x="Driver",
                    y="Points",
                    horizontal=True
                )

            with table_tab:
                st.dataframe(
                    comparison,
                    width="stretch",
                    hide_index=True
                )
        else:
            st.info("Select at least one driver to compare.")

        st.divider()

        # ==========================================
        # 7. TEAM PERFORMANCE
        # ==========================================
        st.subheader("🏎️ Team Performance")

        team_summary = (
            df.groupby("Team", as_index=False)
            .agg(
                Total_Points=("Points", "sum"),
                Total_Wins=("Wins", "sum"),
                Drivers=("Driver", "count")
            )
            .sort_values("Total_Points", ascending=False)
        )

        team_chart, team_table = st.tabs(
            ["Team Points Chart", "Team Summary"]
        )

        with team_chart:
            st.bar_chart(
                team_summary,
                x="Team",
                y="Total_Points",
                horizontal=True
            )

        with team_table:
            st.dataframe(
                team_summary,
                width="stretch",
                hide_index=True
            )

        st.divider()

        # ==========================================
        # 8. FILTER BY TEAM
        # ==========================================
        st.subheader("🔎 Explore a Team")

        teams = ["All Teams"] + sorted(
            df["Team"].unique().tolist()
        )

        selected_team = st.selectbox(
            "Filter drivers by team",
            teams
        )

        if selected_team == "All Teams":
            filtered_df = df.copy()
        else:
            filtered_df = df[
                df["Team"] == selected_team
            ]

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True
        )

        # ==========================================
        # 9. FOOTER
        # ==========================================
        st.caption(
            "Data source: Jolpica F1 API | "
            "Historical championship standings, "
            "not live race timing."
        )

except requests.RequestException as error:
    st.error(f"Could not retrieve F1 data: {error}")

except (KeyError, IndexError, ValueError) as error:
    st.error(f"Could not process the F1 data: {error}")
