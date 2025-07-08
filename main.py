import streamlit as st
import pandas as pd
import base64
# import matplotlib.pyplot as plt # Removed matplotlib import
import altair as alt
from auth import init_firebase, register_coach, login_coach
from players import fetch_players, save_player, fetch_matches, save_match, delete_player, delete_match

def set_bg_local(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        body, .stApp {{
            background-image: url('data:image/png;base64,{encoded}');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center center;
            min-height: 100vh;
            width: 100vw;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Initialize Firebase
st.set_page_config(page_title="CricScore+", layout="wide")
st.markdown("""
    <style>
        .css-1jc7ptx, .e1ewe7hr3, .e1ewe7hr1 {
            visibility: hidden;
        }
        .stApp {
            margin-top: -75px;
        }
        /* CSS to hide the white header bar */
        .st-emotion-cache-1eyfjps {
            display: none;
        }
        /* CSS to make the button smaller */
        .stButton>button {
            padding-top: 0.1rem;
            padding-bottom: 0.1rem;
            font-size: 0.8rem;
        }
         /* CSS for button hover effect */
        .stButton>button:hover {
            background-color: black !important;
            color: white !important; /* Ensure text is visible on black background */
        }
         /* CSS to reduce space below expander titles */
        .streamlit-expander > div[role="button"] p {
            margin-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    h1, h2, h3, h4 {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .stats-box strong {
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

db = init_firebase()

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'username': None,
        'team': None
    })

# Credentials page
def show_credentials():
    set_bg_local("login_bg.png")
    st.title("CricScore+")
    mode = st.radio("", ["Login", "Register"], horizontal=True)
    if mode == "Register":
        st.subheader("Register as Coach")
        user = st.text_input("Your Name", key="reg_user")
        team = st.text_input("Your Team Name", key="reg_team")
        pwd = st.text_input("Password", type="password", key="reg_pass")
        cpwd = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register"):
            if not user or not team or not pwd:
                st.error("All fields are required.")
            elif pwd != cpwd:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_coach(db, user, team, pwd)
                st.success(msg + " Please login.") if ok else st.error(msg)
    else:
        st.subheader("Coach Login")
        user = st.text_input("Your Name", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            ok, team = login_coach(db, user, pwd)
            if ok:
                st.session_state.update({'logged_in': True, 'username': user, 'team': team})
                st.rerun()
            else:
                st.error("Invalid credentials.")
    st.stop()

# Main application pages
def show_app():
    st.sidebar.title(f"Welcome, Coach - {st.session_state['team']}")
    page = st.sidebar.radio("Navigate", ["Edit Player Details", "Team Results", "Player Analytics"])
    username = st.session_state['username']

    # 1. Edit Player Details
    if page == "Edit Player Details":
        st.header("Manage Your Team")
        df = fetch_players(db, username)

        # Add/Register Player
st.subheader("Add / Register Player")
with st.form("player_form"):
    name = st.text_input("Player Name")
    role = st.selectbox("Player Role", ["Batsman", "Bowler", "All-Rounder"])
    submitted = st.form_submit_button("Save Player")
    if submitted:
        if name.strip():
            success, msg = save_player(db, username, name.strip(), role)
            st.success(msg) if success else st.error(msg)
            if success:
                st.rerun()
        else:
            st.error("Player name cannot be empty.")

# Edit Existing Player Info
st.subheader("Edit Player Info")
if not df.empty:
    selected_player = st.selectbox("Select Player to Edit", df.index.tolist(), key="edit_player")
    existing_role = df.loc[selected_player]["role"]
    with st.form("edit_player_form"):
        new_name = st.text_input("New Name", value=selected_player)
        new_role = st.selectbox("New Role", ["Batsman", "Bowler", "All-Rounder"], index=["Batsman", "Bowler", "All-Rounder"].index(existing_role))
        update_submit = st.form_submit_button("Update Player")
        if update_submit:
            if new_name.strip():
                # First delete old entry, then save with new name/role
                delete_player(db, username, selected_player)
                success, msg = save_player(db, username, new_name.strip(), new_role)
                st.success("Player updated successfully.") if success else st.error("Error updating player.")
                if success:
                    st.rerun()
            else:
                st.error("Player name cannot be empty.")

# Add Match
st.subheader("Add Match Record")
if not df.empty:
    selected_player = st.selectbox("Select Player", df.index.tolist(), key="match_player")
    with st.form("match_form"):
        match_id = st.text_input("Match ID")
        runs = st.number_input("Runs", min_value=0)
        wickets = st.number_input("Wickets", min_value=0)
        catches = st.number_input("Catches", min_value=0)
        balls_faced = st.number_input("Balls Faced", min_value=0)
        fours = st.number_input("Fours", min_value=0)
        sixes = st.number_input("Sixes", min_value=0)
        balls_bowled = st.number_input("Balls Bowled", min_value=0)
        dot_balls = st.number_input("Dot Balls", min_value=0)
        submitted = st.form_submit_button("Save Match")
        if submitted:
            if match_id.strip():
                strike_rate = round((runs / balls_faced * 100), 2) if balls_faced > 0 else 0
                economy = round((runs / (balls_bowled / 6)), 2) if balls_bowled > 0 else 0
                efficiency = runs + wickets * 20 + catches * 10 + sixes * 2 + fours - dot_balls
                match_data = {
                    "runs": runs,
                    "wickets": wickets,
                    "catches": catches,
                    "balls_faced": balls_faced,
                    "fours": fours,
                    "sixes": sixes,
                    "balls_bowled": balls_bowled,
                    "dot_balls": dot_balls,
                    "strike_rate": strike_rate,
                    "economy": economy,
                    "efficiency": efficiency
                }
                success, msg = save_match(db, username, selected_player, match_id.strip(), **match_data)
                st.success(msg) if success else st.error(msg)
                if success:
                    st.rerun()
            else:
                st.error("Match ID cannot be empty.")

        # Delete Player
        st.subheader("Delete Player")
        if not df.empty:
            to_delete = st.selectbox("Select Player to delete", df.index.tolist(), key="delete_player")
            if st.button("Delete Player"):
                delete_player(db, username, to_delete)
                st.success(f"Deleted player '{to_delete}'")
                st.rerun()

        # Delete Match Record
        st.subheader("Delete Match Record")
        if not df.empty:
            selected_player = st.selectbox("Player Name", df.index.tolist(), key="del_match_player")
            matches_df = fetch_matches(db, username, selected_player)

            # Clean malformed rows (if any)
            if isinstance(matches_df, pd.DataFrame):
                matches_df = matches_df.dropna(how="all")

            if not matches_df.empty:
                match_id = st.selectbox("Select Match ID", matches_df.index.tolist(), key="match_id")

                # Safely extract match row
                match_row = matches_df.loc[match_id]

                # Handle match_row being a Series, string, or dict
                import json
                if isinstance(match_row, pd.Series):
                    match_row = match_row.to_dict()
                elif isinstance(match_row, str):
                    try:
                        match_row = json.loads(match_row)
                    except:
                        match_row = {}
                elif not isinstance(match_row, dict):
                    match_row = {}

                # Display match summary
                summary_data = {
                    "Runs": match_row.get("runs", "N/A"),
                    "Wickets": match_row.get("wickets", "N/A"),
                    "Catches": match_row.get("catches", "N/A"),
                    "Efficiency": match_row.get("efficiency", "N/A")
                }
                st.subheader("Selected Match Summary")
                st.table(pd.DataFrame([summary_data]))

                # Delete match button
                if st.button("Delete Match"):
                    delete_match(db, username, selected_player, match_id)
                    st.success(f"Deleted match '{match_id}' for {selected_player}")
                    st.rerun()
            else:
                st.warning("No valid match data found for this player.")

    # 2. Team Results
    if page == "Team Results":
        st.header("Team Results")
        df = fetch_players(db, username)

        if df.empty:
            st.warning("No players found. Add some first.")
        else:
            filter_role = st.selectbox("Filter by Role", ["All", "Batsman", "Bowler", "All-Rounder"])
            if filter_role != "All":
                df = df[df["role"].str.lower() == filter_role.lower()]
            
            df = df.fillna({"total_runs": 0, "total_wickets": 0, "total_catches": 0, "efficiency": 0})
            df = df.sort_values(by="efficiency", ascending=False).head(11)

            st.subheader("Top 11 Players by Efficiency")
            st.dataframe(df[["role", "efficiency", "total_runs", "total_wickets", "total_catches"]])
            st.markdown("**Efficiency formula:** Runs + (Wickets × 20) + (Catches × 10)")

    # 3. Player Analytics
    else:
        st.header("Player Analytics")
        df = fetch_players(db, username)
        if not df.empty:
            selected = st.selectbox("Select Player", df.index.tolist())
            player_data = df.loc[selected]
            st.subheader("Player Summary Statistics")
            st.markdown(
                f"""
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <div class="stats-box" style="background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: background-color 0.3s, color 0.3s;">
                        <strong>Role:</strong> {player_data['role']}
                    </div>
                    <div class="stats-box" style="background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: background-color 0.3s, color 0.3s;">
                        <strong>Efficiency:</strong> {player_data['efficiency']}
                    </div>
                    <div class="stats-box" style="background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: background-color 0.3s, color 0.3s;">
                        <strong>Total Runs:</strong> {player_data['total_runs']}
                    </div>
                    <div class="stats-box" style="background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: background-color 0.3s, color 0.3s;">
                        <strong>Total Wickets:</strong> {player_data['total_wickets']}
                    </div>
                    <div class="stats-box" style="background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: background-color 0.3s, color 0.3s;">
                        <strong>Total Catches:</strong> {player_data['total_catches']}
                    </div>
                </div>
                <style>
                    .stats-box:hover {{
                        background-color: black !important;
                        color: white !important;
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )
            match_df = fetch_matches(db, username, selected)
            if not match_df.empty:
                st.subheader("Match-wise Performance")
                st.dataframe(match_df)
                st.subheader("Performance Trend Visualizations")
                # Add a container for the expanders to apply staggered animation
                st.markdown('<div id="performance-trends-expanders">', unsafe_allow_html=True)
                
                # Use a custom class for easier targeting
                expander_css_class = "performance-expander"

                # Initialize session state for chart views
                metrics = ["runs", "wickets", "catches", "efficiency", "strike_rate", "economy"]
                for metric in metrics:
                    if f'{metric}_chart_view' not in st.session_state:
                        st.session_state[f'{metric}_chart_view'] = 'graph'

                with st.expander("Runs per Match"):
                    col1, col2 = st.columns([4, 1]) # Adjusted column ratio
                    with col1:
                         st.markdown("**Runs per Match**") # Re-add title here for layout
                    with col2:
                        button_label = f"Show { 'Graph' if st.session_state.runs_chart_view == 'pie' else 'Pie Chart'}"
                        if st.button(button_label, key="runs_toggle_button"):
                            st.session_state.runs_chart_view = 'graph' if st.session_state.runs_chart_view == 'pie' else 'pie'
                            st.rerun()

                    if st.session_state.runs_chart_view == 'graph':
                         st.line_chart(match_df["runs"])
                    else:
                        # For runs chart
                        runs_data = pd.DataFrame({
                            'Match ID': match_df.index.astype(str),
                            'Runs': match_df['runs'].astype(float)
                        })

                        chart = alt.Chart(runs_data).mark_arc(outerRadius=60).encode(
                            theta=alt.Theta('Runs:Q', stack=True),
                            color=alt.Color('Match ID:N'),
                            tooltip=['Match ID:N', 'Runs:Q']
                        ).properties(
                            title="Runs per Match"
                        )

                        st.altair_chart(chart, use_container_width=True)

                with st.expander("Wickets per Match"):
                    col1, col2 = st.columns([4, 1]) # Adjusted column ratio
                    with col1:
                         st.markdown("**Wickets per Match**") # Re-add title here for layout
                    with col2:
                        button_label = f"Show { 'Graph' if st.session_state.wickets_chart_view == 'pie' else 'Pie Chart'}"
                        if st.button(button_label, key="wickets_toggle_button"):
                            st.session_state.wickets_chart_view = 'graph' if st.session_state.wickets_chart_view == 'pie' else 'pie'
                            st.rerun()

                    if st.session_state.wickets_chart_view == 'graph':
                        st.line_chart(match_df["wickets"])
                    else:
                        # For wickets chart
                        wickets_data = pd.DataFrame({
                            'Match ID': match_df.index.astype(str),
                            'Wickets': match_df['wickets'].astype(float)
                        })

                        chart = alt.Chart(wickets_data).mark_arc(outerRadius=60).encode(
                            theta=alt.Theta('Wickets:Q', stack=True),
                            color=alt.Color('Match ID:N'),
                            tooltip=['Match ID:N', 'Wickets:Q']
                        ).properties(
                            title="Wickets per Match"
                        )

                        st.altair_chart(chart, use_container_width=True)

                with st.expander("Catches per Match"):
                    col1, col2 = st.columns([4, 1]) # Adjusted column ratio
                    with col1:
                         st.markdown("**Catches per Match**") # Re-add title here for layout
                    with col2:
                        button_label = f"Show { 'Graph' if st.session_state.catches_chart_view == 'pie' else 'Pie Chart'}"
                        if st.button(button_label, key="catches_toggle_button"):
                            st.session_state.catches_chart_view = 'graph' if st.session_state.catches_chart_view == 'pie' else 'pie'
                            st.rerun()

                    if st.session_state.catches_chart_view == 'graph':
                        st.line_chart(match_df["catches"])
                    else:
                        # For catches chart
                        catches_data = pd.DataFrame({
                            'Match ID': match_df.index.astype(str),
                            'Catches': match_df['catches'].astype(float)
                        })

                        chart = alt.Chart(catches_data).mark_arc(outerRadius=60).encode(
                            theta=alt.Theta('Catches:Q', stack=True),
                            color=alt.Color('Match ID:N'),
                            tooltip=['Match ID:N', 'Catches:Q']
                        ).properties(
                            title="Catches per Match"
                        )

                        st.altair_chart(chart, use_container_width=True)

                with st.expander("Efficiency Over Matches"):
                    col1, col2 = st.columns([4, 1]) # Adjusted column ratio
                    with col1:
                         st.markdown("**Efficiency Over Matches**") # Re-add title here for layout
                    with col2:
                        button_label = f"Show { 'Graph' if st.session_state.efficiency_chart_view == 'pie' else 'Pie Chart'}"
                        if st.button(button_label, key="efficiency_toggle_button"):
                            st.session_state.efficiency_chart_view = 'graph' if st.session_state.efficiency_chart_view == 'pie' else 'pie'
                            st.rerun()

                    if st.session_state.efficiency_chart_view == 'graph':
                         st.line_chart(match_df["efficiency"])
                    else:
                        # For efficiency chart
                        positive_efficiency = match_df["efficiency"].apply(lambda x: max(0, x))
                        if not positive_efficiency.sum() == 0:
                            efficiency_data = pd.DataFrame({
                                'Match ID': match_df.index.astype(str),
                                'Efficiency': positive_efficiency.astype(float)
                            })

                            chart = alt.Chart(efficiency_data).mark_arc(outerRadius=60).encode(
                                theta=alt.Theta('Efficiency:Q', stack=True),
                                color=alt.Color('Match ID:N'),
                                tooltip=['Match ID:N', 'Efficiency:Q']
                            ).properties(
                                title="Efficiency Over Matches"
                            )

                            st.altair_chart(chart, use_container_width=True)

                with st.expander("Strike Rate Over Matches"):
                    col1, col2 = st.columns([4, 1]) # Adjusted column ratio
                    with col1:
                         st.markdown("**Strike Rate Over Matches**") # Re-add title here for layout
                    with col2:
                        button_label = f"Show { 'Graph' if st.session_state.strike_rate_chart_view == 'pie' else 'Pie Chart'}"
                        if st.button(button_label, key="strike_rate_toggle_button"):
                            st.session_state.strike_rate_chart_view = 'graph' if st.session_state.strike_rate_chart_view == 'pie' else 'pie'
                            st.rerun()

                    if st.session_state.strike_rate_chart_view == 'graph':
                        st.line_chart(match_df["strike_rate"])
                    else:
                        # For strike rate chart
                        valid_strike_rates = match_df["strike_rate"].dropna()
                        if not valid_strike_rates.empty and not valid_strike_rates.sum() == 0:
                            strike_rate_data = pd.DataFrame({
                                'Match ID': valid_strike_rates.index.astype(str),
                                'Strike Rate': valid_strike_rates.astype(float)
                            })

                            chart = alt.Chart(strike_rate_data).mark_arc(outerRadius=60).encode(
                                theta=alt.Theta('Strike Rate:Q', stack=True),
                                color=alt.Color('Match ID:N'),
                                tooltip=['Match ID:N', 'Strike Rate:Q']
                            ).properties(
                                title="Strike Rate Over Matches"
                            )

                            st.altair_chart(chart, use_container_width=True)

                with st.expander("Economy Over Matches"):
                    col1, col2 = st.columns([4, 1]) # Adjusted column ratio
                    with col1:
                         st.markdown("**Economy Over Matches**") # Re-add title here for layout
                    with col2:
                         button_label = f"Show { 'Graph' if st.session_state.economy_chart_view == 'pie' else 'Pie Chart'}"
                         if st.button(button_label, key="economy_toggle_button"):
                            st.session_state.economy_chart_view = 'graph' if st.session_state.economy_chart_view == 'pie' else 'pie'
                            st.rerun()

                    if st.session_state.economy_chart_view == 'graph':
                        st.line_chart(match_df["economy"])
                    else:
                        # For economy chart
                        valid_economies = match_df["economy"].dropna()
                        if not valid_economies.empty and not valid_economies.sum() == 0:
                            economy_data = pd.DataFrame({
                                'Match ID': valid_economies.index.astype(str),
                                'Economy': valid_economies.astype(float)
                            })

                            chart = alt.Chart(economy_data).mark_arc(outerRadius=60).encode(
                                theta=alt.Theta('Economy:Q', stack=True),
                                color=alt.Color('Match ID:N'),
                                tooltip=['Match ID:N', 'Economy:Q']
                            ).properties(
                                title="Economy Over Matches"
                            )

                            st.altair_chart(chart, use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True) # Close the container

                st.markdown(
                    f"""
                    <style>
                    @keyframes expander-color-switch {{
                        0% {{ background-color: white; color: black; }}
                        50% {{ background-color: black; color: white; }}
                        100% {{ background-color: white; color: black; }}
                    }}

                    /* Target the specific expanders within the container */
                    #performance-trends-expanders .streamlit-expander > div[role="button"] {{
                        border: 1px solid rgba(0,0,0,0.1);
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                        padding: 10px;
                        animation: expander-color-switch 2s infinite step-start; /* Apply the animation */
                        color: black; /* Default text color */
                    }}

                    /* Stagger animation start for each expander within the container */
                    #performance-trends-expanders .streamlit-expander:nth-of-type(1) > div[role="button"] {{ animation-delay: 0s; }}
                    #performance-trends-expanders .streamlit-expander:nth-of-type(2) > div[role="button"] {{ animation-delay: 1s; }}
                    #performance-trends-expanders .streamlit-expander:nth-of-type(3) > div[role="button"] {{ animation-delay: 2s; }}
                    #performance-trends-expanders .streamlit-expander:nth-of-type(4) > div[role="button"] {{ animation-delay: 3s; }}
                    #performance-trends-expanders .streamlit-expander:nth-of-type(5) > div[role="button"] {{ animation-delay: 4s; }}
                    #performance-trends-expanders .streamlit-expander:nth-of-type(6) > div[role="button"] {{ animation-delay: 5s; }}

                    #performance-trends-expanders .streamlit-expander > div[role="button"]:hover {{
                         background-color: initial; /* Remove hover effect if animation is running */
                         color: initial;
                    }}

                    /* CSS to make the button smaller */
                    .stButton>button {{
                        padding-top: 0.1rem;
                        padding-bottom: 0.1rem;
                        font-size: 0.8rem;
                    }}

                     /* CSS for button hover effect */
                    .stButton>button:hover {{
                        background-color: black !important;
                        color: white !important; /* Ensure text is visible on black background */
                    }}

                     /* CSS to reduce space below expander titles */
                    .streamlit-expander > div[role="button"] p {{
                        margin-bottom: 0rem;
                    }}

                    </style>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.warning("No match records found for this player.")

# Entry point
def main():
    if not st.session_state['logged_in']:
        show_credentials()
    else:
        show_app()

if __name__ == "__main__":
    main()
