"""Generate the Arabic (RTL) edition of the invitation from the English one.

Everything the guest can read is translated; the machinery — countdown, petals,
audio, RSVP posting, backup log — is carried over untouched so the two editions
stay in step. Run it again after any change to index.html.
"""
import io, os, re, sys

SRC = sys.argv[1]
OUT = sys.argv[2]

s = io.open(SRC, encoding="utf-8").read()

missing = []


def sub(old, new, count=None):
    """Replace, and remember anything that did not match so we fail loudly."""
    global s
    n = s.count(old)
    if n == 0:
        missing.append(old[:70])
        return
    if count is not None and n != count:
        missing.append("COUNT %d!=%d :: %s" % (n, count, old[:60]))
        return
    s = s.replace(old, new)


def resub(pat, new, flags=0, expect=1):
    global s
    s, n = re.subn(pat, new, s, flags=flags)
    if n != expect:
        missing.append("RE %d!=%d :: %s" % (n, expect, pat[:60]))


# ---------------------------------------------------------------- shell / head
sub('<html lang="en">', '<html lang="ar" dir="rtl">')

sub(
    '<title>Mahmoud & Nouran - The Wedding Celebration</title>',
    "<title>محمود ونوران — حفل الزفاف</title>",
)
sub(
    'content="The wedding celebration of Mahmoud &amp; Nouran — Thursday, September 24, 2026 at Lavendula Hall, Tiba Rose Hotel, Cairo."',
    'content="حفل زفاف محمود ونوران — الخميس ٢٤ سبتمبر ٢٠٢٦، قاعة لافندولا، فندق طيبة روز، القاهرة."',
)

# Arabic type: Aref Ruqaa for the calligraphic display, Amiri for headings,
# Tajawal for body. The Latin faces are dropped entirely.
resub(
    r'<link href="https://fonts\.googleapis\.com/css2\?family=Cinzel[^"]*" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Aref+Ruqaa:wght@400;700&family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">',
)

# The asset folder sits one level up now.
s = s.replace('src="assets/', 'src="../assets/')

# ---------------------------------------------------------------- type stack
sub(
    """                    fontFamily: {
                        cursive: ['Great Vibes', 'cursive'],
                        serifHeader: ['Cinzel', 'serif'],
                        bodyText: ['Jost', 'sans-serif'],
                        subHeader: ['Cormorant Garamond', 'serif'],
                    }""",
    """                    fontFamily: {
                        cursive: ['Aref Ruqaa', 'serif'],
                        serifHeader: ['Amiri', 'serif'],
                        bodyText: ['Tajawal', 'sans-serif'],
                        subHeader: ['Amiri', 'serif'],
                    }""",
)

sub("            font-family: 'Jost', sans-serif;", "            font-family: 'Tajawal', sans-serif;")
sub(
    """        .font-cursive { font-family: 'Great Vibes', cursive; }
        .font-cinzel { font-family: 'Cinzel', serif; letter-spacing: 0.06em; }""",
    """        .font-cursive { font-family: 'Aref Ruqaa', serif; line-height: 1.6; }
        /* No letter-spacing anywhere in Arabic: it prises apart letters that
           are supposed to join, and the word stops looking like a word. */
        .font-cinzel { font-family: 'Amiri', serif; }""",
)
sub(
    """        .font-playfair { font-family: 'Cormorant Garamond', serif; font-weight: 600; }""",
    """        .font-playfair { font-family: 'Amiri', serif; font-weight: 700; }

        /* Arabic runs shorter than Latin at the same point size, and Aref Ruqaa
           sits low; both want a little more room than the Latin original. */
        h1.font-cursive, h2.font-cursive { line-height: 1.5; padding-bottom: 0.12em; }""",
)

# Letter-spacing utilities: same reason, they break Arabic joining.
s = re.sub(r"\s(?:md:)?tracking-(?:tight|normal|wide|wider|widest)", "", s)

# Physical directions that need to flip with the text.
s = s.replace("top-3 left-3", "top-3 right-3")
sub("fixed bottom-5 left-5 z-40", "fixed bottom-5 right-5 z-40")
sub('class="space-y-4 text-left"', 'class="space-y-4 text-right"')

# ---------------------------------------------------------------- gallery tabs
# Seven photographs do not need filtering; the whole tab row goes and every
# picture is simply shown.
resub(
    r"[ \t]*<!-- Gallery Category Tabs -->\s*<div class=\"flex justify-center gap-2 mb-8 flex-wrap\">.*?</div>\n",
    "",
    flags=re.S,
)
resub(
    r"[ \t]*function filterGallery\(clickedTab, category\) \{.*?\n        \}\n\n",
    "",
    flags=re.S,
)

