-- جدول المستخدمين
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(80),
  last_name VARCHAR(80),
  email VARCHAR(150) UNIQUE NOT NULL,
  phone VARCHAR(20),
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  diet_history TEXT,
  usage_dates TEXT,
  consultation_history TEXT,
  challenges_completed INT DEFAULT 0,
  consultations INT DEFAULT 0,
  telegram_chat_id VARCHAR(100)
);

select * from users; 

-- جدول السجلات الصحية
CREATE TABLE IF NOT EXISTS health_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  weight FLOAT,
  height FLOAT,
  blood_pressure VARCHAR(20),
  record_date DATE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- جدول الوجبات
CREATE TABLE IF NOT EXISTS meals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(100),
  calories FLOAT,
  meal_date DATE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- جدول الأنشطة الرياضية
CREATE TABLE IF NOT EXISTS activities (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  activity_type VARCHAR(100),
  duration_minutes INT,
  activity_date DATE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- جدول المواعيد
CREATE TABLE IF NOT EXISTS appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  doctor_name VARCHAR(150),
  appointment_date DATE,
  notes TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- medications جدول الادويه
CREATE TABLE IF NOT EXISTS medications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  medication_name VARCHAR(100),
  dosage VARCHAR(50),
  times_per_day INT DEFAULT 1,
  start_date DATE,
  end_date DATE,
  notes TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- جدول مواعيد التذكير 
CREATE TABLE IF NOT EXISTS medication_reminders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  medication_id INT NOT NULL,
  reminder_time TIME NOT NULL,  -- وقت التذكير
  FOREIGN KEY (medication_id) REFERENCES medications(id) ON DELETE CASCADE
);
INSERT INTO medications 
(user_id, medication_name, dosage, times_per_day, start_date, end_date, notes)
VALUES 
(1, 'Vitamin D', '1 capsule', 2, '2025-11-12', '2025-12-12', 'After meals');
INSERT INTO medication_reminders (medication_id, reminder_time)
VALUES 
(1, '08:00:00'),  -- التذكير الأول
(1, '20:00:00');  -- التذكير الثاني

SELECT * FROM medications;

SELECT id, medication_name FROM medications;



