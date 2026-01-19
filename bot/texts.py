START_ROLE_PROMPT = "Assalomu alaykum! Siz kim bo‘lib ro‘yxatdan o‘tasiz?"
ROLE_TEACHER = "O‘qituvchi"
ROLE_STUDENT = "O‘quvchi"

PHONE_PROMPT = "Ajoyib. Endi telefon raqamingizni yuboring."
PHONE_BUTTON = "📞 Telefon raqamni yuborish"
PHONE_OWNERSHIP_FAIL = (
    "Bu raqam sizning akkauntingizga tegishli emas. "
    "Iltimos, pastdagi tugma orqali o‘zingizning raqamingizni yuboring."
)
PHONE_TEXT_ONLY = "Telefon raqamini faqat tugma orqali yuborish mumkin. Pastdagi tugmani bosing."
PHONE_ALREADY_USED = "Bu telefon raqami allaqachon boshqa akkauntga bog‘langan. Iltimos, boshqa raqam yuboring."

NAME_PROMPT = "Rahmat! Endi ismingizni kiriting. Masalan: Shodmon"
NAME_INVALID = (
    "Ism noto‘g‘ri formatda kiritildi. Faqat harflardan foydalaning. "
    "Masalan: Shodmon Xolmurodov"
)
NAME_TEXT_ONLY = "Ismingizni matn ko‘rinishida yuboring."
MISSING_ROLE_PHONE = "Iltimos, avval rol va telefonni yuboring."

REGISTER_DONE_TEACHER = "Tabriklaymiz! Siz o‘qituvchi sifatida ro‘yxatdan o‘tdingiz."
REGISTER_DONE_STUDENT = "Ro‘yxatdan o‘tish yakunlandi. Endi testlarga tayyormiz!"
REFERRAL_SUCCESS = "Siz {teacher_name} o‘qituvchiga biriktirildingiz."
REFERRAL_NOT_FOUND = "Referral link topilmadi. Registratsiyani oddiy tartibda davom ettiramiz."

WELCOME_BACK = "Xush kelibsiz!"
NEED_START = "Davom etish uchun /start buyrug‘ini yuboring."
UNKNOWN_COMMAND = "Tushunmadim. Menyudagi tugmalardan foydalaning."

ADMIN_PROFILE_START = "Admin profil yaratish uchun ro‘yxatdan o‘tamiz."
ADMIN_DONE = "Admin panelga xush kelibsiz."
ADMIN_ONLY = "Bu buyruq faqat adminlar uchun."

HELP_TEXT = "Yordam uchun /start buyrug‘ini yuboring yoki admin bilan bog‘laning."

TEACHER_ONLY = "Bu bo‘lim faqat o‘qituvchilar uchun."
NO_STUDENTS = "Hozircha o‘quvchilaringiz yo‘q."
STUDENTS_LIST_TITLE = "O‘quvchilar ro‘yxati:"

PROFILE_TITLE = "Profil ma’lumotlari:"
ADMIN_SOON = "Bu bo‘lim keyinroq ishga tushadi."

