import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="fittrackdb"
)

cursor = conn.cursor()

# 1. Daily calorie total
print("\n--- Daily Calorie Totals (User 1) ---")
cursor.execute("""
    SELECT Meals.MealID, MealName, MealDate, MealType, Calories
    FROM Meals
    JOIN MealNutrition ON Meals.MealID = MealNutrition.MealID
    WHERE Meals.UserID = %s ORDER BY MealDate DESC
""", (user_id,))
for row in cursor.fetchall():
    print(f"Date: {row[0]} | Calories: {row[1]}")

# 2. Workout history
print("\n--- Workout History (User 1) ---")
cursor.execute("""
    SELECT WorkoutDate, WorkoutType, ExerciseName, Sets, Reps, WeightLbs
    FROM Workouts
    JOIN Exercises ON Workouts.WorkoutID = Exercises.WorkoutID
    WHERE Workouts.UserID = 1
    ORDER BY WorkoutDate
""")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}x{row[4]} @ {row[5]}lbs")

# 3. Body weight trend
print("\n--- Weight Trend (User 1) ---")
cursor.execute("""
    SELECT MeasurementDate, WeightLbs
    FROM BodyMeasurements
    WHERE UserID = 1
    ORDER BY MeasurementDate
""")
for row in cursor.fetchall():
    print(f"Date: {row[0]} | Weight: {row[1]} lbs")

# 4. Sleep log
print("\n--- Sleep Log (User 1) ---")
cursor.execute("""
    SELECT LogDate, SleepHours, EnergyLevel
    FROM RecoveryLogs
    WHERE UserID = 1
    ORDER BY LogDate
""")
for row in cursor.fetchall():
    print(f"Date: {row[0]} | Sleep: {row[1]}hrs | Energy: {row[2]}/10")

cursor.close()
conn.close()
print("\nDone.")