import streamlit as st
import pandas as pd
import time

# Set up the Streamlit page (must be the first command)
st.set_page_config(layout="wide")  # Use the full width of the screen

# Hide Streamlit menu, footer, and prevent code inspection
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}  /* Hide GitHub button */
    </style>

    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.ctrlKey && (e.keyCode === 85 || e.keyCode === 83)) {
            return false;  // Disable "Ctrl + U" (View Source) & "Ctrl + S" (Save As)
        }
        if (e.keyCode == 123) {
            return false;  // Disable "F12" (DevTools)
        }
    };
    </script>
    """, unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    /* General Styling */
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stSidebar {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stHeader {
        color: #4CAF50;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stTable {
        width: 100%;
        border-collapse: collapse;
    }
    .stTable th, .stTable td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    .stTable th {
        background-color: #4CAF50;
        color: white;
    }
    .stTable tr:hover {
        background-color: #f1f1f1;
    }
    /* Slider CSS */
    .slider-container {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
        position: relative;
    }
    .slider-content {
        display: inline-block;
        padding-left: 50%; /* Start from the center */
        animation: slide 18000s linear infinite; /* Slower speed */
    }
    .slider-item {
        display: inline-block;
        margin-right: 50px; /* 0.5 inch gap between players */
        font-size: 18px;
        font-weight: bold;
    }
    @keyframes slide {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-100%); }
    }
    /* Popup CSS */
    .popup {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: fadeInOut 3s ease-in-out;
    }
    @keyframes fadeInOut {
        0% { opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { opacity: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "players" not in st.session_state:
    st.session_state["players"] = pd.DataFrame(columns=["ID", "Name", "Sold Amount", "Rating", "Team Bought", "Category", "Nationality"])

if "team_budgets" not in st.session_state:
    # Initialize team budgets (in lakhs)
    st.session_state["team_budgets"] = {
        "CSK": 9000,  # 90 CR
        "DC": 9000,
        "GT": 9000,
        "KKR": 9000,
        "LSG": 9000,
        "MI": 9000,
        "PBKS": 9000,
        "RR": 9000,
        "RCB": 9000,
        "SRH": 9000,
    }

if "team_squads" not in st.session_state:
    # Initialize team squads
    st.session_state["team_squads"] = {team: [] for team in st.session_state["team_budgets"].keys()}

# Function to generate a unique ID for each player
def generate_unique_id():
    if st.session_state["players"].empty:
        return 1
    else:
        return st.session_state["players"]["ID"].max() + 1

# Function to calculate total team rating
def calculate_team_rating(team):
    squad = st.session_state["team_squads"][team]
    return sum(player["Rating"] for player in squad)

def generate_slider_content():
    slider_items = []
    for team, squad in st.session_state["team_squads"].items():
        for player in squad:
            player_name = player["Name"]
            player_rating = player["Rating"]
            nationality = "✈️" if player["Nationality"] == "Foreign" else ""
            total_team_rating = calculate_team_rating(team)
            slider_items.append(f"{player_name} {nationality} ({player_rating}) | {team} ({total_team_rating})")
    
    # If there are no players, return a default message
    if not slider_items:
        return "No players have been bought yet."
    
    # Interleave the players' details to ensure alternative display
    interleaved_items = []
    for i in range(250):  # Total 250 positions
        interleaved_items.append(slider_items[i % len(slider_items)])
    
    return "   🏏   ".join(interleaved_items)

# Function to show a popup notification
def show_popup(message):
    popup = st.empty()
    popup.markdown(
        f"""
        <div class="popup">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(3)  # Display the popup for 3 seconds
    popup.empty()  # Remove the popup after 3 seconds

