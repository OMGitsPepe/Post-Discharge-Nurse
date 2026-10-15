import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_csv(filename):
    file_path = DATA_DIR / filename
    return pd.read_csv(file_path, dtype=str)


def load_tables():
    date_columns = {
        "patients": ["BIRTHDATE", "DEATHDATE"],
        "encounters": ["START", "STOP"],
        "conditions": ["START", "STOP"],
        "medications": ["START", "STOP"],
        "observations": ["DATE"],
        "procedures": ["START", "STOP"],
        "careplans": ["START", "STOP"],
    }

    tables = {}

    for table_name, columns in date_columns.items():
        table = load_csv(f"{table_name}.csv")

        for column in columns:
            table[column] = pd.to_datetime(
                table[column],
                utc=True,
                errors="raise",
            )

        tables[table_name] = table

    return tables


def get_hospital_discharge_medications(medications, patient_id, encounter_id, discharge_time):
    matches = (
            (medications["PATIENT"] == patient_id)
            & (medications["ENCOUNTER"] == encounter_id)
            & (medications["START"] <= discharge_time)
            & (medications["STOP"].isna()
               | (medications["STOP"] > discharge_time)
               )
    )

    columns = ["CODE", "DESCRIPTION", "START"]

    return medications.loc[matches, columns].copy().sort_values("START")


def get_discharge_careplans(careplans, patient_id, encounter_id, discharge_time):
    matches = (
            (careplans["PATIENT"] == patient_id)
            & (careplans["ENCOUNTER"] == encounter_id)
            & (careplans["START"] <= discharge_time)
            & (careplans["STOP"].isna()
               | (careplans["STOP"] > discharge_time)
               )
    )

    columns = ["CODE", "DESCRIPTION", "START", "STOP"]
    selected = careplans.loc[matches, columns].copy()

    future_stop = selected["STOP"] > discharge_time
    selected.loc[future_stop, "STOP"] = pd.NaT

    return selected


def get_episode_procedures(procedures, patient_id, encounter_ids, discharge_time):
    matches = (
            (procedures["PATIENT"] == patient_id)
            & procedures["ENCOUNTER"].isin(encounter_ids)
            & (procedures["START"] <= discharge_time)
            & (procedures["STOP"] <= discharge_time)
    )

    columns = ["START", "STOP", "SYSTEM", "CODE", "DESCRIPTION"]

    selected = procedures.loc[matches, columns].copy()

    return selected.sort_values("START")


def get_episode_observations(observations, patient_id, encounter_ids, discharge_time):
    matches = (
            (observations["PATIENT"] == patient_id)
            & observations["ENCOUNTER"].isin(encounter_ids)
            & (observations["DATE"] <= discharge_time)
    )

    columns = ["DATE", "CATEGORY", "CODE", "DESCRIPTION", "VALUE", "UNITS",
               "TYPE"]

    selected = observations.loc[matches, columns].copy()

    return selected.sort_values("DATE")


def get_patient_info(patients, patient_id):
    columns = ["Id", "BIRTHDATE", "GENDER", "FIRST", "LAST"]

    matching_patients = patients.loc[patients["Id"] == patient_id, columns]

    if len(matching_patients) != 1:
        raise ValueError("Expected exactly one matching patient.")

    return matching_patients.iloc[0].to_dict()


def get_condition_history(conditions, patient_id, discharge_time):
    matches = (
            (conditions["PATIENT"] == patient_id)
            & (conditions["START"] <= discharge_time)
    )

    columns = ["START", "STOP", "SYSTEM", "CODE", "DESCRIPTION"]
    selected = conditions.loc[matches, columns].copy()

    future_stop = selected["STOP"] > discharge_time
    selected.loc[future_stop, "STOP"] = pd.NaT

    return selected.sort_values("START")


def get_encounter(encounters, patient_id, encounter_id, expected_class):
    matches = encounters.loc[
        (encounters["Id"] == encounter_id)
        & (encounters["PATIENT"] == patient_id)
        ]

    if len(matches) != 1:
        raise ValueError("Expected exactly one matching encounter.")

    encounter = matches.iloc[0]

    if encounter["ENCOUNTERCLASS"] != expected_class:
        raise ValueError(f"Expected an {expected_class} encounter.")

    if pd.isna(encounter["START"]) or pd.isna(encounter["STOP"]):
        raise ValueError("The encounter is missing a start or end time.")

    if encounter["STOP"] < encounter["START"]:
        raise ValueError("The encounter ends before it starts.")

    return encounter


def build_discharge_context(tables, patient_id, emergency_encounter_id, hospitalization_id):
    emergency = get_encounter(
        tables["encounters"],
        patient_id,
        emergency_encounter_id,
        "emergency",
    )

    hospitalization = get_encounter(
        tables["encounters"],
        patient_id,
        hospitalization_id,
        "inpatient",
    )

    discharge_time = hospitalization["STOP"]

    if emergency["START"] > hospitalization["START"] or emergency["STOP"] > discharge_time:
        raise ValueError("Review the selected episode chronology.")

    episode_ids = [emergency_encounter_id, hospitalization_id]

    return {
        "patient": get_patient_info(
            tables["patients"], patient_id
        ),
        "emergency_encounter_id": emergency_encounter_id,
        "hospitalization_id": hospitalization_id,
        "admission_time": hospitalization["START"],
        "discharge_time": discharge_time,
        "hospitalization_reason": hospitalization["REASONDESCRIPTION"],
        "medications": get_hospital_discharge_medications(
            tables["medications"],
            patient_id,
            hospitalization_id,
            discharge_time,
        ),
        "careplans": get_discharge_careplans(
            tables["careplans"],
            patient_id,
            hospitalization_id,
            discharge_time,
        ),
        "procedures": get_episode_procedures(
            tables["procedures"],
            patient_id,
            episode_ids,
            discharge_time,
        ),
        "observations": get_episode_observations(
            tables["observations"],
            patient_id,
            episode_ids,
            discharge_time,
        ),
        "condition_history": get_condition_history(
            tables["conditions"],
            patient_id,
            discharge_time,
        ),
    }


if __name__ == "__main__":
    tables = load_tables()

    context = build_discharge_context(
        tables=tables,
        patient_id="a42c1220-8d98-cc86-a46f-099e66c3b165",
        emergency_encounter_id="a42c1220-8d98-cc86-d678-12b2ba3b5df5",
        hospitalization_id="a42c1220-8d98-cc86-c5d8-a2f1111e8c9f",
    )

    patient = context["patient"]

    print("Patient:", patient["FIRST"], patient["LAST"])
    print("Hospitalization reason:", context["hospitalization_reason"])
    print("Admission time:", context["admission_time"])
    print("Discharge time:", context["discharge_time"])

    print("\nDischarge context:")
    for section in [
        "medications",
        "careplans",
        "procedures",
        "observations",
        "condition_history",
    ]:
        print(f"{section}: {len(context[section])} records")
