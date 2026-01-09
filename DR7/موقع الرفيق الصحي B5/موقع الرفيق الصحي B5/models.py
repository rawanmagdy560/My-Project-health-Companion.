import os 
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db 
from sqlalchemy import text 

# ======= تعريف الجداول الموجودة في قاعدة البيانات health_companion =======

 #====== جدول المستخدمين
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# الأعمدة الجديدة التي يجب إضافتها:
    diet_history = db.Column(db.Text)               # لتخزين سجلات الحمية (كـ نص JSON)
    usage_dates = db.Column(db.Text)                # لتخزين تواريخ الاستخدام (كـ نص JSON)
    consultation_history = db.Column(db.Text)       # لتخزين تواريخ الاستشارات (كـ نص JSON)
    challenges_completed = db.Column(db.Integer, default=0) # عداد التحديات المكتملة
    consultations = db.Column(db.Integer, default=0) # عداد الاستشارات المنفذة
    telegram_chat_id = db.Column(db.String(100))    # معرف تيليجرام للتنبيهات
    # دالة التهيئة (للتأكد من تسجيل created_at عند إنشاء مستخدم جديد)
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    # العلاقات
    health_records = db.relationship('HealthRecord', backref='user', lazy=True)
    meals = db.relationship('Meal', backref='user', lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    medications = db.relationship('Medication', backref='user', lazy=True)
    def __repr__(self):
        return f"<User {self.email}>"
#====== جدول سجلات الصحة
class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    record_date = db.Column(db.Date)

#====== جدول الوجبات
class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    calories = db.Column(db.Float)
    meal_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#====== جدول الأنشطة
class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(100))
    duration_minutes = db.Column(db.Integer)
    activity_date = db.Column(db.Date)
 
#====== جدول  السجل الرياضي
class SportsData(db.Model):
    __tablename__ = "sports_data"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sport_type = db.Column(db.String(100), nullable=False)
    videos = db.Column(db.Text, nullable=True)  # نحفظ JSON كنص
    timestamp = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<SportsData {self.sport_type}>"
    
class ConsultationData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    timestamp = db.Column(db.String(120))

#====== جدول المواعيد
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_name = db.Column(db.String(150))
    appointment_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#====== جدول الأدوية
class Medication(db.Model):
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    medication_name = db.Column(db.String(100))
    dosage = db.Column(db.String(50))
    times_per_day = db.Column(db.Integer, default=1)

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # الأعمدة المطلوبة لتجنب الأخطاء
    time1 = db.Column(db.String(5), nullable=False)   # مثال: "08:00"
    time2 = db.Column(db.String(5))                   # اختياري

    ai_insight = db.Column(db.Text)                   # تحليل الذكاء الاصطناعي
    telegram_chat_id = db.Column(db.String(100))      # معرف تيليجرام

    # العلاقة مع جدول التذكيرات
    reminders = db.relationship(
        'MedicationReminder',
        backref='medication',
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Medication {self.medication_name}>"


#====== جدول تذكيرات الأدوية
class MedicationReminder(db.Model):
    __tablename__ = 'medication_reminders'

    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    reminder_time = db.Column(db.Time, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Reminder {self.reminder_time}>"
