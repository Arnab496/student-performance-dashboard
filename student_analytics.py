import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# ----------------------------------
# 1. CONNECT TO MYSQL DATABASE
# ----------------------------------
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Arnab@123",   # <-- PUT YOUR MYSQL PASSWORD
    database="student_analytics"
)

print("✅ Connected to MySQL")

# ----------------------------------
# 2. LOAD TABLES FROM SQL
# ----------------------------------
students_df = pd.read_sql("SELECT * FROM students", conn)
marks_df = pd.read_sql("SELECT * FROM marks", conn)
attendance_df = pd.read_sql("SELECT * FROM attendance", conn)

conn.close()

print("\nStudents:")
print(students_df)
print("\nMarks:")
print(marks_df)
print("\nAttendance:")
print(attendance_df)

# ----------------------------------
# 3. MERGE DATA
# ----------------------------------
df = marks_df.merge(attendance_df, on=["student_id", "subject"])
df = df.merge(students_df, on="student_id")

print("\nMerged Data:")
print(df)

# ----------------------------------
# 4. SAVE CSV FOR STREAMLIT
# ----------------------------------
df.to_csv("student_data.csv", index=False)
print("\n📁 Saved merged CSV as student_data.csv")

# ----------------------------------
# 5. VISUALIZATIONS
# ----------------------------------

# Scatter plot
plt.figure(figsize=(6,4))
plt.scatter(df["attendance_percentage"], df["marks"])
plt.xlabel("Attendance (%)")
plt.ylabel("Marks")
plt.title("Attendance vs Marks")
plt.grid(True)
plt.show()

# Trend line
sem_trend = df.groupby("semester")["marks"].mean()

plt.figure(figsize=(6,4))
plt.plot(sem_trend.index, sem_trend.values, marker='o')
plt.xlabel("Semester")
plt.ylabel("Avg Marks")
plt.title("Semester-wise Performance Trend")
plt.grid(True)
plt.show()

# Heatmap
pivot_df = df.pivot_table(values="marks", index="student_id", columns="subject")

plt.figure(figsize=(6,4))
sns.heatmap(pivot_df, annot=True, cmap="YlGnBu")
plt.title("Subject-wise Performance Heatmap")
plt.show()

# ----------------------------------
# 6. FAIL PREDICTION MODEL
# ----------------------------------
df["is_fail"] = df["marks"] < 40

X = df[["attendance_percentage"]]
y = df["is_fail"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = LogisticRegression()
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print("\n🤖 Model Accuracy:", accuracy)

# ADD FAIL PROBABILITY (IMPORTANT)
df["fail_probability"] = model.predict_proba(X)[:,1]

print("\nFail Risk Predictions:")
print(df[[
    "student_id", "name", "subject",
    "attendance_percentage", "marks", "fail_probability"
]])

# ----------------------------------
# 7. SAVE UPDATED CSV
# ----------------------------------
df.to_csv("student_data.csv", index=False)
print("\n📁 Saved updated CSV with fail_probability")
