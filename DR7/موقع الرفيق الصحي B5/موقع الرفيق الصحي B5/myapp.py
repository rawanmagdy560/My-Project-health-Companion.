import os
import re
import math
import json
import requests
import threading
from datetime import datetime, date, timedelta
from functools import wraps
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from config import Config
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import User, HealthRecord, Meal, Activity, Appointment, Medication, MedicationReminder, ConsultationData, SportsData
from extensions import db, migrate

# 2️⃣ إنشاء تطبيق Flask
myapp = Flask(__name__)

# 4️⃣ تكوين قاعدة البيانات
myapp.config.from_object(Config)

# 3️⃣ ربط db و migrate بالـ app
db.init_app(myapp)
migrate.init_app(myapp, db)

# إنشاء الجداول في قاعدة البيانات إذا لم تكن موجودة
with myapp.app_context():
    db.create_all()
    
DESIGNERS_DIR = os.path.join(myapp.root_path, 'مصممين الموقع')  # تحديد مسار مجلد صور المصممين
DESIGNER_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')  # تحديد الامتدادات المسموح بها لصور المصممين

 # قاموس لتخزين مؤقتات المكالمات 
scheduled_call_timers = {} 
scheduled_telegram_timers = {}
@myapp.route('/assets/health-background')  # مسار لجلب صورة خلفية الصحة

def health_background():
    """إرجاع صورة الخلفية الصحية من مجلد التطبيق."""
    return send_from_directory(myapp.root_path, 'الصحه .jpg')  # إرسال الصورة المطلوبة للمتصفح


@myapp.route('/assets/designers/<path:filename>')  # مسار لعرض ملفات المصممين

def designer_asset(filename):
    """تقديم ملف المصمم حسب الاسم المطلوب."""
    return send_from_directory(DESIGNERS_DIR, filename)  # إعادة الملف المطلوب من مجلد المصممين

AI_API_URL = os.getenv('HEALTH_AI_API_URL', 'https://api.openai.com/v1/chat/completions')  # عنوان خدمة الذكاء الاصطناعي للمحادثات
AI_API_KEY = os.getenv('HEALTH_AI_API_KEY', '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')  # مفتاح الوصول لواجهة الذكاء الاصطناعي
AI_MODEL = os.getenv('HEALTH_AI_MODEL', 'gpt-4o-mini')  # اسم النموذج المستخدم للردود
SPORTS_VIDEO_SEARCH_URL = os.getenv('SPORTS_VIDEO_SEARCH_URL', 'https://piped.video/api/v1/search')  # رابط البحث عن فيديوهات الرياضة
try:
    SPORTS_VIDEO_MAX_RESULTS = int(os.getenv('SPORTS_VIDEO_MAX_RESULTS', '6'))  # قراءة الحد الأقصى لعدد الفيديوهات
except ValueError:
    SPORTS_VIDEO_MAX_RESULTS = 6  # الرجوع للقيمة الافتراضية عند حدوث خطأ
SPORTS_VIDEO_REGION = os.getenv('SPORTS_VIDEO_REGION', 'SA')  # تحديد المنطقة الجغرافية لنتائج الفيديو
SPORTS_VIDEO_LANGUAGE = os.getenv('SPORTS_VIDEO_LANGUAGE', 'ar')  # تحديد لغة نتائج الفيديو

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC3a9c61080e6f28d62ed2ade6e7fa7d20')  # معرف حساب تويلو
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '93360e62a6bfb139654fc370f063e5cb')  # رمز تفويض تويلو
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')  # رقم الهاتف المرسل من تويلو
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8360121391:AAFvJsN2SheNYVcVlyfF H8-zpVphoDSS-XY')  # رمز روبوت تيليجرام


SPORT_ALIAS_MAP = {  # خريطة تحويل أسماء الرياضات إلى صيغة موحدة للبحث
    'كرة القدم': 'soccer',
    'الكرة القدم': 'soccer',
    'football': 'soccer',
    'soccer': 'soccer',
    'يوغا': 'yoga',
    'اليوغا': 'yoga',
    'yoga': 'yoga',
    'السباحة': 'swimming',
    'سباحة': 'swimming',
    'swimming': 'swimming',
    'كرة السلة': 'basketball',
    'سلة': 'basketball',
    'basketball': 'basketball',
    'running': 'running',
    'الجري': 'running',
    'ركض': 'running',
    'boxing': 'boxing',
    'الملاكمة': 'boxing',
    'قوة': 'strength',
    'تمارين القوة': 'strength',
    'strength': 'strength'
}

SPORT_FALLBACK_QUERIES = {  # عبارات بديلة للبحث عن فيديوهات لكل رياضة
    'soccer': ['تمارين كرة القدم للمبتدئين بالعربي', 'تدريبات مهارات كرة القدم بالعربي'],
    'basketball': ['تمارين كرة السلة بالعربي', 'تدريبات كرة السلة للمبتدئين بالعربي'],
    'swimming': ['تمارين السباحة خارج الماء بالعربي', 'تقوية السباحة الحرة بالعربي'],
    'running': ['تمارين الجري بالعربي', 'تقوية العدائين بالعربي'],
    'boxing': ['تدريبات الملاكمة بالعربي', 'أساسيات الملاكمة بالعربي'],
    'strength': ['تمارين القوة المنزلية بالعربي', 'تمارين وزن الجسم بالعربي'],
    'yoga': ['يوغا صباحية بالعربي', 'يوغا للاسترخاء بالعربي']
}

ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')  # نمط للتأكد من وجود حروف عربية في النص

def list_designer_profiles():
    try:
        entries = []  # قائمة لتجميع بيانات المصممين
        for name in os.listdir(DESIGNERS_DIR):  # المرور على ملفات المصممين في المجلد
            lower = name.lower()  # تحويل الاسم إلى أحرف صغيرة للتعامل الموحد
            if not lower.endswith(DESIGNER_IMAGE_EXTENSIONS):  # تجاهل الملفات غير المدعومة
                continue
            base = os.path.splitext(name)[0]  # استخراج اسم الملف بدون الامتداد
            cleaned = re.sub(r'[\s_\-]+', ' ', base).strip()  # تنظيف الاسم من الفراغات والرموز
            if re.fullmatch(r'[A-Za-z ]+', cleaned):  # التحقق إن كان الاسم بالحروف اللاتينية
                label = cleaned.title()  # تنسيق الاسم بشكل جميل
            else:
                label = cleaned  # استخدام الاسم كما هو للغة العربية
            entries.append({'filename': name, 'label': label, 'is_featured': 'mohamed asem' in lower})  # إضافة البيانات للقائمة
        entries.sort(key=lambda item: (not item['is_featured'], item['label'].lower()))  # ترتيب القائمة مع إبراز المصمم المميز
        return entries  # إعادة قائمة المصممين المعالجة
    except FileNotFoundError:
        return []  # إعادة قائمة فارغة عند عدم وجود المجلد

