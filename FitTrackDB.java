import java.sql.*;
import java.util.Scanner;

public class FitTrackDB {

    static final String HOST = "jdbc:mysql://localhost:3306/fittrackdb";
    static final String USER = "root";
    static final String PASS = "password";

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== FitTrackDB Login ===");
        System.out.print("Enter your email: ");
        String email = scanner.nextLine();

        try {
            Connection conn = DriverManager.getConnection(HOST, USER, PASS);

            // Check if user exists
            PreparedStatement loginStmt = conn.prepareStatement(
                "SELECT UserID, FirstName FROM Users WHERE Email = ?"
            );
            loginStmt.setString(1, email);
            ResultSet rs = loginStmt.executeQuery();

            if (!rs.next()) {
                System.out.println("No account found with that email.");
                conn.close();
                return;
            }

            int userID = rs.getInt("UserID");
            String name = rs.getString("FirstName");
            System.out.println("\nWelcome, " + name + "!");

            // Show menu
            boolean running = true;
            while (running) {
                System.out.println("\nWhat would you like to view?");
                System.out.println("1. Daily Calorie Totals");
                System.out.println("2. Workout History");
                System.out.println("3. Weight Trend");
                System.out.println("4. Sleep Log");
                System.out.println("5. Exit");
                System.out.print("Choose (1-5): ");
                String choice = scanner.nextLine();

                switch (choice) {
                    case "1":
                        System.out.println("\n--- Daily Calorie Totals ---");
                        PreparedStatement cal = conn.prepareStatement(
                            "SELECT MealDate, SUM(Calories) AS Total FROM Meals " +
                            "JOIN MealNutrition ON Meals.MealID = MealNutrition.MealID " +
                            "WHERE Meals.UserID = ? GROUP BY MealDate"
                        );
                        cal.setInt(1, userID);
                        ResultSet calRs = cal.executeQuery();
                        while (calRs.next()) {
                            System.out.println("Date: " + calRs.getString("MealDate") +
                                " | Calories: " + calRs.getInt("Total"));
                        }
                        break;

                    case "2":
                        System.out.println("\n--- Workout History ---");
                        PreparedStatement wo = conn.prepareStatement(
                            "SELECT WorkoutDate, WorkoutType, ExerciseName, Sets, Reps, WeightLbs " +
                            "FROM Workouts JOIN Exercises ON Workouts.WorkoutID = Exercises.WorkoutID " +
                            "WHERE Workouts.UserID = ? ORDER BY WorkoutDate"
                        );
                        wo.setInt(1, userID);
                        ResultSet woRs = wo.executeQuery();
                        while (woRs.next()) {
                            System.out.println(woRs.getString("WorkoutDate") + " | " +
                                woRs.getString("WorkoutType") + " | " +
                                woRs.getString("ExerciseName") + " | " +
                                woRs.getInt("Sets") + "x" + woRs.getInt("Reps") +
                                " @ " + woRs.getDouble("WeightLbs") + "lbs");
                        }
                        break;

                    case "3":
                        System.out.println("\n--- Weight Trend ---");
                        PreparedStatement wt = conn.prepareStatement(
                            "SELECT MeasurementDate, WeightLbs FROM BodyMeasurements " +
                            "WHERE UserID = ? ORDER BY MeasurementDate"
                        );
                        wt.setInt(1, userID);
                        ResultSet wtRs = wt.executeQuery();
                        while (wtRs.next()) {
                            System.out.println("Date: " + wtRs.getString("MeasurementDate") +
                                " | Weight: " + wtRs.getDouble("WeightLbs") + " lbs");
                        }
                        break;

                    case "4":
                        System.out.println("\n--- Sleep Log ---");
                        PreparedStatement sl = conn.prepareStatement(
                            "SELECT LogDate, SleepHours, EnergyLevel FROM RecoveryLogs " +
                            "WHERE UserID = ? ORDER BY LogDate"
                        );
                        sl.setInt(1, userID);
                        ResultSet slRs = sl.executeQuery();
                        while (slRs.next()) {
                            System.out.println("Date: " + slRs.getString("LogDate") +
                                " | Sleep: " + slRs.getDouble("SleepHours") + "hrs" +
                                " | Energy: " + slRs.getInt("EnergyLevel") + "/10");
                        }
                        break;

                    case "5":
                        running = false;
                        System.out.println("Goodbye, " + name + "!");
                        break;

                    default:
                        System.out.println("Invalid choice, try again.");
                }
            }
            conn.close();

        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
        scanner.close();
    }
}