# This edition shows only the two childhood photographs, so every card that is
# not one of them is dropped, and the grid narrows to suit a pair.
resub(
    r'\n[ \t]*<div class="gallery-item (?:outings|engagement) .*?\n[ \t]*</div>\n[ \t]*</div>\n',
    "\n",
    flags=re.S,
    expect=5,
)
sub(
    '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6" id="galleryGrid">',
    '<div class="grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-6 max-w-3xl mx-auto" id="galleryGrid">',
)

# "Our Journey Together" went with the rest of the journey; the small label
# above it is heading enough for two baby photographs.
resub(r'\n[ \t]*<h2 class="font-cursive text-5xl text-\[#7d5a50\] mt-1">Our Journey Together</h2>', "")

# ---------------------------------------------------------------- copy
PAIRS = [
    # header
    ("Together With Their Families", "بمشاركة عائلتيهما"),
    ("The Wedding Celebration of", "يتشرفان بدعوتكم لحضور حفل زفاف"),
    (
        '"In the spirit of joy and tradition, we invite you to share our happiness as we celebrate our new beginning together."',
        "«بكل فرحٍ وامتنان، ندعوكم لمشاركتنا سعادتنا ونحن نبدأ حياتنا معًا.»",
    ),
    # countdown
    ("Counting Down To Our Big Day", "العدّ التنازلي ليومنا الكبير"),
    (">Days<", ">يوم<"),
    (">Hours<", ">ساعة<"),
    (">Mins<", ">دقيقة<"),
    (">Secs<", ">ثانية<"),
    # gallery
    ("Cherished Chapters", "ذكريات غالية"),
    (">Childhood<", ">الطفولة<"),
    (">Mahmoud</h4>", ">محمود</h4>"),
    (">Nouran</h4>", ">نوران</h4>"),
    ("Always dreaming big with a bright smile.", "يحلم دائمًا بالكبير، وابتسامته لا تفارقه."),
    ("Filled with joy and endless energy.", "مليئة بالفرح وطاقة لا تنتهي."),
    # alt text
    ('alt="Mahmoud as a little boy"', 'alt="محمود وهو طفل صغير"'),
    ('alt="Nouran as a little girl"', 'alt="نوران وهي طفلة صغيرة"'),
    # schedule
    ("Wedding Schedule", "برنامج الحفل"),
    ("Thursday, September 24, 2026", "الخميس ٢٤ سبتمبر ٢٠٢٦"),
    (">6:00 PM<", ">٦:٠٠ مساءً<"),
    (">7:00 PM<", ">٧:٠٠ مساءً<"),
    (">7:15 PM<", ">٧:١٥ مساءً<"),
    ("Guest Arrivals & Welcome", "استقبال الضيوف"),
    (
        "Doors open at 6:00 PM sharp — please try not to be late, the Katb Ketab begins at 7:00 PM.",
        "تفتح الأبواب في تمام ٦:٠٠ مساءً — نرجو ألا تتأخروا، فكتب الكتاب يبدأ في ٧:٠٠ مساءً.",
    ),
    (">Katb Ketab<", ">كتب الكتاب<"),
    ("The official tying of the wedding knot ceremony.", "مراسم عقد القران."),
    ("Zaffah & Celebration Party", "الزفة والاحتفال"),
    (
        "Joyous Egyptian Zaffah, music, dinner & dancing till late!",
        "زفة مصرية بهيجة، وموسيقى وعشاء ورقص حتى وقت متأخر!",
    ),
    ("📅 Add to Google Calendar", "📅 أضيفوا الموعد إلى تقويم جوجل"),
    # venue
    ("Venue & Location", "المكان"),
    ("Lavendula Hall", "قاعة لافندولا"),
    ("Tiba Rose Hotel", "فندق طيبة روز"),
    (
        "Join us at the elegant outdoor halls of Tiba Rose. Ample valet parking and convenient access available.",
        "ننتظركم في القاعات المفتوحة الأنيقة بفندق طيبة روز، ويتوفر موقف سيارات واسع وخدمة صف السيارات.",
    ),
    ("🗺️ Get Google Maps Directions", "🗺️ الاتجاهات على خرائط جوجل"),
    # rsvp form
    ("Honor Us With Your Presence", "شرفونا بحضوركم"),
    (">RSVP</h2>", ">تأكيد الحضور</h2>"),
    ("Full Name *</label>", "الاسم الكامل *</label>"),
    ('placeholder="e.g. Ahmed Hassan"', 'placeholder="مثال: أحمد حسن"'),
    ("Will You Attend? *</label>", "هل ستشرفوننا؟ *</label>"),
    (
        '<option value="" disabled selected>Select Attendance</option>',
        '<option value="" disabled selected>اختاروا الإجابة</option>',
    ),
    ('<option value="Yes">Yes</option>', '<option value="نعم">نعم، سأحضر</option>'),
    ('<option value="Maybe">Maybe</option>', '<option value="ربما">ربما</option>'),
    (
        '<option value="Unfortunately No">Unfortunately No</option>',
        '<option value="معتذر">للأسف لن أستطيع</option>',
    ),
    ("Number of Guests *</label>", "عدد الأشخاص *</label>"),
    ('<option value="1">1 Person</option>', '<option value="١">شخص واحد</option>'),
    ('<option value="2">2 Persons</option>', '<option value="٢">شخصان</option>'),
    ('<option value="3">3 Persons</option>', '<option value="٣">٣ أشخاص</option>'),
    ('<option value="4+">4 or More Persons</option>', '<option value="٤+">٤ أشخاص أو أكثر</option>'),
    ("🎵 Song Requests</label>", "🎵 أغنية تتمنونها</label>"),
    (
        'placeholder="A song that will get you onto the dance floor..."',
        'placeholder="أغنية تقوم بكم إلى ساحة الرقص..."',
    ),
    ("Warm Blessings</label>", "كلمة تهنئة</label>"),
    (
        'placeholder="Write a sweet message for Mahmoud &amp; Nouran..."',
        'placeholder="اكتبوا كلمة جميلة لمحمود ونوران..."',
    ),
    ("Confirm &amp; Submit RSVP", "أرسلوا تأكيد الحضور"),
    # modal
    (">Thank You!<", ">شكرًا لكم!<"),
    (
        "Your response has been saved and added to Mahmoud & Nouran's wedding guest list.",
        "تم حفظ ردكم وإضافته إلى قائمة ضيوف محمود ونوران.",
    ),
    ("Close Window", "إغلاق"),
    # backup log
    ("RSVP Backup Log (private)", "سجل الردود (خاص)"),
    (
        "Local copy of responses on this device — the live list lives in your Google Sheet",
        "نسخة محفوظة على هذا الجهاز — القائمة الحية في جدول جوجل",
    ),
    (">Timestamp<", ">التاريخ والوقت<"),
    (">Full Name<", ">الاسم<"),
    (">Attendance<", ">الحضور<"),
    (">Guests<", ">عدد الأشخاص<"),
    (">Song Requests<", ">الأغنية<"),
    (">Blessings<", ">التهنئة<"),
    (">Sent<", ">أُرسل<"),
    ("📥 Download Sheet (CSV)", "📥 تنزيل ملف الردود"),
    # footer
    (">Mahmoud & Nouran<", ">محمود ونوران<"),
    ("Made with ❤️", "صُنع بحب ❤️"),
    # ---- script-side, guest facing
    ("btn.innerText = 'Sending…';", "btn.innerText = 'جارٍ الإرسال…';"),
    ("|| 'None'", "|| 'لا شيء'"),
    (
        """const tone = { 'Yes': 'bg-emerald-100 text-emerald-800',
                                   'Maybe': 'bg-amber-100 text-amber-800',
                                   'Unfortunately No': 'bg-rose-100 text-rose-800' };""",
        """const tone = { 'نعم': 'bg-emerald-100 text-emerald-800',
                                   'ربما': 'bg-amber-100 text-amber-800',
                                   'معتذر': 'bg-rose-100 text-rose-800' };""",
    ),
    (
        """warm = response.attendance === 'Unfortunately No'
                ? `Thank you for letting us know, ${response.name} — you will be missed, and we appreciate the reply.`
                : `Thank you ${response.name}! Your response ("${response.attendance}") has been sent to Mahmoud & Nouran.`;""",
        """warm = response.attendance === 'معتذر'
                ? `شكرًا لإخبارنا يا ${response.name} — سنفتقدكم، ونقدّر لكم ردكم.`
                : `شكرًا لكم يا ${response.name}! تم إرسال ردكم ("${response.attendance}") إلى محمود ونوران.`;""",
    ),
    ('showModal("RSVP Received!", warm);', 'showModal("وصلنا ردكم!", warm);'),
    (
        'showModal("Sheet Empty", "There are no responses to export yet.");',
        'showModal("لا توجد ردود", "لا توجد ردود لتصديرها بعد.");',
    ),
    (
        'No RSVPs recorded on this device yet.',
        'لا توجد ردود محفوظة على هذا الجهاز بعد.',
    ),
    (
        "item.synced ? '✓ sent' : '⚠ local only',",
        "item.synced ? '✓ أُرسل' : '⚠ محفوظ محليًا',",
    ),
    (
        "const rows = [['Timestamp', 'Name', 'Attendance', 'Guests', 'Song Requests', 'Blessings', 'Sent to Sheet']];",
        "const rows = [['التاريخ والوقت', 'الاسم', 'الحضور', 'عدد الأشخاص', 'الأغنية', 'التهنئة', 'أُرسل']];",
    ),
    ("r.synced ? 'yes' : 'no'", "r.synced ? 'نعم' : 'لا'"),
    (
        'link.download = "Mahmoud_Nouran_Wedding_RSVP_Responses.csv";',
        'link.download = "ردود-حفل-محمود-ونوران.csv";',
    ),
    ("adminBtn.textContent = '📋 RSVP backup log';", "adminBtn.textContent = '📋 سجل الردود';"),
    # calendar entry the guest ends up with
    (
        "text=Mahmoud+%26+Nouran+Wedding&dates=20260924T150000Z/20260924T210000Z&details=Katb+Ketab+and+Wedding+Celebration+of+Mahmoud+%26+Nouran&location=Lavendula%2C+Tiba+Rose+Hotel%2C+5th+Settlement+Cairo",
        "text=%D8%B2%D9%81%D8%A7%D9%81+%D9%85%D8%AD%D9%85%D9%88%D8%AF+%D9%88%D9%86%D9%88%D8%B1%D8%A7%D9%86&dates=20260924T150000Z/20260924T210000Z&details=%D9%83%D8%AA%D8%A8+%D8%A7%D9%84%D9%83%D8%AA%D8%A7%D8%A8+%D9%88%D8%AD%D9%81%D9%84+%D8%B2%D9%81%D8%A7%D9%81+%D9%85%D8%AD%D9%85%D9%88%D8%AF+%D9%88%D9%86%D9%88%D8%B1%D8%A7%D9%86&location=%D9%82%D8%A7%D8%B9%D8%A9+%D9%84%D8%A7%D9%81%D9%86%D8%AF%D9%88%D9%84%D8%A7%D8%8C+%D9%81%D9%86%D8%AF%D9%82+%D8%B7%D9%8A%D8%A8%D8%A9+%D8%B1%D9%88%D8%B2%D8%8C+%D8%A7%D9%84%D8%AA%D8%AC%D9%85%D8%B9+%D8%A7%D9%84%D8%AE%D8%A7%D9%85%D8%B3+%D8%A7%D9%84%D9%82%D8%A7%D9%87%D8%B1%D8%A9",
    ),
]