def get_twilio_client():
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):  # التأكد من توفر بيانات تويلو الأساسية
        return None  # إرجاع لا شيء عند نقص البيانات
    try:
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)  # إنشاء عميل تويلو للتعامل مع الرسائل
    except Exception:
        return None  # التعامل مع أي خطأ وإرجاع لا شيء


def login_required(view):
    @wraps(view)  # الحفاظ على خصائص الدالة الأصلية
    def wrapped(*args, **kwargs):
        email = session.get('user_email')  # قراءة البريد من الجلسة

        if not email:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('login'))

        # البحث عن المستخدم داخل قاعدة البيانات
        user = User.query.filter_by(email=email).first()

        if not user:
            session.pop('user_email', None)
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('login'))

        return view(*args, **kwargs)

    return wrapped

def normalize_email(value):
    return value.strip().lower()  # تنظيف البريد الإلكتروني وتحويله لأحرف صغيرة


def get_current_user():
    email = session.get('user_email')
    if not email:
        return None
    return User.query.filter_by(email=email).first()

def ensure_user_defaults(user):

    if user.diet_history is None:
        user.diet_history = '[]'

    if user.usage_dates is None:
        user.usage_dates = '[]'

    if user.consultation_history is None:
        user.consultation_history = '[]'

    if user.challenges_completed is None:
        user.challenges_completed = 0

    if user.consultations is None:
        user.consultations = 0

    db.session.commit()
    return user


def haversine_distance(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):  # التأكد من توفر كل الإحداثيات
        return None  # إرجاع لا شيء عند نقص البيانات
    phi1 = math.radians(lat1)  # تحويل خط العرض الأول إلى راديان
    phi2 = math.radians(lat2)  # تحويل خط العرض الثاني إلى راديان
    d_phi = math.radians(lat2 - lat1)  # حساب الفرق في خطوط العرض
    d_lambda = math.radians(lng2 - lng1)  # حساب الفرق في خطوط الطول
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2  # معادلة هافرسين
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))  # حساب الزاوية المركزية
    return 6371000 * c  # تحويل المسافة إلى أمتار باستخدام نصف قطر الأرض


def create_diet_plan(form_data):
    age = int(form_data['age'])  # تحويل العمر إلى عدد صحيح
    height_cm = float(form_data['height'])  # تحويل الطول إلى رقم عشري
    weight_kg = float(form_data['weight'])  # تحويل الوزن إلى رقم عشري
    gender = form_data['gender']  # قراءة جنس المستخدم
    activity = form_data['activity']  # مستوى النشاط البدني
    goal = form_data['goal']  # الهدف الغذائي للمستخدم
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if gender == 'male' else -161)  # معادلة معدل الحرق الأساسي
    activity_factor = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725
    }.get(activity, 1.2)  # تحديد معامل النشاط المناسب
    goal_adjustment = {
        'maintain': 0,
        'lose': -300,
        'gain': 300
    }.get(goal, 0)  # تعديل السعرات حسب الهدف
    maintenance = bmr * activity_factor  # حساب سعرات المحافظة على الوزن
    total_calories = max(1200, round(maintenance + goal_adjustment))  # ضمان حد أدنى للسعرات اليومية
    meals = [
        {
            'title': 'الفطور',
            'calories': int(total_calories * 0.3),
            'items': ['شوفان مع حليب منخفض الدسم', 'بيض مسلوق', 'ثمرة فاكهة']
        },
        {
            'title': 'الغداء',
            'calories': int(total_calories * 0.4),
            'items': ['بروتين خفيف مثل دجاج أو سمك', 'حبوب كاملة أو أرز بني', 'سلطة خضراء']
        },
        {
            'title': 'العشاء',
            'calories': int(total_calories * 0.25),
            'items': ['بروتين نباتي أو حيواني خفيف', 'خضروات مطهوة بالبخار', 'مصدر صحي للكربوهيدرات']
        }
    ]  # تقسيم السعرات على ثلاث وجبات رئيسية
    snacks_calories = total_calories - sum(meal['calories'] for meal in meals)  # حساب المتبقي للوجبات الخفيفة
    if snacks_calories > 0:
        meals.append({
            'title': 'وجبات خفيفة',
            'calories': snacks_calories,
            'items': ['مكسرات غير مملحة', 'زبادي يوناني', 'شرائح خضار طازجة']
        })  # إضافة وجبات خفيفة عند توفر سعرات
    hydration_ml = int(weight_kg * 35)  # حساب كمية الماء اليومية المقترحة
    return {
        'total_calories': total_calories,
        'bmr': int(bmr),
        'hydration_ml': hydration_ml,
        'meals': meals,
        'allergies': form_data.get('allergies', '').strip()
    }  # إعادة تفاصيل الخطة الغذائية


def generate_ai_reply(message):
    if not AI_API_KEY:  # التحقق من توفر مفتاح الذكاء الاصطناعي
        return 'الرجاء إعداد مفتاح واجهة برمجة التطبيقات في HEALTH_AI_API_KEY.'  # رسالة تنبيه عند غياب المفتاح
    try:
        response = requests.post(
            AI_API_URL,  # عنوان واجهة الذكاء الاصطناعي المستهدفة
            headers={
                'Authorization': f'Bearer {AI_API_KEY}',  # تمرير المفتاح في ترويسة الطلب
                'Content-Type': 'application/json'  # تحديد نوع البيانات المرسلة
            },
            json={
                'model': AI_MODEL,  # تحديد النموذج المطلوب استخدامه
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an Arabic-speaking virtual health assistant. Provide balanced, evidence-informed guidance, remind users that your advice does not replace a real doctor, and encourage professional consultation for emergencies.'
                    },  # تهيئة رسالة النظام لتحديد دور المساعد
                    {'role': 'user', 'content': message}  # تضمين رسالة المستخدم بالطلب
                ],
                'temperature': 0.2,  # ضبط العشوائية في الردود
                'max_tokens': 400  # تحديد الحد الأقصى لطول الرد
            },
            timeout=30  # تعيين مهلة للطلب بثواني
        )
        response.raise_for_status()  # إثارة خطأ عند فشل الطلب
        data = response.json()  # تحويل الرد إلى بيانات JSON
        reply = data.get('choices', [{}])[0].get('message', {}).get('content')  # استخراج الرد النصي
        if reply:
            return reply.strip()  # إعادة الرد بعد إزالة الفراغات
        return 'تعذر توليد رد من المساعد الطبي، يرجى المحاولة مرة أخرى.'  # رسالة عند عدم وجود محتوى
    except requests.exceptions.RequestException:
        return 'تعذر الاتصال بخدمة الذكاء الاصطناعي، حاول مرة أخرى لاحقاً.'  # معالجة أخطاء الاتصال


