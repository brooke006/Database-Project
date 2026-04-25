import mysql.connector

# Change these if your MySQL password/database name is different
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="fittrackdb"
)

cursor = conn.cursor()

# This is the user we are testing in the report.
# If your test user is not UserID 1, change this number.
user_id = 1

# 1. Daily calorie totals
print("\n--- Daily Calorie Totals (User 1) ---")
cursor.execute("""
    SELECT Meals.MealDate, SUM(MealNutrition.Calories) AS TotalCalories
    FROM Meals
    JOIN MealNutrition ON Meals.MealID = MealNutrition.MealID
    WHERE Meals.UserID = %s
    GROUP BY Meals.MealDate
    ORDER BY Meals.MealDate DESC
""", (user_id,))

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"Date: {row[0]} | Calories: {row[1]}")
else:
    print("No meal data found for this user.")

# 2. Workout history
print("\n--- Workout History (User 1) ---")
cursor.execute("""
    SELECT Workouts.WorkoutDate, Workouts.WorkoutType, Exercises.ExerciseName,
           Exercises.Sets, Exercises.Reps, Exercises.WeightLbs
    FROM Workouts
    JOIN Exercises ON Workouts.WorkoutID = Exercises.WorkoutID
    WHERE Workouts.UserID = %s
    ORDER BY Workouts.WorkoutDate DESC
""", (user_id,))

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}x{row[4]} @ {row[5]} lbs")
else:
    print("No workout exercise data found for this user.")

# 3. Body weight trend
print("\n--- Weight Trend (User 1) ---")
cursor.execute("""
    SELECT MeasurementDate, WeightLbs
    FROM BodyMeasurements
    WHERE UserID = %s
    ORDER BY MeasurementDate DESC
""", (user_id,))

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"Date: {row[0]} | Weight: {row[1]} lbs")
else:
    print("No weight data found for this user.")

# 4. Sleep log
print("\n--- Sleep Log (User 1) ---")
cursor.execute("""
    SELECT LogDate, SleepHours, EnergyLevel
    FROM RecoveryLogs
    WHERE UserID = %s
    ORDER BY LogDate DESC
""", (user_id,))

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"Date: {row[0]} | Sleep: {row[1]} hrs | Energy: {row[2]}/10")
else:
    print("No sleep data found for this user.")

cursor.close()
conn.close()

print("\nDone.")