for old, new in PAIRS:
    sub(old, new)

# The backup-log close button sits on its own line, so it needs a pattern.
resub(r'(closeSheetManager\(\)"[^>]*>)\s*Close\s*(</button>)', r"\1\n                        إغلاق\n                    \2")

# The couple's name in the hero and anywhere else it survived as raw text.
s = s.replace("Mahmoud &amp; Nouran", "محمود ونوران").replace("Mahmoud & Nouran", "محمود ونوران")

# ---------------------------------------------------------------- numerals
# Arabic-Indic digits everywhere the page writes numbers itself.
resub(
    r"        function updateCountdown\(\) \{",
    """        // Egypt reads ٠١٢٣ as readily as 0123, and a page with no Latin
        // letters should not be printing Latin digits either.
        const arabicDigits = n => String(n).replace(/[0-9]/g, d => '٠١٢٣٤٥٦٧٨٩'[d]);

        function updateCountdown() {""",
)
for fld in ("cdDays", "cdHours", "cdMins", "cdSecs"):
    resub(
        r"document\.getElementById\('%s'\)\.innerText = ([^;]+);" % fld,
        lambda m: "document.getElementById('%s').innerText = arabicDigits(%s);" % (fld, m.group(1)),
        expect=2,
    )
sub("timestamp: new Date().toLocaleString(),", "timestamp: new Date().toLocaleString('ar-EG'),")

if missing:
    print("UNMATCHED:")
    for m in missing:
        print("  -", m)
    sys.exit(1)

leftover = re.findall(r">[^<>]*[A-Za-z]{3}[^<>]*<", re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", s, flags=re.S))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", OUT)
if leftover:
    print("LEFTOVER LATIN TEXT NODES:")
    for t in leftover:
        print("  ", t.strip())
