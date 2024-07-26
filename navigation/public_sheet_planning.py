import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection




RPE_to_pct = st.session_state["RPE_to_pct_fun"]
round_to_multiple = st.session_state["round_to_multiple_fun"]



if "round_multiple" in st.session_state:
    round_multiple = st.session_state["round_multiple"]

if "metadata_spreadsheet_url" in st.session_state:
    metadata_spreadsheet_url = st.session_state["metadata_spreadsheet_url"]

if metadata_spreadsheet_url:

    #--- read google sheets ------------------------------------------------------------------------

    metadata_conn = st.connection("gsheets", type = GSheetsConnection)
    metadata_df = metadata_conn.read(spreadsheet = metadata_spreadsheet_url, ttl = 5)


    metadata_df.set_index("spreadsheet", inplace = True)

    st.dataframe(metadata_df)

    # program
    program_conn = st.connection("gsheets", type = GSheetsConnection)
    program_df = program_conn.read(spreadsheet = metadata_df.loc["program", "url"])
    program_df["date"] = pd.to_datetime(program_df["date"], format = "%d.%m.%Y")

    st.markdown("## Program")
    st.dataframe(program_df)

    # override_1RM
    override_1RM_conn = st.connection("gsheets", type = GSheetsConnection)
    override_1RM_df = override_1RM_conn.read(spreadsheet = metadata_df.loc["override_1RM", "url"])
    override_1RM_df["date"] = pd.to_datetime(override_1RM_df["date"], format = "%d.%m.%Y")

    st.markdown("## 1RM override")
    st.dataframe(override_1RM_df)

    # actual progression
    actual_progression_conn = st.connection("gsheets", type = GSheetsConnection)
    actual_progression_df = actual_progression_conn.read(spreadsheet = metadata_df.loc["actual_progression", "url"])
    actual_progression_df["date"] = pd.to_datetime(actual_progression_df["date"], format = "%d.%m.%Y")


    # variations
    variations_conn = st.connection("gsheets", type = GSheetsConnection)
    variations_df = variations_conn.read(spreadsheet = metadata_df.loc["variations", "url"])
    st.session_state["variations_df"] = variations_df

    st.markdown("## Variations")
    st.dataframe(variations_df)
    



    # join program_df with variations_df on exercise
    # program_df = (program_df
    #               .merge(variations_df, left_on = "exercise", right_on = "variation")
    #               .drop(columns=['variation'])
    #             #   .apply(lambda row: )
    # )

    # st.write(program_df)
    

    increments = variations_df[["base_lift", "microcycle_increment"]].drop_duplicates()
    increments["daily_increment"] = increments["microcycle_increment"] / 7
    st.session_state["increments"] = increments

    st.markdown("## Increments")
    st.write(increments)

    base_lift_progression = (program_df
                             .merge(variations_df, left_on = "exercise", right_on = "variation")
                             .drop(columns=['variation'])
                             .groupby("base_lift")["date"]
                             .unique()
                             .to_frame()
                             .explode(column = "date")
                             .reset_index()
                             .merge(override_1RM_df, on = ["date", "base_lift"], how = "outer")
                             .sort_values(by = ["base_lift", "date"])
                             # join microcycle weight increments
                             .merge(variations_df[["base_lift", "microcycle_increment"]].drop_duplicates(), on = "base_lift", how = "inner")
                            #  .set_index("date")
    )

    # base_lift_progression["override_group"] = base_lift_progression["override_1RM"].groupby("base_lift").isna().cumsum()

    # base_lift_progression["planned_1RM"] = base_lift_progression.groupby("base_lift")["1RM"].cumsum()

    st.markdown("## Base Lift Progression")
    st.write(base_lift_progression)
    # st.write(base_lift_progression.dtypes)

    #--- calculate stats for actual progression --------------------------------------------------------------------------------

    # join actual_progression_df with program_df to get planned weight, reps, RPE and variations_df to get variation_pct_of_1RM 
    actual_progression_df = (actual_progression_df
                             .merge(program_df, on = ["exercise", "date", "set_type"], suffixes = ("_actual", "_planned"))
                             .drop(columns = ["sets"])
                             .merge(variations_df, left_on = "exercise", right_on = "variation")
                             .drop(columns = ["variation"])
                             .rename(columns = {"weight": "weight_actual"})
                             .sort_values(by = ["date", "set_number"])
    )

    # calculate the planned percentage of 1RM given the planned reps and RPE
    actual_progression_df["pct_load_planned"] = actual_progression_df.apply(lambda row: RPE_to_pct(row["reps_planned"], row["RPE_planned"], row["RPE-to-pct-1RM"], row["variation_pct_of_1RM"]), axis = 1)

    # calculate e1RM and mean e1RM for actual progression
    actual_progression_df["e1RM"] = actual_progression_df.apply(lambda row: row["weight_actual"] / RPE_to_pct(row["reps_actual"], row["RPE_actual"], row["RPE-to-pct-1RM"], row["variation_pct_of_1RM"]), axis = 1)
    actual_progression_df["mean_e1RM"] = actual_progression_df.groupby(["date", "exercise"])["e1RM"].transform("mean")

    # calculate potential reps (actual progression and planned)
    actual_progression_df["potential_reps_planned"] = actual_progression_df["reps_planned"] + (10 - actual_progression_df["RPE_planned"])
    actual_progression_df["potential_reps_actual"] = actual_progression_df["reps_actual"] + (10 - actual_progression_df["RPE_actual"])

    # calculate mean potential reps for (actual progression and planned)
    actual_progression_df["mean_potential_reps_planned"] = actual_progression_df.groupby(["date", "exercise"])["potential_reps_planned"].transform("mean")
    actual_progression_df["mean_potential_reps_actual"] = actual_progression_df.groupby(["date", "exercise"])["potential_reps_actual"].transform("mean")

    actual_progression_df["mean_weight_actual"] = actual_progression_df.groupby(["date", "exercise"])["weight_actual"].transform("mean")


    actual_progression_df = actual_progression_df.merge(override_1RM_df, on = ["date", "base_lift"], how = "left")


    # add columns for planned 1RM and weight
    actual_progression_df["planned_1RM"] = pd.NA
    actual_progression_df["weight_planned"] = pd.NA

    # create empty dataframe to which all planned base lift progressions will be appended
    all_planned_base_lift_progressions = pd.DataFrame()

    for base_lift, base_lift_df in actual_progression_df.groupby("base_lift"):

        # get all relevant dates uniquely, dates from the program
        # and dates on which this specific base lift 1RM is overridden
        base_lift_override_1RM_df = override_1RM_df.loc[override_1RM_df["base_lift"] == base_lift]
        unique_dates = np.sort(pd.concat([base_lift_progression.loc[base_lift_progression["base_lift"] == base_lift, "date"], base_lift_override_1RM_df["date"]]).unique())
       
        actual_progression_df.set_index(["date", "base_lift"], inplace = True)

        # construct dataframe to store the planned progression for a given base lift
        planned_base_lift_progression = pd.DataFrame(columns = ["base_lift", "date", "planned_1RM", "mean_e1RM", "adjust_planned_1RM_using_e1RM"])
        planned_base_lift_progression["date"] = unique_dates
        planned_base_lift_progression["base_lift"] = base_lift
        # add the override 1RM values
        planned_base_lift_progression = planned_base_lift_progression.merge(override_1RM_df, on = ["date", "base_lift"], how = "left")

        # get the daily increment for the current base lift
        daily_base_lift_increment = float(increments.loc[increments["base_lift"] == base_lift, "daily_increment"])

        # loop over all dates in the progression
        for i, date in enumerate(unique_dates):
            
            # set planned 1RM to override 1RM
            if not pd.isna(planned_base_lift_progression.at[i, "override_1RM"]):
                planned_base_lift_progression.at[i, "planned_1RM"] = planned_base_lift_progression.at[i, "override_1RM"]

            if date == unique_dates[0]:
                # if there exists no override 1RM on the first date of a program, set planned 1RM to 0 so it is not NA and won't throw errors
                if pd.isna(planned_base_lift_progression.at[0, "override_1RM"]):
                    planned_base_lift_progression.at[0, "planned_1RM"] = 0

            # write the planned 1RM in the actual progression dataframe (for the base lift)
            base_lift_df.loc[base_lift_df["date"] == date, "planned_1RM"] = planned_base_lift_progression.at[i, "planned_1RM"]
            # then use the planned 1RM to calculate the planned weight
            base_lift_df.loc[base_lift_df["date"] == date, "weight_planned"] = base_lift_df.loc[base_lift_df["date"] == date, "planned_1RM"] * base_lift_df.loc[base_lift_df["date"] == date, "pct_load_planned"]
            # add column for weights rounded to the nearest multiple
            base_lift_df.loc[base_lift_df["date"] == date, "weight_planned_rounded"] = base_lift_df.loc[base_lift_df["date"] == date, "weight_planned"].apply(lambda x: round_to_multiple(x, round_multiple))

            # make sure date is in the plan, if not the date came from the override 1RM dataframe and has
            # been handled above
            if date in base_lift_progression.loc[base_lift_progression["base_lift"] == base_lift]["date"].tolist():
                # subset the actual progression dataframe for the base lift appropriately
                # only use rows for the current date and ensure that the row should be used for 1RM planning
                base_lift_df_subset = base_lift_df.loc[(base_lift_df["date"] == date) & (base_lift_df["use_for_1RM_planning"] == True)]
                # st.write(base_lift_df_subset)

                mean_potential_reps_actual = base_lift_df_subset["potential_reps_actual"].mean()
                mean_potential_reps_planned = base_lift_df_subset["potential_reps_planned"].mean()

                mean_weight_actual = base_lift_df_subset["weight_actual"].mean()
                mean_weight_planned = base_lift_df_subset["weight_planned_rounded"].mean()

                
                # check if RPE or weight is off by more than 0.5 or 1.25 kg respectively
                if (
                    abs(mean_potential_reps_actual - mean_potential_reps_planned) > 0.5
                    or abs(mean_weight_actual - mean_weight_planned) > 1.25
                    ):
                    planned_base_lift_progression.at[i, "adjust_planned_1RM_using_e1RM"] = True
                else:
                    planned_base_lift_progression.at[i, "adjust_planned_1RM_using_e1RM"] = False

                # writing the mean e1RM into the base lift progression dataframe
                if base_lift_df_subset.empty: 
                    # this is empty if all exercises performed on this day are not to be used for 1RM planning
                    # if this is the case just use the mean e1RM from those exercises
                    planned_base_lift_progression.at[i, "mean_e1RM"] = base_lift_df.loc[base_lift_df["date"] == date, "e1RM"].mean()
                else:
                    # otherwise use the mean e1RM from the exercises that are to be used for 1RM planning
                    planned_base_lift_progression.at[i, "mean_e1RM"] = base_lift_df_subset["e1RM"].mean()

                mean_e1RM = planned_base_lift_progression.at[i, "mean_e1RM"]

                # update planned 1RM
                if i != len(unique_dates) - 1: # if not the last date
                    if planned_base_lift_progression.at[i, "adjust_planned_1RM_using_e1RM"] == True:
                        planned_base_lift_progression.at[i+1, "planned_1RM"] = mean_e1RM
                    else:
                        days_since_last_day = (unique_dates[i+1] - unique_dates[i]).astype("timedelta64[D]").astype(int)
                        planned_base_lift_progression.at[i+1, "planned_1RM"] = planned_base_lift_progression.at[i, "planned_1RM"] + daily_base_lift_increment * days_since_last_day


            
            actual_progression_df.update(planned_base_lift_progression.set_index(["date", "base_lift"]))
            actual_progression_df["weight_planned"] = actual_progression_df.apply(lambda row: row["planned_1RM"] * row["pct_load_planned"], axis = 1)
            actual_progression_df["weight_planned_rounded"] = actual_progression_df["weight_planned"].apply(lambda x: round_to_multiple(x, round_multiple))


        st.markdown(f"## planned {base_lift} progression")
        st.write(planned_base_lift_progression)
        
        all_planned_base_lift_progressions = pd.concat([all_planned_base_lift_progressions, planned_base_lift_progression])

        actual_progression_df.reset_index(inplace = True)


        st.markdown(f"## {base_lift}")
        st.write(base_lift_df)

    st.session_state["all_planned_base_lift_progressions"] = all_planned_base_lift_progressions
    
    actual_progression_df.sort_values(by = ["date", "base_lift", "set_number"], inplace = True)

    st.markdown("## Actual Progression")
    st.dataframe(actual_progression_df)


    st.markdown("## all planned base lift progressions")
    st.write(all_planned_base_lift_progressions)


    program_df = (program_df
                  .merge(variations_df, left_on = "exercise", right_on = "variation")              
                  .drop(columns=['variation', 'microcycle_increment', 'use_for_1RM_planning'])
                  .merge(all_planned_base_lift_progressions, on = ["date", "base_lift"], how = "left")
    )

    program_df["pct_load_planned"] = program_df.apply(lambda row: RPE_to_pct(row["reps"], row["RPE"], row["RPE-to-pct-1RM"], row["variation_pct_of_1RM"]), axis = 1)
    program_df["weight_planned"] = program_df["planned_1RM"] * program_df["pct_load_planned"]
    program_df["weight_planned_rounded"] = program_df["weight_planned"].apply(lambda x: round_to_multiple(x, round_multiple))

    # sort by date and set_type
    program_df["set_type_order"] = program_df["set_type"].replace({"top": 0, "backoff": 1, "backoff 1": 2, "backoff 2": 3})
    program_df.sort_values(by = ["date", "set_type_order"], inplace = True)
    program_df.drop(columns = ["set_type_order"], inplace = True)
    

    st.markdown("## Planned Progression")
    st.write(program_df)

    st.session_state["program_df"] = program_df
    
    # join actual_progression_df with variations_df on exercise
    # st.markdown("## Stats")
    # stats_df = (actual_progression_df
    #             .merge(variations_df, left_on = "exercise", right_on = "variation")
    #             .drop(columns=['variation']))

    # # join stats_df with program_df on exercise, date, set_type
    # stats_df = (stats_df
    #             .merge(program_df,
    #                    on = ["exercise", "date", "set_type"],
    #                    suffixes = ("_actual", "_planned")))

    # st.write(stats_df)

    # stats_df["e1RM"] = stats_df.apply(lambda row: RPE_to_pct(row["reps"], row["RPE"], row[""], row["variation_adj_factor"]), axis = 1)

    

    