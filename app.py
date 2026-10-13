
import streamlit as st
import pandas as pd
import requests

# -------------------------------
# 1. Page Configuration
# -------------------------------
st.set_page_config(
    page_title="F1 Analytics Dashboard",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ Formula 1 Analytics Dashboard")
st.caption("Explore Formula 1 championship data")

# -------------------------------
# 2. Fetch F1 Data
# -------------------------------
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


# -------------------------------
# 3. Sidebar Settings
# -------------------------------
st.sidebar.header("⚙️ Dashboard Settings")

year = st.sidebar.selectbox(
    "Select F1 Season",
    [2025, 2024, 2023]
)

try:
    df = get_standings(year)

    if df.empty:
        st.warning("No standings data found for this season.")

    else:
        # -------------------------------
        # 4. Summary Metrics
        # -------------------------------
        st.subheader(f"🏆 {year} Driver Championship")

        col1, col2, col3 = st.columns(3)

        leader = df.iloc[0]

        col1.metric("Championship Leader", leader["Driver"])
        col2.metric("Leader's Points", f'{leader["Points"]:g}')
        col3.metric("Drivers Listed", len(df))

        st.divider()

        # -------------------------------
        # 5. Complete Standings Table
        # -------------------------------
        st.subheader("🏁 Driver Standings")

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        # -------------------------------
        # 6. Driver Comparison
        # -------------------------------
        st.subheader("📊 Driver Points Comparison")

        driver_names = df["Driver"].tolist()

        selected_drivers = st.multiselect(
            "Choose drivers to compare",
            options=driver_names,
            default=driver_names[:3]
        )

        if selected_drivers:
            comparison_df = df[
                df["Driver"].isin(selected_drivers)
            ].sort_values("Points", ascending=False)

            st.bar_chart(
                comparison_df,
                x="Driver",
                y="Points",
                horizontal=True
            )

            st.dataframe(
                comparison_df[
                    ["Position", "Driver", "Team", "Points", "Wins"]
                ],
                width="stretch",
                hide_index=True
            )
        else:
            st.info("Select at least one driver to display the comparison.")

        st.divider()

        # -------------------------------
        # 7. Team Filter
        # -------------------------------
        st.subheader("🔎 Explore Team Performance")

        teams = ["All Teams"] + sorted(
            df["Team"].unique().tolist()
        )

        selected_team = st.selectbox(
            "Select a team",
            teams
        )

        if selected_team == "All Teams":
            team_df = df.copy()
        else:
            team_df = df[df["Team"] == selected_team].copy()

        st.dataframe(
            team_df,
            width="stretch",
            hide_index=True
        )

        st.caption(
            "Source: Jolpica F1 API | "
            "Historical championship standings, not live race timing."
        )

except requests.RequestException as error:
    st.error(f"Unable to fetch F1 data: {error}")

except (KeyError, IndexError, ValueError) as error:
    st.error(f"Unable to process F1 data: {error}")