def normalize_sport_query(value):
    if not value:  # التحقق من وجود قيمة للرياضة
        return ''  # إعادة نص فارغ عند غياب الإدخال
    return SPORT_ALIAS_MAP.get(value.strip().lower(), value.strip().lower())  # إرجاع الاسم الموحد أو المدخل المنظف


def extract_video_id_from_url(url):
    if not url:  # التأكد من وجود رابط لتحليله
        return None  # إرجاع لا شيء عند عدم توفر الرابط
    parsed = urlparse(url)  # تحليل الرابط إلى مكوناته
    if parsed.query:  # التحقق من وجود معلمات في الرابط
        params = parse_qs(parsed.query)  # تحويل المعلمات إلى قاموس
        if 'v' in params and params['v']:  # البحث عن معرف الفيديو من المعلمة v
            return params['v'][0]  # إعادة معرف الفيديو إن وجد
    if parsed.path.startswith('/watch/'):  # التحقق من صيغة رابط المشاهدة القصير
        return parsed.path.split('/')[-1]  # استخراج معرف الفيديو من المسار
    if parsed.netloc in {'youtu.be', 'www.youtu.be'}:  # التعامل مع روابط يوتيوب القصيرة
        return parsed.path.lstrip('/') or None  # إعادة المعرف أو لا شيء عند عدم وجوده
    return None  # إعادة لا شيء إذا لم يتم العثور على معرف


def build_search_link(query):
    return f'https://www.youtube.com/results?search_query={quote_plus(query)}'  # بناء رابط بحث في يوتيوب مع ترميز النص


def search_videos(query, limit, seen_urls):
    params = {
        'q': query,
        'region': SPORTS_VIDEO_REGION,
        'language': SPORTS_VIDEO_LANGUAGE
    }  # المعلمات المرسلة لواجهة البحث عن الفيديوهات
    try:
        response = requests.get(SPORTS_VIDEO_SEARCH_URL, params=params, timeout=12)  # إرسال طلب البحث مع مهلة
        response.raise_for_status()  # التأكد من نجاح الطلب
        data = response.json()  # تحويل الرد إلى JSON
    except requests.exceptions.RequestException:
        return []  # إعادة قائمة فارغة عند فشل الطلب
    items = []
    if isinstance(data, list):
        items = data  # التعامل مع الرد إذا كان قائمة مباشرة
    elif isinstance(data, dict):
        if isinstance(data.get('items'), list):
            items = data['items']  # استخراج العناصر من المفتاح items
        elif isinstance(data.get('data'), list):
            items = data['data']  # استخراج العناصر من المفتاح data
    videos = []
    for item in items:
        if len(videos) >= limit:  # التوقف عند الوصول للحد المطلوب
            break
        item_type = item.get('type')
        if item_type and item_type not in {'stream', 'video'}:  # تجاهل العناصر غير الفيديوهات
            continue
        title = (item.get('title') or '').strip()  # قراءة العنوان وتنظيفه
        description = (item.get('description') or item.get('shortDescription') or '').strip()  # قراءة الوصف
        combined_text = f"{title} {description}"  # دمج العنوان والوصف للتحقق من اللغة
        if not title or not ARABIC_PATTERN.search(combined_text):  # التأكد من وجود محتوى عربي
            continue
        source_url = item.get('url') or item.get('shortUrl') or item.get('videoUrl')  # الحصول على رابط الفيديو
        if not source_url:
            continue  # تجاهل العنصر عند عدم توفر رابط
        if not source_url.startswith('http'):
            source_url = urljoin('https://piped.video', source_url)  # إكمال الرابط النسبي
        video_id = extract_video_id_from_url(source_url)  # استخراج معرف الفيديو إن أمكن
        video_url = f'https://www.youtube.com/watch?v={video_id}' if video_id else source_url  # بناء رابط يوتيوب النهائي
        if video_url in seen_urls:  # منع تكرار الفيديوهات
            continue
        thumbnail = item.get('thumbnail') or item.get('thumbnailUrl')  # قراءة صورة المعاينة
        channel_title = item.get('uploaderName') or item.get('author', '')  # الحصول على اسم القناة
        videos.append({
            'title': title,
            'description': description,
            'video_id': video_id,
            'thumbnail': thumbnail,
            'channel_title': channel_title or 'يوتيوب',
            'video_url': video_url
        })  # تجميع بيانات الفيديو في القاموس
    return videos  # إعادة قائمة الفيديوهات المطابقة


def fetch_sport_videos(sport_type):
    if not sport_type:  # التأكد من إدخال نوع الرياضة
        return [], 'الرجاء إدخال نوع الرياضة.'  # رسالة خطأ عند غياب النوع
    canonical = normalize_sport_query(sport_type)  # تحويل اسم الرياضة للصيغة الموحدة
    base_phrase = sport_type.strip()  # تنظيف النص من الفراغات
    query_variants = [
        f'{base_phrase} تمارين بالعربي',
        f'تمارين {base_phrase} للمبتدئين بالعربي',
        f'شرح {base_phrase} بالعربي'
    ]  # إنشاء عبارات بحث رئيسية
    if canonical and canonical != base_phrase.lower():
        query_variants.append(f'{canonical} training arabic')  # إضافة عبارة بحث إضافية عند اختلاف الاسم الموحد
    query_variants.extend(SPORT_FALLBACK_QUERIES.get(canonical, []))  # إضافة العبارات الاحتياطية لهذه الرياضة
    videos = []
    seen_urls = set()  # مجموعة لتجنب تكرار الروابط
    for query in query_variants:
        if len(videos) >= SPORTS_VIDEO_MAX_RESULTS:  # التوقف عند الوصول للحد الأقصى
            break
        needed = SPORTS_VIDEO_MAX_RESULTS - len(videos)  # عدد الفيديوهات المتبقية المطلوب جلبها
        results = search_videos(query, needed, seen_urls)  # البحث عن فيديوهات لكل عبارة
        for video in results:
            videos.append(video)  # إضافة الفيديو للقائمة النهائية
            seen_urls.add(video['video_url'])  # حفظ الرابط لتجنب التكرار
            if len(videos) >= SPORTS_VIDEO_MAX_RESULTS:
                break
    if not videos and canonical:  # تجربة البحث البديل عند عدم العثور على نتائج
        fallback_query = f'{canonical} تمارين بالعربي'
        results = search_videos(fallback_query, SPORTS_VIDEO_MAX_RESULTS, seen_urls)
        for video in results:
            videos.append(video)
            seen_urls.add(video['video_url'])
            if len(videos) >= SPORTS_VIDEO_MAX_RESULTS:
                break
    if not videos and canonical:
        english_query = f'{canonical} training arabic'  # استخدام عبارة إنجليزية لإيجاد نتائج إضافية
        results = search_videos(english_query, SPORTS_VIDEO_MAX_RESULTS, seen_urls)
        for video in results:
            videos.append(video)
            seen_urls.add(video['video_url'])
            if len(videos) >= SPORTS_VIDEO_MAX_RESULTS:
                break
    if videos:
        return videos, None  # إعادة الفيديوهات عند نجاح البحث
    fallback_queries = SPORT_FALLBACK_QUERIES.get(canonical, query_variants)  # استخدام عبارات البحث الاحتياطية
    fallback_videos = []
    for query in fallback_queries:
        fallback_videos.append({
            'title': query,
            'description': 'اضغط لعرض قائمة فيديوهات عربية حول هذا التمرين.',
            'video_id': None,
            'thumbnail': None,
            'channel_title': 'يوتيوب',
            'video_url': build_search_link(query)
        })  # إنشاء روابط بحث للمستخدم عند عدم توفر فيديوهات مباشرة
    if fallback_videos:
        return fallback_videos, None  # إعادة النتائج البديلة
    return [], 'لم يتم العثور على تمارين مطابقة للرياضة المطلوبة.'  # رسالة عند عدم إيجاد أي نتائج


