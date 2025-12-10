import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# BASIC CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="STUDENT DASHBOARD",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# SMALL CSS TOUCHES FOR A CLEAN, CLASSIC LOOK
# ---------------------------------------------------------
st.markdown("""
<style>
/* Card background automatically adapts in both themes */
.metric-card {
    padding: 16px;
    border-radius: 12px;
    background-color: rgba(255,255,255,0.12); /* Transparent white on dark, white on light */
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.2);
    margin-bottom: 10px;
}

/* Metric title */
.metric-card h3 {
    font-size: 1rem;
    margin-bottom: 6px;
    color: #ffffff;   /* Always visible in Dark mode */
    font-weight: 500;
}

/* Metric value */
.metric-card p {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;   /* Pure white -> visible on dark */
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "student_data.csv")

def load_data():
    if not os.path.exists(CSV_PATH):
        cols = [
            "student_id", "name", "subject", "marks",
            "exam_date", "att_id", "attendance_percentage",
            "dept", "semester"
        ]
        df = pd.DataFrame(columns=cols)
    else:
        df = pd.read_csv(CSV_PATH)

    # Ensure numeric fields
    df["marks"] = pd.to_numeric(df["marks"], errors="coerce")
    df["attendance_percentage"] = pd.to_numeric(df["attendance_percentage"], errors="coerce")
    df["semester"] = pd.to_numeric(df["semester"], errors="coerce")

    # Required computed fields
    df["is_fail"] = df["marks"] < 40
    df["fail_probability"] = np.where(df["marks"] < 40, 0.9, 0.2)

    return df

if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# ---------------------------------------------------------
# SIDEBAR – ADD STUDENT
# ---------------------------------------------------------
st.sidebar.title("🎓 STUDENT DASHBOARD")
st.sidebar.write("Monitor, analyze, and manage student performance.")

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Quick Add Student")

with st.sidebar.form("add_form", clear_on_submit=True):
    new_id = st.number_input("Student ID", min_value=1, step=1)
    new_name = st.text_input("Name")
    new_dept = st.text_input("Department (e.g. CSE, IT)", value="CSE")
    new_sem = st.number_input("Semester", min_value=1, max_value=8, step=1, value=1)

    existing_subjects = df["subject"].dropna().unique().tolist()
    if existing_subjects:
        new_sub = st.selectbox("Subject", existing_subjects)
    else:
        new_sub = st.text_input("Subject", value="Maths")

    new_marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=1.0, value=60.0)
    new_att = st.number_input("Attendance %", min_value=0.0, max_value=100.0, step=1.0, value=80.0)

    submitted = st.form_submit_button("Add Record")

if submitted:
    new_row = {
        "student_id": int(new_id),
        "name": new_name,
        "dept": new_dept,
        "semester": int(new_sem),
        "subject": new_sub,
        "marks": float(new_marks),
        "attendance_percentage": float(new_att),
        "exam_date": None,
        "att_id": None,
        "is_fail": new_marks < 40,
        "fail_probability": 0.9 if new_marks < 40 else 0.2
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state.df = df
    df.to_csv(CSV_PATH, index=False)
    st.sidebar.success("✅ Student record added!")

st.sidebar.markdown("---")

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.subheader("🔎 Filters")

subjects = st.sidebar.multiselect(
    "Subject",
    options=sorted(df["subject"].dropna().unique()),
    default=sorted(df["subject"].dropna().unique()),
)

semesters = st.sidebar.multiselect(
    "Semester",
    options=sorted(df["semester"].dropna().unique()),
    default=sorted(df["semester"].dropna().unique()),
)

depts = st.sidebar.multiselect(
    "Department",
    options=sorted(df["dept"].dropna().unique()),
    default=sorted(df["dept"].dropna().unique()),
)

filtered_df = df.copy()
if subjects:
    filtered_df = filtered_df[filtered_df["subject"].isin(subjects)]
if semesters:
    filtered_df = filtered_df[filtered_df["semester"].isin(semesters)]
if depts:
    filtered_df = filtered_df[filtered_df["dept"].isin(depts)]

# ---------------------------------------------------------
# MAIN LAYOUT – TABS
# ---------------------------------------------------------
st.title("📊 STUDENT DASHBOARD")
st.write("A classic, interactive and advanced view of student performance data.")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🏠 Overview", "📈 Analytics", "🛠 Manage Data"])

# ---------------------------------------------------------
# TAB 1 – OVERVIEW
# ---------------------------------------------------------
with tab1:
    col_a, col_b, col_c, col_d = st.columns(4)

    total_students = filtered_df["student_id"].nunique()
    avg_marks = filtered_df["marks"].mean() if not filtered_df.empty else 0
    avg_att = filtered_df["attendance_percentage"].mean() if not filtered_df.empty else 0
    fail_pct = (filtered_df["is_fail"].mean() * 100) if not filtered_df.empty else 0

    with col_a:
        st.markdown('<div class="metric-card"><h3>Total Students</h3>'
                    f'<p>{int(total_students)}</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="metric-card"><h3>Average Marks</h3>'
                    f'<p>{avg_marks:.1f}</p></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="metric-card"><h3>Average Attendance</h3>'
                    f'<p>{avg_att:.1f}%</p></div>', unsafe_allow_html=True)
    with col_d:
        st.markdown('<div class="metric-card"><h3>Fail Percentage</h3>'
                    f'<p>{fail_pct:.1f}%</p></div>', unsafe_allow_html=True)

    st.markdown("### 🏅 Top Performing Students")
    if not filtered_df.empty:
        top_df = (
            filtered_df.groupby(["student_id", "name", "dept"], as_index=False)["marks"]
            .mean()
            .sort_values("marks", ascending=False)
            .head(5)
        )
        st.table(top_df)
    else:
        st.info("No data available. Add some students from the sidebar to get started.")

# ---------------------------------------------------------
# TAB 2 – ANALYTICS
# ---------------------------------------------------------
with tab2:
    if filtered_df.empty:
        st.warning("No data to visualize. Add some records first.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("📍 Attendance vs Marks")
            fig1, ax1 = plt.subplots(figsize=(5,4))
            sns.scatterplot(
                data=filtered_df,
                x="attendance_percentage",
                y="marks",
                hue="subject",
                style="dept",
                ax=ax1
            )
            ax1.grid(True, alpha=0.3)
            st.pyplot(fig1)

        with c2:
            st.subheader("📈 Semester-wise Marks Trend")
            trend_df = (
                filtered_df.groupby("semester", as_index=False)["marks"]
                .mean()
                .sort_values("semester")
            )
            fig2, ax2 = plt.subplots(figsize=(5,4))
            sns.lineplot(
                data=trend_df,
                x="semester",
                y="marks",
                marker="o",
                ax=ax2
            )
            ax2.grid(True, alpha=0.3)
            st.pyplot(fig2)

        st.markdown("---")
        st.subheader("🔥 Subject-wise Heatmap (Marks)")

        heat_df = filtered_df.pivot_table(
            values="marks",
            index="student_id",
            columns="subject",
            aggfunc="mean"
        )

        fig3, ax3 = plt.subplots(figsize=(8,4))
        sns.heatmap(heat_df, annot=True, cmap="YlGnBu", ax=ax3)
        st.pyplot(fig3)

        st.markdown("---")
        st.subheader("⚠️ Fail Probability Table")

        show_cols = [
            "student_id", "name", "dept", "semester",
            "subject", "attendance_percentage", "marks", "fail_probability"
        ]

        st.dataframe(filtered_df[show_cols].sort_values("fail_probability", ascending=False))

# ---------------------------------------------------------
# TAB 3 – MANAGE DATA (FULL CRUD WORKING)
# ---------------------------------------------------------
with tab3:
    st.subheader("🛠 Full Data Editor")

    st.write("""
    Edit any cell, add rows, or delete rows.
    Click **Save Changes** to update your data permanently.
    """)

    editable_df = df.copy()

    edited_df = st.data_editor(
        editable_df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_table"
    )

    if st.button("💾 Save Changes"):
        edited_df["marks"] = pd.to_numeric(edited_df["marks"], errors="coerce")
        edited_df["attendance_percentage"] = pd.to_numeric(edited_df["attendance_percentage"], errors="coerce")
        edited_df["semester"] = pd.to_numeric(edited_df["semester"], errors="coerce")

        edited_df["is_fail"] = edited_df["marks"] < 40
        edited_df["fail_probability"] = np.where(edited_df["marks"] < 40, 0.9, 0.2)

        edited_df.to_csv(CSV_PATH, index=False)
        st.session_state.df = edited_df

        st.success("✅ Changes saved successfully!")
        st.experimental_rerun()
