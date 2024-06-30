import streamlit as st
import pandas as pd


def validate_sheets(xls):
    required_sheets = ['Volunteer Data', 'Soldier Data']
    missing_sheets = [sheet for sheet in required_sheets if
                      sheet not in xls.sheet_names]
    if missing_sheets:
        return False, f"Missing sheets: {', '.join(missing_sheets)}"
    return True, None


def validate_columns(df, required_columns, sheet_name):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing columns in {sheet_name}: {', '.join(missing_columns)}"
    return True, None


def match_soldiers_to_volunteers(soldiers, volunteers):
    matches = []
    unmatched_soldiers = soldiers.copy()
    unmatched_volunteers = volunteers.copy()

    for volunteer in volunteers:
        preferred_soldiers = [
            soldier for soldier in unmatched_soldiers
            if soldier['City'] == volunteer['City'] and
               (volunteer['Religiosity'] != 'High' or soldier['Gender'] == volunteer[
                   'Gender'])
        ]

        if not preferred_soldiers:
            preferred_soldiers = [
                soldier for soldier in unmatched_soldiers
                if volunteer['Religiosity'] != 'High' or soldier['Gender'] == volunteer[
                    'Gender']
            ]

        if not preferred_soldiers:
            preferred_soldiers = unmatched_soldiers

        if preferred_soldiers:
            match = preferred_soldiers[0]
            matches.append({'Volunteer': volunteer['Name'], 'Soldier': match['Name']})
            unmatched_soldiers.remove(match)
            unmatched_volunteers.remove(volunteer)

    for soldier in unmatched_soldiers:
        if unmatched_volunteers:
            volunteer = unmatched_volunteers[0]
            matches.append({'Volunteer': volunteer['Name'], 'Soldier': soldier['Name']})
            unmatched_volunteers.remove(volunteer)

    return matches


# Example data for the XLSX file
volunteer_data = {
    "Name": ["David Cohen", "Sara Levy"],
    "Address": ["123 Kibbutz Galuyot St, Tel Aviv", "456 Herzl St, Jerusalem"],
    "City": ["Tel Aviv", "Jerusalem"],
    "Gender": ["Male", "Female"],
    "Religiosity": ["High", "Medium"]
}

soldier_data = {
    "Name": ["Michael Goldstein", "Rebecca Shapiro"],
    "Address": ["789 Ben Yehuda St, Haifa", "101 Hillel St, Rishon LeZion"],
    "City": ["Haifa", "Rishon LeZion"],
    "Gender": ["Male", "Female"],
    "Religiosity": ["Low", "High"]
}

# Create a DataFrame
df_volunteers = pd.DataFrame(volunteer_data)
df_soldiers = pd.DataFrame(soldier_data)

# Save to an Excel file
example_file = "example_file.xlsx"
with pd.ExcelWriter(example_file) as writer:
    df_volunteers.to_excel(writer, sheet_name='Volunteer Data', index=False)
    df_soldiers.to_excel(writer, sheet_name='Soldier Data', index=False)

# Set page config for layout and color
st.set_page_config(page_title="Soldier to Volunteer Matcher", page_icon=":handshake:",
                   layout="centered")

st.title("עמותת אח גדול - Soldier to Volunteer Matcher")
st.markdown("""
## Empowering Soldiers with Community Support
Welcome to our platform where we connect soldiers with dedicated volunteers who have walked a similar path. Our mission is to provide personal guidance, assistance with rights, and integration into Israeli society.
""")

with open(example_file, "rb") as file:
    btn = st.download_button(
        label="Download an example XLSX file",
        data=file,
        file_name="example_file.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

uploaded_file = st.file_uploader("Upload an XLSX file", type=["xlsx"],
                                 help="Upload your Excel file containing the volunteer and soldier data.")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)

    valid, error = validate_sheets(xls)
    if not valid:
        st.error(error)
    else:
        df_volunteers = pd.read_excel(xls, sheet_name='Volunteer Data')
        df_soldiers = pd.read_excel(xls, sheet_name='Soldier Data')

        volunteer_columns = ['Name', 'Address', 'City', 'Gender', 'Religiosity']
        soldier_columns = ['Name', 'Address', 'City', 'Gender', 'Religiosity']

        valid, error = validate_columns(df_volunteers, volunteer_columns,
                                        'Volunteer Data')
        if not valid:
            st.error(error)
        else:
            valid, error = validate_columns(df_soldiers, soldier_columns,
                                            'Soldier Data')
            if not valid:
                st.error(error)
            else:
                volunteers_list = df_volunteers.to_dict('records')
                soldiers_list = df_soldiers.to_dict('records')

                matched_data = match_soldiers_to_volunteers(soldiers_list,
                                                            volunteers_list)

                df_matches = pd.DataFrame(matched_data)

                st.markdown("### Matched Pairs")
                st.dataframe(df_matches)