def send_sms_notification(phone, body):
    client = get_twilio_client()  # الحصول على عميل تويلو لإرسال الرسائل
    if not client or not TWILIO_FROM_NUMBER or not phone or not body:  # التحقق من توفر جميع البيانات المطلوبة
        return False  # إرجاع فشل عند نقص البيانات
    try:
        client.messages.create(to=phone, from_=TWILIO_FROM_NUMBER, body=body)  # إرسال رسالة نصية للمستخدم
        return True  # تأكيد نجاح الإرسال
    except Exception:
        return False  # التعامل مع أي خطأ أثناء الإرسال


def initiate_call_notification(phone, message):
    client = get_twilio_client()  # الحصول على عميل تويلو للمكالمات
    if not client or not TWILIO_FROM_NUMBER or not phone or not message:  # التحقق من البيانات الأساسية
        return False
    try:
        client.calls.create(to=phone, from_=TWILIO_FROM_NUMBER, twiml=f"<Response><Say language='ar-SA'>{message}</Say></Response>")  # إجراء مكالمة صوتية بالتذكير
        return True
    except Exception:
        return False  # فشل عند حدوث استثناء


def send_telegram_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN or not chat_id or not text:  # التأكد من توفر البيانات المطلوبة لإرسال الرسالة
        return False
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15
        )  # إرسال طلب إلى واجهة تيليجرام
        if response.status_code != 200:  # التحقق من نجاح الاستجابة
            return False
        data = response.json()  # تحويل الرد إلى JSON
        return data.get('ok') is True  # التأكد من قبول الرسالة
    except requests.exceptions.RequestException:
        return False  # التعامل مع أخطاء الشبكة


def schedule_call_notification(phone, medicine_name, time_str):
    if not time_str or not phone:  # التأكد من توفر بيانات الوقت ورقم الهاتف
        return
    try:
        target_time = datetime.strptime(time_str, '%H:%M').time()  # تحويل وقت التذكير إلى كائن وقت
    except ValueError:
        return  # تجاهل الوقت غير الصحيح
    now = datetime.now()  # وقت التنفيذ الحالي
    scheduled_datetime = datetime.combine(now.date(), target_time)  # إنشاء تاريخ التذكير من وقت اليوم الحالي
    if scheduled_datetime <= now:  # إذا كان الوقت قد مضى، يتم جدولة التذكير لليوم التالي
        scheduled_datetime += timedelta(days=1)
    delay = (scheduled_datetime - now).total_seconds()  # حساب عدد الثواني حتى الموعد
    message = f"هذا تذكير بموعد دوائك {medicine_name}. يرجى تناول الدواء الآن."

    def trigger_call():
        initiate_call_notification(phone, message)  # تنفيذ المكالمة عند الموعد
        schedule_call_notification(phone, medicine_name, time_str)  # إعادة جدولة التذكير لليوم التالي

    timer = threading.Timer(delay, trigger_call)  # إنشاء مؤقت لتنفيذ المكالمة
    timer.daemon = True  # جعل المؤقت يعمل في الخلفية دون منع إغلاق التطبيق
    timer.start()  # بدء المؤقت
    scheduled_call_timers.append(timer)  # حفظ المؤقت في القائمة لإدارته لاحقاً


def schedule_telegram_notification(chat_id, medicine_name, time_str):
    if not time_str or not chat_id:  # التحقق من توفر البيانات الأساسية
        return
    try:
        target_time = datetime.strptime(time_str, '%H:%M').time()  # تحويل الوقت إلى كائن وقت
    except ValueError:
        return
    now = datetime.now()
    scheduled_datetime = datetime.combine(now.date(), target_time)
    if scheduled_datetime <= now:
        scheduled_datetime += timedelta(days=1)
    delay = (scheduled_datetime - now).total_seconds()
    message = f"حان الآن موعد تناول دوائك {medicine_name}."

    def trigger_message():
        send_telegram_message(chat_id, message)  # إرسال رسالة تيليجرام عند الموعد
        schedule_telegram_notification(chat_id, medicine_name, time_str)  # إعادة جدولة التذكير لليوم التالي

    timer = threading.Timer(delay, trigger_message)  # إنشاء مؤقت للإرسال المتكرر
    timer.daemon = True
    timer.start()
    scheduled_telegram_timers.append(timer)  # حفظ المؤقت ضمن قائمة التنبيهات


def analyze_medicine_with_ai(name, dosage):
    if not name:  # التأكد من توفر اسم الدواء
        return 'لم يتم تقديم اسم الدواء لتحليله.'
    prompt = (
        "أنت صيدلي عربي محترف. قدم تلخيصاً موجزاً باللغة العربية عن هذا الدواء يشمل فئة العلاج، آلية العمل، أهم الاستخدامات، وأبرز التحذيرات. "
        f"اسم الدواء: {name}."
        f" الجرعة المقترحة: {dosage or 'غير محددة'}."
        " استخدم لغة مبسطة ومباشرة، واذكر أنه لا يغني عن استشارة الطبيب."
    )  # صياغة طلب للذكاء الاصطناعي لوصف الدواء
    analysis = generate_ai_reply(prompt)  # الحصول على الاستجابة من الذكاء الاصطناعي
    if analysis.startswith('تعذر') or analysis.startswith('الرجاء إعداد'):
        return 'تعذر الحصول على تحليل من الذكاء الاصطناعي حالياً.'  # رسالة عند فشل التحليل
    return analysis  # إعادة التلخيص للمستخدم


