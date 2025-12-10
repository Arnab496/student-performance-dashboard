import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Student Dashboard", layout="wide")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
df = pd.read_csv("student_data.csv")

# ---------------------------------------------------------
# SIDEBAR – USER INPUT FORM
# ---------------------------------------------------------
st.sidebar.header("➕ Add New Student Record")

with st.sidebar.form("add_form"):
    new_id = st.number_input("Student ID", min_value=1, step=1)
    new_name = st.text_input("Student Name")
    new_sub = st.selectbox("Subject", df["subject"].unique())
    new_marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=1.0)
    new_att = st.number_input("Attendance %", min_value=0.0, max_value=100.0, step=1.0)
    new_sem = st.selectbox("Semester", df["semester"].unique())

    submitted = st.form_submit_button("Save")

if submitted:
    new_row = {
        "student_id": new_id,
        "name": new_name,
        "subject": new_sub,
        "marks": new_marks,
        "attendance_percentage": new_att,
        "semester": new_sem,
        "is_fail": new_marks < 40,
        "fail_probability": 1 if new_marks < 40 else 0
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("student_data.csv", index=False)
    st.sidebar.success("Student Record Added! Refresh Page!")

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.title("🔎 Filters")

subjects = st.sidebar.multiselect(
    "Select Subject",
    options=df["subject"].unique(),
    default=df["subject"].unique()
)

semesters = st.sidebar.multiselect(
    "Select Semester",
    options=df["semester"].unique(),
    default=df["semester"].unique()
)

df_filtered = df[
    (df["subject"].isin(subjects)) &
    (df["semester"].isin(semesters))
]

# ---------------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------------
st.title("📊 Student Performance Analytics Dashboard")
st.markdown("---")

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Students", df_filtered['student_id'].nunique())
col2.metric("Average Marks", round(df_filtered['marks'].mean(), 2))
col3.metric("Average Attendance", f"{round(df_filtered['attendance_percentage'].mean(), 1)}%")
col4.metric("Fail %", f"{round(df_filtered['is_fail'].mean()*100, 2)}%")

st.markdown("---")

# ---------------------------------------------------------
# SCATTER PLOT
# ---------------------------------------------------------
st.header("📍 Attendance vs Marks")

fig1, ax1 = plt.subplots(figsize=(5,4))
ax1.scatter(df_filtered["attendance_percentage"], df_filtered["marks"])
ax1.set_xlabel("Attendance (%)")
ax1.set_ylabel("Marks")
ax1.set_title("Attendance vs Marks")
ax1.grid(True)
st.pyplot(fig1)

# ---------------------------------------------------------
# SEMESTER TREND
# ---------------------------------------------------------
st.header("📈 Semester-wise Average Marks")

sem_trend = df_filtered.groupby("semester")["marks"].mean()

fig2, ax2 = plt.subplots(figsize=(6,4))
ax2.plot(sem_trend.index, sem_trend.values, marker="o")
ax2.set_xlabel("Semester")
ax2.set_ylabel("Average Marks")
ax2.set_title("Marks Trend Across Semesters")
ax2.grid(True)
st.pyplot(fig2)

# ---------------------------------------------------------
# HEATMAP
# ---------------------------------------------------------
st.header("🔥 Subject-wise Performance Heatmap")

pivot_df = df_filtered.pivot_table(values="marks", index="student_id", columns="subject")

fig3, ax3 = plt.subplots(figsize=(8,4))
sns.heatmap(pivot_df, annot=True, cmap="YlGnBu", ax=ax3)
st.pyplot(fig3)

# ---------------------------------------------------------
# FAIL PROBABILITY TABLE
# ---------------------------------------------------------
st.header("⚠️ Fail Probability Table")

fail_df = df_filtered[[
    "student_id", "name", "subject",
    "attendance_percentage", "marks", "fail_probability"
]]

st.dataframe(fail_df)