NO_TEMPLATES = "Hozircha faol fan shablonlari yo‘q."
TEMPLATE_CHOOSE = "Fan shablonini tanlang:"
TEMPLATE_NOT_FOUND = "Shablon topilmadi. Qayta urinib ko‘ring."
TEST_TITLE_PROMPT = "Test nomini kiriting."
MATERIAL_PROMPT = "Agar material bo‘lsa, PDF yoki rasm yuboring."
MATERIAL_SKIP_HINT = "Agar material yo‘q bo‘lsa, \"O‘tkazib yuborish\" deb yozing."
MATERIAL_SKIP_WORD = "O‘tkazib yuborish"
TEACHER_KEYS_START = (
    "Test yaratildi! Endi javoblarni kiriting. Hammasi bitta joyda ko'rinadi."
)
STUDENT_KEYS_START = "Test boshlandi! Javoblaringiz bitta joyda ko'rinadi."
Y1_INSTRUCTION = "1-32 javoblarni yuboring. Misol: ACBDA... (32 ta harf)"
Y2_INSTRUCTION = "33-35 javoblar (A-E). Misol: ACD yoki 33-A,34-C,35-D"
OPEN_INSTRUCTION = (
    "36-45 (a/b) javoblarni bitta xabarda yuboring.\n"
    "Namuna:\n"
    "36a=12; 36b=23\n"
    "37a=14; 37b=8.4\n"
    "...\n"
    "45a=3; 45b=2.5"
)
Y1_PROMPT = "Y-1 javoblar kalitini yuboring (32 ta harf, faqat A/B/C/D)."
Y1_STUDENT_PROMPT = "Y-1 javoblaringizni yuboring (32 ta harf, faqat A/B/C/D)."
Y1_INVALID = "Y-1 javobi noto‘g‘ri. Talab: {error}."
Y2_PROMPT = (
    "33–35 savollar javoblarini yuboring (A–E).\n"
    "Misol: 33-A, 34-C, 35-D\n"
    "Yoki qisqa yozuv: ACD"
)
Y2_STUDENT_PROMPT = (
    "33–35 savollar javoblarini yuboring (A–E).\n"
    "Misol: ACD\n"
    "Yoki: 33-A, 34-C, 35-D"
)
Y2_INVALID = "Javob formati mos kelmadi: {error}. Masalan: ACD yoki 33-A,34-C,35-D."
Y2_OUTDATED = "33–35 savollar formati yangilandi. Iltimos, javoblarni qayta kiriting: 33-A,34-C,35-D."
O_PROMPT_A = "{item_no}-savol (a) javobini yuboring. Masalan: 12 yoki 7/8"
O_PROMPT_B = "{item_no}-savol (b) javobini yuboring. Masalan: -3 yoki 2.5"
O_STUDENT_PROMPT_A = "{item_no}-savol (a) javobi? Masalan: 12 yoki 7/8"
O_STUDENT_PROMPT_B = "{item_no}-savol (b) javobi? Masalan: -3 yoki 2.5"
O_INVALID = "Format mos kelmadi. Masalan: 12 | -3 | 7/8 | 2.5"
SUMMARY_ERROR = "Format mos kelmadi. Masalan: 7/8 yoki -3 yoki 2.5"
SUMMARY_CANCELLED = "Jarayon bekor qilindi."
SUMMARY_EDIT_PROMPT = "Qaysi bo‘limni qayta kiritamiz?"
SUMMARY_INCOMPLETE = "Avval barcha bo‘limlarni to‘ldiring."
PUBLISH_READY = "Hammasi tayyor. Testni e’lon qilamizmi?"
PUBLISHED_SUCCESS = "Test e’lon qilindi. Kod: {code}\nHavola: https://t.me/{bot}?start=test_{code}"
KEYS_INCOMPLETE = "Kalitlar to‘liq emas. Avval barcha bo‘limlarni kiriting."
TEACHER_PUBLISH_BLOCKED_MISSING_KEYS = (
    "Testni e’lon qilish uchun hamma bo‘lim javoblari kiritilishi kerak: Y-1, Y-2, O."
)
TEACHER_PUBLISH_BLOCKED_OPEN = (
    "Testni e’lon qilish uchun Ochiq savollar to‘liq kiritilishi kerak (36–45: a va b)."
)
OPEN_OUTDATED = (
    "Ochiq savollar (36–45) endi a va b javob bilan kiritiladi. Iltimos, qayta kiriting."
)
TEACHER_TEST_PUBLISHED = (
    "✅ Test tayyor!\n"
    "📌 Nomi: {title}\n"
    "📚 Fan: {subject}\n"
    "⏱ Vaqt: {time_limit} daqiqa\n\n"
    "🔑 Test kodi: `{code}`\n\n"
    "O‘quvchilar testni shu kod bilan ochishadi:\n"
    "1) Botdan “✅ Testga kirish” → kodni yozish\n"
    "2) Havola: {link}\n\n"
    "{material_note}"
    "Kodni o‘quvchilarga yuboring ✅"
)
TEACHER_MATERIAL_NOTE = "📎 Material biriktirildi.\n\n"
TEACHER_CLOSE_SOON = "Test yopildi. Yangi test yaratishingiz mumkin."
TEST_NOT_FOUND = "Test topilmadi."
GENERAL_RETRY = "Nimadir xato bo‘ldi. Iltimos, qayta urinib ko‘ring."
NO_TESTS = "Hozircha testlaringiz yo‘q."
MY_TESTS_TITLE = "Testlaringiz:"
ENTER_TEST_CODE = "Test kodini yuboring."
TEST_CODE_NOT_FOUND = "Kod topilmadi. Qayta tekshirib yuboring."
TEST_NOT_PUBLISHED = "Test hali e’lon qilinmagan."
ALREADY_SUBMITTED = "Siz bu testni allaqachon topshirgansiz."
SUBMIT_CONFIRM = "Javoblarni yuborishni tasdiqlaysizmi?"
RESULT_SUMMARY = "Natija:\nY1: {y1}/32\nY2: {y2}/3\nO: {o}/10\nJami: {total}/45"
NO_RESULTS = "Hozircha natijalar yo‘q."
RESULTS_TITLE = "Natijalar:"
STUDENT_ONLY = "Bu bo‘lim faqat o‘quvchilar uchun."
STUDENT_SUBMITTED_RESULT = (
    "✅ Test yakunlandi!\n"
    "🎯 Natijangiz: {total}/45\n\n"
    "Bo‘limlar:\n"
    "• 1–32 (Y-1): {y1}/32\n"
    "• 33–35: {y2}/3\n"
    "• 36–45 (O): {o}/10\n\n"
    "{feedback_line}\n"
    "{wrong_line}\n"
    "Natijalar saqlandi. Xohlasangiz, keyin ham ko‘rib turasiz."
)
STUDENT_SUBMITTED_RESULT_NO_WRONGS = "🔥 Zo‘r! Hammasi to‘g‘ri."
ALL_DONE_INSTRUCTION = "Hamma bo'limlar tayyor. Tasdiqlash tugmasini bosing."