def calculate_next_reminder(reminder_times):
    parsed_times = []  # قائمة لحفظ الأوقات الصالحة
    for time_str in reminder_times:
        try:
            parsed_times.append(datetime.strptime(time_str, '%H:%M').time())  # تحويل النص إلى وقت
        except ValueError:
            continue  # تجاهل الأوقات غير الصالحة
    if not parsed_times:
        return None, None  # إعادة لا شيء عند عدم وجود أوقات صحيحة
    now = datetime.now()  # وقت التنفيذ الحالي
    candidates = []
    for time_obj in parsed_times:
        candidate = datetime.combine(now.date(), time_obj)  # إنشاء موعد لليوم الحالي
        if candidate <= now:  # إذا كان الموعد قد مر، يتم نقله لليوم التالي
            candidate += timedelta(days=1)
        candidates.append(candidate)
    next_datetime = min(candidates)  # أقرب موعد قادم
    return next_datetime, next_datetime - now  # إعادة الموعد والمدة المتبقية


def format_remaining_time(delta):
    if delta is None:  # التأكد من وجود مدة زمنية لحسابها
        return None
    total_seconds = int(delta.total_seconds())  # تحويل المدة إلى ثواني كاملة
    if total_seconds < 60:  # حالة المدة القصيرة جداً
        return 'أقل من دقيقة'
    hours = total_seconds // 3600  # حساب الساعات المتبقية
    minutes = (total_seconds % 3600) // 60  # حساب الدقائق المتبقية بعد خصم الساعات
    parts = []
    if hours:
        parts.append(f"{hours} ساعة")  # إضافة الساعات للنص النهائي
    if minutes:
        parts.append(f"{minutes} دقيقة")  # إضافة الدقائق للنص النهائي
    if not parts:
        parts.append('أقل من دقيقة')  # fallback عند عدم وجود ساعات أو دقائق
    return ' و '.join(parts)  # دمج أجزاء الوقت بنص عربي واضح


def build_next_reminder_text(medicine_entry):
    # تم التعديل: استخدام الخصائص المباشرة (medicine_entry.time1) بدلاً من .get()
    reminder_times = [t for t in [medicine_entry.time1, medicine_entry.time2] if t] 
    next_datetime, delta = calculate_next_reminder(reminder_times)
    if not next_datetime or not delta:
        return 'لا يوجد موعد قادم'
    remaining = format_remaining_time(delta)
    return f"يتبقى {remaining} للموعد القادم عند الساعة {next_datetime.strftime('%H:%M')}"

@myapp.route('/', methods=['GET'])

def root():
    if 'user_email' in session:  # إذا كان المستخدم مسجلاً بالفعل، الانتقال للوحة التحكم
        return redirect(url_for('dashboard'))
    return render_template('intro.html', designers=list_designer_profiles())  # عرض الصفحة التعريفية مع المصممين


@myapp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = normalize_email(request.form.get('email', ''))
        password = request.form.get('password', '')

        # البحث في قاعدة البيانات
        user = User.query.filter_by(email=email).first()

        # التحقق من وجود المستخدم ومقارنة الباسورد المشفَّر
        if user and check_password_hash(user.password_hash, password):

            session['user_email'] = user.email  # حفظ المستخدم في الجلسة
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('dashboard'))

        flash('بيانات الدخول غير صحيحة، يرجى المحاولة مرة أخرى.', 'error')
        return redirect(url_for('login'))

    return render_template('index.html')


@myapp.route('/register', methods=['GET', 'POST'])

def register():
    if request.method == 'POST':  # معالجة بيانات التسجيل عند إرسال النموذج
        first_name = request.form.get('first_name', '').strip()  # قراءة الاسم الأول
        last_name = request.form.get('last_name', '').strip()  # قراءة الاسم الأخير
        email = normalize_email(request.form.get('email', ''))  # تنسيق البريد الإلكتروني
        phone = request.form.get('phone', '').strip()  # قراءة رقم الهاتف
        password = request.form.get('password', '')  # كلمة المرور
        confirm_password = request.form.get('confirm_password', '')  # تأكيد كلمة المرور
        # ✅ التحقق من إدخال جميع البيانات
        if not all([first_name, last_name, email, phone, password, confirm_password]):
            flash('الرجاء تعبئة جميع الحقول المطلوبة.', 'error')  # تنبيه عند نقص البيانات
            return redirect(url_for('register'))
        # ✅ التحقق من تطابق كلمتي المرور
        if password != confirm_password:  # التحقق من تطابق كلمات المرور
            flash('كلمتا المرور غير متطابقتين.', 'error')
            return redirect(url_for('register'))
        # ✅ التحقق من عدم وجود البريد في قاعدة البيانات
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('البريد الإلكتروني مسجل بالفعل.', 'error')
            return redirect(url_for('register'))

          # تشفير كلمة المرور ثم إضافة المستخدم
        hashed_password = generate_password_hash(password)
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('تم إنشاء الحساب بنجاح، يمكنك تسجيل الدخول الآن.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')  # عرض صفحة التسجيل عند الطلب GET


@myapp.route('/logout',  methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        email = normalize_email(request.form.get('email',''))
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
         # هنا تحفظ مثلاً session['user_id'] = user.id أو session['user_email'] = user.email
            session['user_email'] = user.email
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('dashboard'))
        flash('بيانات الدخول غير صحيحة.', 'error')
        return redirect(url_for('login'))
    return render_template('index.html')

@myapp.route('/dashboard')
@login_required
def dashboard():

    user = get_current_user()
    now = datetime.utcnow()

     # -------- ترحيب حسب الوقت --------
    hour = now.hour
    if hour < 12:
        greeting = "صباح الخير"
    elif hour < 18:
        greeting = "مساء الخير"
    else:
        greeting = "مساء الخير"

    # -------- تحميل usage_dates --------
    usage_dates_str = user.usage_dates or '[]'
    try:
        usage_dates = json.loads(usage_dates_str)
    except:
        usage_dates = []

    today_date_str = now.strftime('%Y-%m-%d')

    # تسجيل يوم الاستخدام إذا لم يكن موجوداً
    if today_date_str not in usage_dates:
        usage_dates.append(today_date_str)
        user.usage_dates = json.dumps(usage_dates)
        db.session.commit()

    # -------- إنشاء stats --------
    stats = {
        "usage_days": len(usage_dates),
        "challenges_completed": user.challenges_completed or 0,
        "consultations": user.consultations or 0,
    }

    # -------- احضار عدد الأدوية من قاعدة البيانات --------
    medicines_count = Medication.query.filter_by(user_id=user.id).count()

    return render_template(
        'dashboard.html',
        user=user,
        greeting=greeting,
        usage_dates=usage_dates,
        stats=stats,
        medicines_count=medicines_count   # ← تم إضافته هنا
    )

