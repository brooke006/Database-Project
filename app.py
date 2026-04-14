from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "fittrackdb_secret"

def get_db():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="password",
        database="fittrackdb"
    )

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT UserID, FirstName FROM Users WHERE Email = %s AND Password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid email or password."
    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        first = request.form["first_name"]
        last = request.form["last_name"]
        email = request.form["email"]
        dob = request.form["dob"]
        password = request.form["password"]
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Users (FirstName, LastName, Email, DateOfBirth, Password)
                VALUES (%s, %s, %s, %s, %s)
            """, (first, last, email, dob, password))
            db.commit()
            user_id = cursor.lastrowid
            session["user_id"] = user_id
            session["user_name"] = first
            cursor.close()
            db.close()
            return redirect(url_for("dashboard"))
        except Exception as e:
            error = "Email already exists. Try logging in."
        cursor.close()
        db.close()
    return render_template("signup.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT Meals.MealID, Meals.MealName, Meals.MealDate, Meals.MealType, MealNutrition.Calories
        FROM Meals
        JOIN MealNutrition ON Meals.MealID = MealNutrition.MealID
        WHERE Meals.UserID = %s ORDER BY Meals.MealDate DESC
    """, (user_id,))
    meals = cursor.fetchall()

    cursor.execute("""
        SELECT WorkoutID, WorkoutDate, WorkoutType, DurationMin
        FROM Workouts WHERE UserID = %s ORDER BY WorkoutDate DESC
    """, (user_id,))
    workouts = cursor.fetchall()

    cursor.execute("""
        SELECT MeasurementID, MeasurementDate, WeightLbs FROM BodyMeasurements
        WHERE UserID = %s ORDER BY MeasurementDate DESC
    """, (user_id,))
    weights = cursor.fetchall()

    cursor.execute("""
        SELECT LogDate, SleepHours, EnergyLevel FROM RecoveryLogs
        WHERE UserID = %s ORDER BY LogDate DESC
    """, (user_id,))
    sleep = cursor.fetchall()

    cursor.execute("""
        SELECT LogDate, OuncesConsumed FROM WaterLogs
        WHERE UserID = %s ORDER BY LogDate DESC
    """, (user_id,))
    water = cursor.fetchall()

    cursor.execute("""
        SELECT GoalID, GoalType, TargetValue, CurrentValue, TargetDate
        FROM Goals WHERE UserID = %s ORDER BY StartDate DESC
    """, (user_id,))
    goals = cursor.fetchall()

    cursor.close()
    db.close()
    return render_template("dashboard.html", meals=meals, workouts=workouts,
                           weights=weights, sleep=sleep, water=water, goals=goals)

@app.route("/add_meal", methods=["GET", "POST"])
def add_meal():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Meals (UserID, MealName, MealDate, MealType)
            VALUES (%s, %s, %s, %s)
        """, (session["user_id"], request.form["meal_name"],
              request.form["meal_date"], request.form["meal_type"]))
        meal_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO MealNutrition (MealID, Calories, ProteinG, CarbsG, FatG)
            VALUES (%s, %s, %s, %s, %s)
        """, (meal_id, request.form["calories"], request.form["protein"],
              request.form["carbs"], request.form["fat"]))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("dashboard"))
    return render_template("add_meal.html")

@app.route("/delete_meal/<int:meal_id>")
def delete_meal(meal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Meals WHERE MealID = %s AND UserID = %s",
                   (meal_id, session["user_id"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/add_workout", methods=["GET", "POST"])
def add_workout():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Workouts (UserID, WorkoutDate, WorkoutType, DurationMin, Notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (session["user_id"], request.form["workout_date"],
              request.form["workout_type"], request.form["duration"],
              request.form["notes"]))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("dashboard"))
    return render_template("add_workout.html")

@app.route("/delete_workout/<int:workout_id>")
def delete_workout(workout_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Workouts WHERE WorkoutID = %s AND UserID = %s",
                   (workout_id, session["user_id"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/add_weight", methods=["GET", "POST"])
def add_weight():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO BodyMeasurements (UserID, MeasurementDate, WeightLbs, Notes)
            VALUES (%s, %s, %s, %s)
        """, (session["user_id"], request.form["measurement_date"],
              request.form["weight"], request.form["notes"]))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("dashboard"))
    return render_template("add_weight.html")

@app.route("/delete_weight/<int:measurement_id>")
def delete_weight(measurement_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM BodyMeasurements WHERE MeasurementID = %s AND UserID = %s",
                   (measurement_id, session["user_id"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/add_sleep", methods=["GET", "POST"])
def add_sleep():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO RecoveryLogs (UserID, LogDate, SleepHours, EnergyLevel, Notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (session["user_id"], request.form["log_date"],
              request.form["sleep_hours"], request.form["energy_level"],
              request.form["notes"]))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("dashboard"))
    return render_template("add_sleep.html")

@app.route("/add_water", methods=["GET", "POST"])
def add_water():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO WaterLogs (UserID, LogDate, OuncesConsumed)
            VALUES (%s, %s, %s)
        """, (session["user_id"], request.form["log_date"],
              request.form["ounces"]))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("dashboard"))
    return render_template("add_water.html")

@app.route("/add_goal", methods=["GET", "POST"])
def add_goal():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Goals (UserID, GoalType, TargetValue, CurrentValue, StartDate, TargetDate, Notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session["user_id"], request.form["goal_type"],
              request.form["target_value"], request.form["current_value"],
              request.form["start_date"], request.form["target_date"],
              request.form["notes"]))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("dashboard"))
    return render_template("add_goal.html")

@app.route("/delete_goal/<int:goal_id>")
def delete_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Goals WHERE GoalID = %s AND UserID = %s",
                   (goal_id, session["user_id"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cursor = db.cursor()
    if request.method == "POST":
        cursor.execute("""
            UPDATE Users SET FirstName=%s, LastName=%s, Email=%s, DateOfBirth=%s
            WHERE UserID=%s
        """, (request.form["first_name"], request.form["last_name"],
              request.form["email"], request.form["dob"], session["user_id"]))
        if request.form["password"]:
            cursor.execute("UPDATE Users SET Password=%s WHERE UserID=%s",
                           (request.form["password"], session["user_id"]))
        db.commit()
        session["user_name"] = request.form["first_name"]
        cursor.close()
        db.close()
        return redirect(url_for("profile"))
    cursor.execute("SELECT FirstName, LastName, Email, DateOfBirth FROM Users WHERE UserID=%s",
                   (session["user_id"],))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template("profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')