# Function to convert rank number to exponent (e.g., 2 → ²)
def rank_to_exponent(rank):
    exponents = {1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹", 10: "¹⁰"}
    return exponents.get(rank, str(rank))

# Streamlit app title and description
st.title("Mock IPL Auction Dashboard")
st.write("Manage and track player details during the auction, including team budgets and squads.")

# Section 0: Slider for Sold Players
slider_content = generate_slider_content()
st.markdown(
    f"""
    <div class="slider-container">
        <div class="slider-content">
            <div class="slider-item">{slider_content}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Section 1: Team Budgets (Top Section)
st.header("Team Budgets")

# Calculate team rankings
team_rankings = []
for team, squad in st.session_state["team_squads"].items():
    total_points = calculate_team_rating(team)
    team_rankings.append({"Team": team, "Total Points": total_points})

# Sort teams alphabetically if total points are 0, otherwise by total points in descending order
if all(team["Total Points"] == 0 for team in team_rankings):
    team_rankings = sorted(team_rankings, key=lambda x: x["Team"])
else:
    team_rankings = sorted(team_rankings, key=lambda x: x["Total Points"], reverse=True)

# Assign ranks
for i, team in enumerate(team_rankings):
    team["Rank"] = i + 1

# Display team budgets with rankings
budget_cols = st.columns(5)  # Display teams in 5 columns
for i, team in enumerate(team_rankings):
    team_name = team["Team"]
    rank = team["Rank"]
    budget = st.session_state["team_budgets"][team_name]
    
    # Display team name with ranking as exponent (e.g., CSK²)
    team_label = f"{team_name}{rank_to_exponent(rank)}"
    
    # Display metric
    budget_cols[i % 5].metric(label=team_label, value=f"{budget / 100} Cr")

# Section 2: Player Entry and Modification (Left Sidebar)
with st.sidebar:
    st.header("Player Entry and Modification")
    with st.form("player_form"):
        name = st.text_input("Player Name")
        sold_amount = st.number_input("Sold Amount (in lakhs)", min_value=0, step=1)
        
        # Dropdown showing teams and their current remaining budget
        team_bought = st.selectbox(
            "Team Bought",
            options=[f"{team} (Budget: {budget} lakhs)" for team, budget in st.session_state["team_budgets"].items()],
        )
        
        # Extract team name from the dropdown option
        team_bought = team_bought.split(" (")[0]
        
        rating = st.number_input("Player Rating (0-100)", min_value=0, max_value=100, step=1)

        # Add dropdown for Category (Batter, Bowler, All-rounder, Wicketkeeper)
        category = st.selectbox("Player Category", options=["Batter", "Bowler", "Allrounder", "Wicketkeeper"])

        # Add dropdown for Nationality (Indian or Foreign)
        nationality = st.selectbox("Nationality", options=["Indian", "Foreign"])

        submitted_add = st.form_submit_button("Add Player")
        submitted_modify = st.form_submit_button("Modify Player")
        submitted_delete = st.form_submit_button("Delete Player")

        if submitted_add:
            # Validate input
            if not name.strip():
                st.error("Player Name cannot be empty.")
            elif st.session_state["team_budgets"][team_bought] < sold_amount:
                st.error(f"Insufficient budget for {team_bought}! Available budget: {st.session_state['team_budgets'][team_bought]} lakhs.")
            else:
                # Add new player
                new_entry = {
                    "ID": generate_unique_id(),
                    "Name": name.strip(),
                    "Sold Amount": sold_amount,
                    "Rating": rating,
                    "Team Bought": team_bought,
                    "Category": category,
                    "Nationality": nationality,
                }
                st.session_state["players"] = pd.concat(
                    [st.session_state["players"], pd.DataFrame([new_entry])],
                    ignore_index=True,
                )

                # Add player to the team's squad
                st.session_state["team_squads"][team_bought].append({
                    "ID": new_entry["ID"],
                    "Name": name.strip(),
                    "Sold Amount": sold_amount,
                    "Rating": rating,
                    "Category": category,
                    "Nationality": nationality,
                })

                # Deduct sold amount from the team's budget
                st.session_state["team_budgets"][team_bought] -= sold_amount

                # Show popup notification
                popup_message = f"Congratulations {name.strip()} ({rating}) | {team_bought} ({calculate_team_rating(team_bought)})"
                show_popup(popup_message)

                st.success(f"Player '{name}' added to {team_bought} successfully!")

                # Force re-render to ensure the UI updates immediately
                st.rerun()

        if submitted_modify:
            # Validate input
            if not name.strip():
                st.error("Player Name cannot be empty.")
            elif st.session_state["team_budgets"][team_bought] < sold_amount:
                st.error(f"Insufficient budget for {team_bought}! Available budget: {st.session_state['team_budgets'][team_bought]} lakhs.")
            else:
                # Check if the player already exists
                if name.strip() in st.session_state["players"]["Name"].values:
                    # Modify existing player
                    player_id = st.session_state["players"].loc[st.session_state["players"]["Name"] == name.strip(), "ID"].values[0]
                    original_team = st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Team Bought"].values[0]
                    old_sold_amount = st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Sold Amount"].values[0]

                    # If the team is changed, adjust budgets and squads
                    if original_team != team_bought:
                        # Add the old sold amount back to the original team's budget
                        st.session_state["team_budgets"][original_team] += old_sold_amount
                        
                        # Remove the player from the original team's squad
                        st.session_state["team_squads"][original_team] = [player for player in st.session_state["team_squads"][original_team] if player["ID"] != player_id]

                        # Deduct the new sold amount from the new team's budget
                        st.session_state["team_budgets"][team_bought] -= sold_amount

                        # Add the player to the new team's squad
                        st.session_state["team_squads"][team_bought].append({
                            "ID": player_id,
                            "Name": name.strip(),
                            "Sold Amount": sold_amount,
                            "Rating": rating,
                            "Category": category,
                            "Nationality": nationality,
                        })
                    else:
                        # If the team is not changed, adjust the budget by the difference between the new and old sold amount
                        price_difference = sold_amount - old_sold_amount
                        st.session_state["team_budgets"][team_bought] -= price_difference

                        # Update the player's price in the team's squad
                        for player in st.session_state["team_squads"][team_bought]:
                            if player["ID"] == player_id:
                                player["Sold Amount"] = sold_amount
                                player["Rating"] = rating
                                player["Category"] = category
                                player["Nationality"] = nationality

                    # Update the player's details in the global player list
                    st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Name"] = name.strip()
                    st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Sold Amount"] = sold_amount
                    st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Rating"] = rating
                    st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Team Bought"] = team_bought
                    st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Category"] = category
                    st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Nationality"] = nationality

                    st.success(f"Player '{name}' modified successfully!")
                else:
                    st.error(f"Player '{name}' does not exist. Please add the player first.")

                # Force re-render to ensure the UI updates immediately
                st.rerun()

        if submitted_delete:
            # Validate input
            if not name.strip():
                st.error("Player Name cannot be empty.")
            else:
                # Check if the player exists
                if name.strip() in st.session_state["players"]["Name"].values:
                    # Delete existing player
                    player_id = st.session_state["players"].loc[st.session_state["players"]["Name"] == name.strip(), "ID"].values[0]
                    original_team = st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Team Bought"].values[0]
                    old_sold_amount = st.session_state["players"].loc[st.session_state["players"]["ID"] == player_id, "Sold Amount"].values[0]

                    # Add the old sold amount back to the original team's budget
                    st.session_state["team_budgets"][original_team] += old_sold_amount

                    # Remove the player from the original team's squad
                    st.session_state["team_squads"][original_team] = [player for player in st.session_state["team_squads"][original_team] if player["ID"] != player_id]

                    # Remove the player from the global player list
                    st.session_state["players"] = st.session_state["players"][st.session_state["players"]["Name"] != name.strip()]

                    st.success(f"Player '{name}' deleted successfully!")
                else:
                    st.error(f"Player '{name}' does not exist.")

                # Force re-render to ensure the UI updates immediately
                st.rerun()

# Section 3: Players Sold List (Left Section)
st.header("Players Sold")
if not st.session_state["players"].empty:
    # Sort players by ID in descending order (latest at the top)
    sorted_players = st.session_state["players"].sort_values(by="ID", ascending=False)
    st.dataframe(sorted_players, use_container_width=True)
else:
    st.write("No players sold yet.")

# Section 4: Team Squad (Right Section)
st.header("Team Squad")
selected_team = st.selectbox("Select Team to View Squad", list(st.session_state["team_squads"].keys()))

if st.session_state["team_squads"][selected_team]:
    squad_df = pd.DataFrame(st.session_state["team_squads"][selected_team])

    # Calculate totals
    total_sold = squad_df["Sold Amount"].sum()
    total_rating = squad_df["Rating"].sum()
    total_remaining_budget = st.session_state["team_budgets"][selected_team]

    # Convert totals to Crores (Cr)
    total_sold_cr = total_sold / 100
    total_remaining_budget_cr = total_remaining_budget / 100

    # Count categories and nationalities
    num_batters = squad_df[squad_df["Category"] == "Batter"].shape[0]
    num_bowlers = squad_df[squad_df["Category"] == "Bowler"].shape[0]
    num_allrounders = squad_df[squad_df["Category"] == "Allrounder"].shape[0]
    num_wicketkeepers = squad_df[squad_df["Category"] == "Wicketkeeper"].shape[0]
    num_indian = squad_df[squad_df["Nationality"] == "Indian"].shape[0]
    num_foreign = squad_df[squad_df["Nationality"] == "Foreign"].shape[0]
    num_players = squad_df.shape[0]

    # Display squad details
    st.table(squad_df)
    st.write(f"**Total Sold Amount for {selected_team}: {total_sold_cr} Cr**")
    st.write(f"**Total Rating for {selected_team}: {total_rating}**")
    st.write(f"**Remaining Budget for {selected_team}: {total_remaining_budget_cr} Cr**")
    st.write(f"**No. of Batters: {num_batters}**")
    st.write(f"**No. of Bowlers: {num_bowlers}**")
    st.write(f"**No. of Allrounders: {num_allrounders}**")
    st.write(f"**No. of Wicketkeepers: {num_wicketkeepers}**")
    st.write(f"**No. of Indian Players: {num_indian}**")
    st.write(f"**No. of Foreign Players: {num_foreign}**")
    st.write(f"**Total No. of Players Bought: {num_players}**")
else:
    st.write(f"No players bought by {selected_team} yet.")

# Section 5: Team Rankings (Right Section)
st.header("Team Rankings")
team_rankings = []

# Calculate total points (ratings) for each team
for team, squad in st.session_state["team_squads"].items():
    total_points = calculate_team_rating(team)
    team_rankings.append({"Team": team, "Total Points": total_points})

# Sort teams by total points in descending order
team_rankings = sorted(team_rankings, key=lambda x: x["Total Points"], reverse=True)

# Display rankings
if team_rankings:
    st.write("Teams ranked by total points (ratings):")
    for i, team in enumerate(team_rankings):
        st.write(f"{i + 1}. {team['Team']}: {team['Total Points']} points")
else:
    st.write("No teams have bought players yet.")