@myapp.route('/biometrics', methods=['GET', 'POST'])
@login_required
def biometrics_view():
    user = get_current_user()  # جلب بيانات المستخدم الحالي
    result = None  # متغير لحفظ نتيجة التحليل عند الحاجة
    if request.method == 'POST':  # تنفيذ المنطق عند إرسال النموذج
        metric_type = request.form.get('metric_type', '').strip()  # نوع القياس المطلوب فحصه
        if metric_type not in {'glucose', 'blood_pressure', 'heart_rate'}:  # التحقق من صحة النوع
            flash('الرجاء اختيار نوع القياس الصحيح.', 'error')
            return redirect(url_for('biometrics_view'))
        try:
            if metric_type == 'glucose':  # معالجة قياس سكر الدم
                value_str = request.form.get('glucose_value', '').strip().replace(',', '.')  # قراءة قيمة السكر
                value = float(value_str)
                if value < 70:
                    status = 'منخفض'
                elif value <= 140:
                    status = 'طبيعي'
                else:
                    status = 'مرتفع'
                summary = f"قياس السكر لديك هو {value} ملغم/ديسيلتر، وهو {status}."  # تلخيص النتيجة للمستخدم
                measurement_details = f"سكر الدم: {value} ملغم/ديسيلتر"
            elif metric_type == 'blood_pressure':  # معالجة قياس ضغط الدم
                systolic_str = request.form.get('systolic', '').strip()
                diastolic_str = request.form.get('diastolic', '').strip()
                systolic = float(systolic_str)
                diastolic = float(diastolic_str)
                if systolic < 90 or diastolic < 60:
                    status = 'منخفض'
                elif systolic <= 120 and diastolic <= 80:
                    status = 'طبيعي'
                else:
                    status = 'مرتفع'
                systolic_display = int(round(systolic))
                diastolic_display = int(round(diastolic))
                summary = f"ضغطك هو {systolic_display}/{diastolic_display} مم زئبقي، وهو {status}."
                measurement_details = f"ضغط الدم: {systolic_display}/{diastolic_display} مم زئبقي"
            else:  # معالجة معدل نبض القلب
                value_str = request.form.get('heart_rate', '').strip().replace(',', '.')
                value = float(value_str)
                if value < 60:
                    status = 'منخفض'
                elif value <= 100:
                    status = 'طبيعي'
                else:
                    status = 'مرتفع'
                heart_rate_display = int(round(value))
                summary = f"نبض قلبك هو {heart_rate_display} ضربة في الدقيقة، وهو {status}."
                measurement_details = f"معدل نبض القلب: {heart_rate_display} ضربة في الدقيقة"
        except ValueError:
            flash('الرجاء إدخال أرقام صحيحة للقياسات.', 'error')  # تنبيه عند إدخال قيم غير رقمية
            return redirect(url_for('biometrics_view'))
        advice_prompt = (
            "أنت طبيب عربي مختص بالصحة العامة. استقبل البيانات التالية وقدم نصائح قصيرة وعملية باللغة العربية، "
            "تتضمن ثلاث توصيات بحد أقصى بناءً على حالة القياس. ذكر المستخدم بأن النصائح لا تغني عن استشارة طبيب عند الطوارئ. "
            f"{summary} التفاصيل: {measurement_details}."
        )  # تجهيز الطلب الخاص بالذكاء الاصطناعي لتقديم النصائح
        advice = generate_ai_reply(advice_prompt)  # الحصول على النصائح من الذكاء الاصطناعي
        if advice.startswith('تعذر') or advice.startswith('الرجاء'):
            advice = 'تعذر الحصول على نصائح من المساعد حالياً، يرجى المحاولة لاحقاً.'  # رسالة بديلة عند فشل الذكاء الاصطناعي
        status_styles = {
            'منخفض': {'badge': 'bg-blue-100 text-blue-600', 'card': 'border-blue-200'},
            'طبيعي': {'badge': 'bg-green-100 text-green-600', 'card': 'border-green-200'},
            'مرتفع': {'badge': 'bg-red-100 text-red-600', 'card': 'border-red-200'}
        }  # أنماط عرض مختلفة حسب حالة القياس
        styles = status_styles.get(status, status_styles['طبيعي'])  # اختيار النمط المناسب للحالة
        result = {
            'metric_type': metric_type,
            'status': status,
            'summary': summary,
            'measurement_details': measurement_details,
            'advice': advice,
            'badge_class': styles['badge'],
            'card_class': styles['card']
        }  # بناء نتيجة التحليل لعرضها في الواجهة
    return render_template('biometrics.html', result=result, user=user)  # عرض صفحة القياسات مع النتيجة الحالية
@myapp.route('/diet', methods=['GET', 'POST'])
@login_required
def diet_view():
    user = get_current_user()  # المستخدم الحالي
    ai_reply = None  # تعريف المتغير مسبقًا لتجنب الأخطاء

    if request.method == 'POST':
        # التحقق من الحقول المطلوبة
        required_fields = ['age', 'height', 'weight', 'gender', 'activity', 'goal']
        if not all(request.form.get(field) for field in required_fields):
            flash('الرجاء تعبئة جميع الحقول المطلوبة.', 'error')
            return redirect(url_for('diet_view'))

        # تجميع البيانات
        form_data = {
            'age': request.form['age'],
            'height': request.form['height'],
            'weight': request.form['weight'],
            'gender': request.form['gender'],
            'activity': request.form['activity'],
            'goal': request.form['goal'],
            'allergies': request.form.get('allergies', '')
        }

        # إنشاء الرسالة المرسلة للذكاء الاصطناعي
        prompt = (
            "أنت أخصائي تغذية محترف. أنشئ خطة غذائية يومية باللغة العربية استناداً إلى هذه البيانات: "
            f"العمر: {form_data['age']} سنة، "
            f"الجنس: {form_data['gender']}. "
            f"الطول: {form_data['height']} سم، "
            f"الوزن: {form_data['weight']} كجم. "
            f"مستوى النشاط: {form_data['activity']}. "
            f"الهدف: {form_data['goal']}. "
            f"الحساسيات أو الأطعمة الممنوعة: {form_data['allergies'] or 'لا يوجد'}. "
            "قدّم خطة متوازنة بثلاث وجبات رئيسية ووجبات خفيفة اختيارية، مع ذكر السعرات التقديرية والتنبيهات الصحية المناسبة."
        )

        # الحصول على الخطة من الذكاء الاصطناعي
        ai_reply = generate_ai_reply(prompt)

        # التحقق من فشل الذكاء الاصطناعي
        if not ai_reply or ai_reply.startswith('تعذر') or ai_reply.startswith('الرجاء إعداد'):
            flash(ai_reply or "حدث خطأ أثناء إنشاء الخطة.", 'error')
            return render_template('diet.html', plan=None, user=user)

        # حفظ الخطة في جدول Meal
        new_meal = Meal(
            user_id=user.id,
            name=ai_reply,
            calories=0,
            meal_date=date.today()
        )

        db.session.add(new_meal)
        db.session.commit()

        flash('تم حفظ الخطة الغذائية بنجاح.', 'success')

    # العرض سواء GET أو POST
    return render_template('diet.html', plan=ai_reply, user=user)
