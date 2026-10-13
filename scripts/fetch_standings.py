
import requests

# Fetch historical Formula 1 driver standings
url = "https://api.jolpi.ca/ergast/f1/2025/driverStandings.json"

try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]

    if not standings:
        print("No standings data found.")
    else:
        drivers = standings[0]["DriverStandings"]

        print("\n🏎️ F1 DRIVER STANDINGS — 2025")
        print("-" * 50)

        for driver in drivers:
            name = (
                driver["Driver"]["givenName"]
                + " "
                + driver["Driver"]["familyName"]
            )
            points = driver["points"]
            position = driver["position"]
            team = driver["Constructors"][0]["name"]

            print(
                f"{position:>2}. {name:<25} "
                f"{points:>6} points | {team}"
            )

except requests.RequestException as error:
    print("Network error:", error)
except (KeyError, IndexError, ValueError) as error:
    print("Could not process the F1 data:", error)