@myapp.route('/sports', methods=['GET', 'POST'])
@login_required
def sports_view():
    user = get_current_user() 
    videos = [] 
    selected_sport = '' 
    error_message = None

    if request.method == 'POST':
        selected_sport = request.form.get('sport_type', '').strip()
        videos, error_message = fetch_sport_videos(selected_sport)

        if error_message:
            flash(error_message, 'error')
            videos = []
        else:
            flash('تم جلب التمارين المقترحة.', 'success')

            # ⬅️ الكود الجديد: تسجيل البحث في قاعدة البيانات باستخدام SportsData
            new_sports_data = SportsData(
                user_id=user.id, # استخدام user.email من كائن SQLAlchemy
                sport_type=selected_sport,
                videos=json.dumps(videos), # ⬅️ تحويل قائمة الفيديوهات إلى نص JSON للحفظ
                timestamp=datetime.utcnow().isoformat()
            )
            db.session.add(new_sports_data)
            db.session.commit() # ⬅️ حفظ السجل الجديد في DB

    return render_template('sports.html',
                           user=user,
                           videos=videos,
                           selected_sport=selected_sport)

@myapp.route('/consultation', methods=['GET'])
@login_required
def consultation_view():
    user = get_current_user() # ⬅️ يجب جلب كائن المستخدم للوصول إلى بريده
    
    # ⬅️ التعديل: استبدال الإضافة إلى القائمة العامة (consultation_data) بالحفظ في DB
    new_consultation_entry = ConsultationData( user_id=user.id,  timestamp=datetime.utcnow())
    
    db.session.add(new_consultation_entry)
    db.session.commit() # ⬅️ حفظ السجل في قاعدة البيانات

    return render_template('consultation.html')
@myapp.route('/medicine', methods=['GET', 'POST'])
@login_required
def medicine_view():
    user = get_current_user() 
    
    if request.method == 'POST': 
        action = request.form.get('action') 
        
        # =====================================================
        # 1) إضافة دواء جديد
        # =====================================================
        if action == 'add':

            name = request.form.get('name', '').strip()
            dosage = request.form.get('dosage', '').strip()
            time1 = request.form.get('time1', '').strip()
            time2 = request.form.get('time2', '').strip()
            notes = request.form.get('notes', '').strip()

            if not name or not dosage or not time1:
                flash('الرجاء إدخال اسم الدواء والجرعة ووقت التذكير الأول.', 'error')
                return redirect(url_for('medicine_view'))

            # تحديث الهاتف
            phone_input = request.form.get('phone', '').strip()
            if phone_input:
                user.phone = phone_input  

            if not user.phone:
                flash('الرجاء إدخال رقم هاتف صالح لاستلام التذكيرات.', 'error')
                return redirect(url_for('medicine_view'))

            # تحديث Telegram ID
            telegram_input = request.form.get('telegram_chat_id', '').strip()
            if telegram_input:
                user.telegram_chat_id = telegram_input

            if not user.telegram_chat_id:
                flash('الرجاء إدخال معرف تيليجرام صالح لاستلام التذكيرات.', 'error')
                return redirect(url_for('medicine_view'))

            db.session.commit()

            # تحليل الذكاء الاصطناعي
            ai_insight = analyze_medicine_with_ai(name, dosage)

            # إضافة الدواء إلى جدول MEDICATIONS (بدون time1 / time2)
            medicine_entry = Medication(
                user_id=user.id,
                medication_name=name,
                dosage=dosage,
                notes=notes,
                ai_insight=ai_insight,
                telegram_chat_id=user.telegram_chat_id,
                time1=time1,   # ← أضف هذا السطر
                time2=time2,
            )

            db.session.add(medicine_entry)
            db.session.commit()  # لازم commit هنا عشان الدواء يأخذ ID

            # =====================================================
            # 2) إضافة التذكيرات لجدول medication_reminders
            # =====================================================
            reminder1 = MedicationReminder(
                medication_id=medicine_entry.id,
                reminder_time=time1
            )
            db.session.add(reminder1)

            if time2:
                reminder2 = MedicationReminder(
                    medication_id=medicine_entry.id,
                    reminder_time=time2
                )
                db.session.add(reminder2)

            db.session.commit()

            flash('تمت إضافة الدواء بنجاح وتم تفعيل التذكيرات.', 'success')
            return redirect(url_for('medicine_view'))

        # =====================================================
        # 3) حذف دواء
        # =====================================================
        elif action == 'delete':
            medication_id = request.form.get('medication_id')

            if medication_id and medication_id.isdigit():
                m = Medication.query.get(int(medication_id))

                if m and m.user_id == user.id:
                    db.session.delete(m)
                    db.session.commit()
                    flash('تم حذف الدواء بنجاح.', 'success')
                else:
                    flash('لا يمكن حذف هذا الدواء.', 'error')

            return redirect(url_for('medicine_view'))

    # =====================================================
    # 4) عرض قائمة الأدوية
    # =====================================================
    user_medications = user.medications

    for med in user_medications:
        med.next_reminder_text = build_next_reminder_text(med)

    return render_template('medicine.html', user=user, medications=user_medications)
@myapp.route('/hospitals', methods=['GET'])
@login_required
def hospitals_view():
    return render_template('hospitals.html')  # عرض صفحة المستشفيات القريبة
@myapp.route('/emergency', methods=['GET'])
@login_required
def emergency_view():
    return render_template('emergency.html')

@myapp.route('/api/hospitals', methods=['GET'])
@login_required
def hospitals_api():
    mode = request.args.get('mode', 'nearby').strip().lower()  # تحديد نوع الطلب الوارد

    if mode not in {'search', 'nearby'}:
        return jsonify({'error': 'وضع الطلب غير مدعوم.'}), 400

    if mode == 'search':
        search_query = request.args.get('query', '').strip()
        if not search_query:
            return jsonify({'error': 'الرجاء إدخال اسم المستشفى للبحث.'}), 400
        try:
            response = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={
                    'q': search_query,
                    'format': 'json',
                    'addressdetails': 1,
                    'limit': 12
                },
                headers={'User-Agent': 'HealthCompanion/1.0 (noreply@example.com)'},
                timeout=25
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return jsonify({'error': 'تعذر الحصول على بيانات المستشفيات.'}), 502
        items = response.json() if response.content else []
        results = []
        for item in items:
            lat_value = item.get('lat')
            lng_value = item.get('lon')
            if lat_value is None or lng_value is None:
                continue
            try:
                lat_float = float(lat_value)
                lng_float = float(lng_value)
            except (TypeError, ValueError):
                continue
            address_data = item.get('address') or {}
            address_parts = [
                address_data.get('country'),
                address_data.get('state'),
                address_data.get('city') or address_data.get('town') or address_data.get('village'),
                address_data.get('suburb'),
                address_data.get('road'),
                address_data.get('house_number')
            ]
            address = ', '.join(part for part in address_parts if part) or item.get('display_name')
            results.append({
                'name': item.get('display_name') or 'مستشفى',
                'address': address,
                'phone': None,
                'website': None,
                'location': {
                    'lat': lat_float,
                    'lng': lng_float
                },
                'tags': {},
                'opening_hours': None,
                'distance_meters': None,
                'google_map_url': f'https://www.google.com/maps/search/?api=1&query={lat_float},{lng_float}',
                'source': 'nominatim'
            })
        return jsonify({'hospitals': results, 'query': search_query})

    lat = request.args.get('lat')
    lng = request.args.get('lng')
    radius = request.args.get('radius', '5000')
    if not lat or not lng:
        return jsonify({'error': 'الرجاء تفعيل تحديد الموقع.'}), 400
    try:
        float_lat = float(lat)
        float_lng = float(lng)
        float_radius = float(radius)
    except ValueError:
        return jsonify({'error': 'إحداثيات أو نصف قطر غير صالح.'}), 400
    radius_int = max(100, int(float_radius))
    query = (
        '[out:json][timeout:25];'
        '('
        f'node["amenity"="hospital"](around:{radius_int},{float_lat},{float_lng});'
        f'way["amenity"="hospital"](around:{radius_int},{float_lat},{float_lng});'
        f'relation["amenity"="hospital"](around:{radius_int},{float_lat},{float_lng});'
        ');'
        'out center tags;'
    )
    try:
        response = requests.post(
            'https://overpass-api.de/api/interpreter',
            data=query.encode('utf-8'),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return jsonify({'error': 'تعذر الحصول على بيانات المستشفيات.'}), 502
    data = response.json()
    elements = data.get('elements', [])
    unique_results = {}
    for item in elements:
        tags = item.get('tags', {})
        center = item.get('center') or {}
        lat_value = item.get('lat') or center.get('lat')
        lng_value = item.get('lon') or center.get('lon')
        if lat_value is None or lng_value is None:
            continue
        try:
            lat_float = float(lat_value)
            lng_float = float(lng_value)
        except (TypeError, ValueError):
            continue
        address_parts = [
            tags.get('addr:country'),
            tags.get('addr:state'),
            tags.get('addr:city'),
            tags.get('addr:suburb'),
            tags.get('addr:street'),
            tags.get('addr:housenumber')
        ]
        address = ', '.join(part for part in address_parts if part)
        opening_hours = tags.get('opening_hours')
        phone = tags.get('phone') or tags.get('contact:phone')
        website = tags.get('website') or tags.get('contact:website')
        if website and not website.startswith(('http://', 'https://')):
            website = f"https://{website.lstrip('/')}"
        distance = haversine_distance(float_lat, float_lng, lat_float, lng_float)
        if distance is None:
            continue
        key = (round(lat_float, 6), round(lng_float, 6))
        payload = {
            'name': tags.get('name', 'مستشفى'),
            'address': address or tags.get('addr:full'),
            'phone': phone,
            'website': website,
            'location': {
                'lat': lat_float,
                'lng': lng_float
            },
            'tags': {
                'operator': tags.get('operator'),
                'operator_type': tags.get('operator:type'),
                'emergency': tags.get('emergency')
            },
            'opening_hours': opening_hours,
            'distance_meters': distance,
            'google_map_url': f'https://www.google.com/maps/search/?api=1&query={lat_float},{lng_float}',
            'source': 'openstreetmap'
        }
        existing = unique_results.get(key)
        if not existing or distance < existing['distance_meters']:
            unique_results[key] = payload
    results = list(unique_results.values())
    results.sort(key=lambda item: item['distance_meters'] if item['distance_meters'] is not None else float('inf'))
    limited_results = results[:20]
    return jsonify({'hospitals': limited_results, 'query': None})


@myapp.route('/messages', methods=['GET'])
@login_required
def messages_view():
    user = get_current_user()
    
    # ⬅️ التعديل: استبدال الإضافة إلى القائمة العامة بالحفظ في DB
    new_visit = ConsultationData(
         user_id=user.id, 
        timestamp=datetime.utcnow().isoformat()
    )
    db.session.add(new_visit)
    db.session.commit() # ⬅️ حفظ سجل الزيارة في قاعدة البيانات

    return render_template('messages.html', user=user)

@myapp.route('/messages/challenge', methods=['POST'])
@login_required
def complete_challenge():
    user = get_current_user() 

    # ⬅️ التعديل الأول: استخدام الخاصية المباشرة لزيادة العداد
    user.challenges_completed = (user.challenges_completed or 0) + 1 

    # ⬅️ التعديل الثاني: تسجيل الحدث في قاعدة البيانات (باستخدام ConsultationData كسجل عام)
    event_log = ConsultationData(
        user_id=user.id, 
        timestamp=datetime.utcnow().isoformat()
        # يمكن إضافة حقل event_type='challenge_completed' إذا كان النموذج يسمح
    )
    db.session.add(event_log)
    
    # ⬅️ التعديل الثالث: حفظ تحديث العداد وسجل الحدث في قاعدة البيانات
    db.session.commit() 
    
    flash('أحسنت! لقد أكملت تحدي اليوم.', 'success')
    return redirect(url_for('messages_view'))


@myapp.route('/api/consultation', methods=['POST'])
@login_required
def consultation_api():
    payload = request.get_json(silent=True) or {}
    message = payload.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'الرجاء إدخال استفسار صحي صحيح.'}), 400
        
    reply = generate_ai_reply(message)
    user = get_current_user()
    
    # ⬅️ التعديل الأول: استخدام الخاصية المباشرة لزيادة عداد الاستشارات
    # user.consultations هي حقل في كائن SQLAlchemy
    user.consultations = (user.consultations or 0) + 1 

    # ⬅️ التعديل الثاني: جلب السجل الحالي ومعالجته كـ JSON
    history_str = user.consultation_history or '[]' 
    try:
        # تحويل النص المخزن في DB إلى قائمة Python
        history = json.loads(history_str) 
    except:
        history = []
        
    history.append(datetime.utcnow().isoformat())
    
    # ⬅️ التعديل الثالث: حفظ القائمة كسلسلة نصية (JSON) في العمود
    # يتم تحويل قائمة Python إلى نص ليتم تخزينها في عمود db.Text
    user.consultation_history = json.dumps(history)
    
    # ⬅️ التعديل الرابع: حفظ جميع التغييرات في قاعدة البيانات
    db.session.commit() 

    return jsonify({'reply': reply})



if __name__ == "__main__":
    myapp.run(debug=True ,host="0.0.0.0",port=9000)
