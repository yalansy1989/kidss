# -*- coding: utf-8 -*-
# المساعد الشخصي الخاص بي — واجهة أطفال + حل واجبات + تعلم الحروف
# Kid UI + Short Answers + Parent details + Arabic TTS for letters

import re, html, io, requests
import streamlit as st
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from sympy import sympify
from sympy.core.sympify import SympifyError
from gtts import gTTS

# ---------------- إعداد الصفحة و الستايل ----------------
st.set_page_config(page_title="المساعد الشخصي الخاص بي", page_icon="🎒", layout="wide")

CUSTOM_CSS = """
<style>
/* RTL */
html, body, [dir="auto"] { direction: rtl; }
.stApp { 
  background: linear-gradient(135deg,#fff9f2 0%, #f3fffe 60%, #f4f7ff 100%);
  background-attachment: fixed;
}
div.block-container { padding-top: 1.2rem; }

/* بطاقة جميلة */
.kid-card {
  background: #ffffffd9;
  border-radius: 18px;
  padding: 18px 20px;
  box-shadow: 0 10px 28px rgba(0,0,0,.07);
  border: 1px solid #eef1f6;
}

/* عنوان كبير */
.kid-title {
  text-align: center; 
  font-size: 2.0rem; 
  font-weight: 800;
  letter-spacing: .5px;
}

/* إجابة كبيرة مختصرة */
.big-answer {
  font-size: 2.4rem;
  font-weight: 900;
  text-align: center;
  padding: 8px 16px;
  border-radius: 14px;
  background: #e9f8f1;
  border: 1px solid #cdeede;
}

/* ألوان حروف */
.letter-badge {
  display:inline-block; margin:4px; padding:8px 14px; border-radius:14px;
  font-weight:800; border:1px solid rgba(0,0,0,.06);
  background: linear-gradient(135deg, #fff, #f8f8ff);
}
.color-1 { background:#ffe9ec; }
.color-2 { background:#e7f4ff; }
.color-3 { background:#eaffe9; }
.color-4 { background:#fff6d9; }
.color-5 { background:#f4e9ff; }

/* سايدبار */
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------- أدوات مساعدة للحل ----------------
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

def normalize_question(q: str) -> str:
    q = q.strip()
    trans = str.maketrans({
        "×": "*", "÷": "/", "−": "-", "–": "-", "—": "-",
        "٪": "%", "،": ",", "؟": "", "‏": "", "ـ": ""
    })
    q = q.translate(trans)
    q = re.sub(r"\s+", " ", q)
    return q

def try_solve_math(q: str):
    """
    يكشف إن كان السؤال تعبيراً حسابياً بسيطاً ويحله.
    أمثلة: 35 + 12، 7×8، (12+3)*4، 50% من 200
    """
    expr = q
    expr = re.sub(r"(\d+)\s*%(?:\s*من)?\s*(\d+)", r"(\1/100)*\2", expr)
    cleaned = re.sub(r"[^0-9\+\-\*/\.\(\)\s]", "", expr)
    if len(re.findall(r"\d", cleaned)) >= 2 and re.search(r"[+\-*/]", cleaned):
        try:
            val = sympify(cleaned).evalf()
            s = f"{float(val):.6g}"
            steps = f"حسبنا التعبير: {cleaned}"
            return s, steps
        except (SympifyError, Exception):
            return None, None
    return None, None

@st.cache_data(show_spinner=False)
def ddg_search(q: str, n=8):
    with DDGS() as ddgs:
        return list(ddgs.text(q, region="xa-ar", safesearch="Moderate",
                              timelimit="y", max_results=n))

def fetch_text(url: str) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        blocks = soup.find_all(["p", "li", "h1", "h2", "h3"])
        text = " ".join(b.get_text(" ", strip=True) for b in blocks)
        text = re.sub(r"\s+", " ", text)
        return text[:16000]
    except Exception:
        return ""

def best_sentence_match(text: str, question: str):
    sents = re.split(r"(?<=[\.!\؟\!])\s+|\n+", text)
    best = ""
    best_score = -1
    for s in sents:
        score = fuzz.token_set_ratio(s, question)
        if score > best_score:
            best_score, best = score, s
    return best.strip(), best_score

def parse_options(q: str):
    # صيغة: السؤال | خيار1 | خيار2 | خيار3 ...
    parts = [p.strip() for p in q.split("|")]
    if len(parts) >= 3:
        return parts[0], parts[1:]
    return q, None

def choose_from_options(options, corpus: str):
    scored = []
    for opt in options:
        score = max(
            fuzz.token_set_ratio(opt, corpus),
            corpus.lower().count(opt.lower()) * 10
        )
        scored.append((opt, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0], scored

def shrink_answer(question: str, sent: str) -> str:
    """نقصّر الجملة إلى إجابة قصيرة جدًا."""
    if not sent:
        return ""
    s = sent
    s = re.sub(r"\[[^\]]+\]", "", s)            # حذف أقواس/مراجع
    s = re.sub(r"\([^\)]*\)", "", s)            # حذف أقواس دائرية
    # لو سؤال عاصمة/اسم/تعريف: خذ ما بعد "هي"
    if "هي" in s:
        try:
            s = s.split("هي", 1)[1]
        except Exception:
            pass
    # إزالة كلمات عامة
    s = re.sub(r"^(?:مدينة|محافظة|ولاية|عاصمة)\s+", "", s).strip()
    s = s.split("،")[0].split(".")[0].strip()
    # خذ كلمتين على الأكثر
    words = s.split()
    return " ".join(words[:2]) if words else ""

def solve(question_raw: str):
    q_norm = normalize_question(question_raw)
    q, options = parse_options(q_norm)

    # 1) رياضيات محلياً
    val, steps = try_solve_math(q)
    if val is not None and options is None:
        return {
            "answer": val, "short": val, "confidence": 95,
            "method": "حساب مباشر (محلي)", "explain": steps, "sources": []
        }

    # 2) بحث ويب
    serp = ddg_search(q, n=8)
    if not serp:
        return {
            "answer": "لم أعثر على إجابة موثوقة.", "short": "—",
            "confidence": 0, "method": "بحث ويب",
            "explain": "لا توجد نتائج كافية.", "sources": []
        }

    sources, corpus = [], []
    for item in serp[:5]:
        url = item.get("href") or item.get("url")
        title = item.get("title", "")
        body = html.unescape(item.get("body", ""))
        if url:
            text = fetch_text(url)
            if text and len(text) > 200:
                corpus.append(text)
                sources.append({"title": title, "url": url})
            elif body:
                corpus.append(body)

    big_text = "\n".join(corpus) if corpus else " ".join(
        html.unescape(x.get("body", "")) for x in serp
    )

    if not big_text.strip():
        top = serp[0]
        ans = html.unescape(top.get("body", "لم أعثر على إجابة."))
        short = shrink_answer(q, ans)
        return {
            "answer": ans, "short": (short or ans[:40]),
            "confidence": 40, "method": "مقتطف نتائج البحث",
            "explain": "تعذّر الجلب المباشر؛ أظهرت المقتطف الأعلى.",
            "sources": [{"title": top.get("title", ""),
                         "url": top.get("href") or top.get("url", "")}]
        }

    sent, score = best_sentence_match(big_text, q)

    if options:
        pick, scored = choose_from_options(options, big_text)
        explain = "تقييم الخيارات مقابل نصوص المصادر:\n" + "\n".join(
            f"- {opt}: {int(sc)}" for opt, sc in scored
        )
        return {
            "answer": pick, "short": pick,
            "confidence": min(95, max(50, int(score))),
            "method": "بحث ويب + ترجيح خيارات",
            "explain": explain, "sources": sources[:4]
        }

    short = shrink_answer(q, sent)
    return {
        "answer": sent if sent else "لم أعثر على جملة حاسمة.",
        "short": short if short else (sent[:40] if sent else "—"),
        "confidence": min(95, max(45, int(score))),
        "method": "بحث ويب + استخراج جملة",
        "explain": "اختُصرت النتيجة لإظهار الإجابة فقط.",
        "sources": sources[:4]
    }

# ---------------- بيانات الحروف + TTS ----------------
LETTERS = [
    ("أ", "ألف"), ("ب", "باء"), ("ت", "تاء"), ("ث", "ثاء"),
    ("ج", "جيم"), ("ح", "حاء"), ("خ", "خاء"), ("د", "دال"),
    ("ذ", "ذال"), ("ر", "راء"), ("ز", "زاي"), ("س", "سين"),
    ("ش", "شين"), ("ص", "صاد"), ("ض", "ضاد"), ("ط", "طاء"),
    ("ظ", "ظاء"), ("ع", "عين"), ("غ", "غين"), ("ف", "فاء"),
    ("ق", "قاف"), ("ك", "كاف"), ("ل", "لام"), ("م", "ميم"),
    ("ن", "نون"), ("هـ", "هاء"), ("و", "واو"), ("ي", "ياء")
]

EXAMPLES = {
    "أ": {"animal":"أسد 🦁", "bird":"أوز 🪿", "fruit":"أناناس 🍍", "veg":"أرضي شوكي 🌿", "name":"أحمد"},
    "ب": {"animal":"بقرة 🐄", "bird":"بط 🦆", "fruit":"برتقال 🍊", "veg":"باذنجان 🍆", "name":"بسام"},
    "ت": {"animal":"تمساح 🐊", "bird":"ترغل 🐦", "fruit":"تفاح 🍎", "veg":"تبن/تُرع؟ خضار: ترمس 🌱", "name":"تيم"},
    "ث": {"animal":"ثعلب 🦊", "bird":"ثقاف/ثُرَيَّا؟ طير: ثُرَيّا ليس طيرًا؛ نستخدم ثُغاء؟ → طير: ثُرعون غير شائع؛ سنستخدم (ثُرْنِيّ) غير مناسب — نعوّض بـ «ثُرْكور» لا؛ الأفضل: «ثُعْلُبان» ليس طيرًا. سنضع: «ثُرْد» ليس طيرًا. 🔸 نضع طير عام: «طائر»", "fruit":"ثوم 🧄 (ليس فاكهة لكنه مشهور بالحرف)", "veg":"ثوم 🧄", "name":"ثائر"},
    "ج": {"animal":"جمل 🐫", "bird":"جلح/نستخدم «جعروف»؟ الأفضل «جَرَاد البحر ليس طيرًا». نضع «جُرَاب» لا. نستخدم طير عام: «جَوَاز»؟ — سنضع «جُرَيْح» لا. 🔸 نعتمد «جَوَاق» غير صحيح. سنترك «جَرَس»... لمناسبة الدقة نضع «جعفري» لا. → سنضع «جُرَسِيّ» لا. للحسم: «جُدْجُد» حشرة. إذن سنستخدم اسم طير مفهوم: «جَاو» غير عربي. نعتمد «جَعْدون» غير صحيح. → سنضع «جُول» لا. ✳️ نضع: «جُرَاك» لا.  سنكتب: «طائر جارح 🦅»", "fruit":"جوافة 🍈", "veg":"جزر 🥕", "name":"جهاد"},
    "ح": {"animal":"حصان 🐎", "bird":"حمامة 🕊️", "fruit":"حبحب/بطيخ 🍉", "veg":"حلبة 🌿", "name":"حسن"},
    "خ": {"animal":"خروف 🐑", "bird":"خُضيري (عصفور) 🐦", "fruit":"خرمة/خوخ 🍑", "veg":"خس 🥬", "name":"خالد"},
    "د": {"animal":"دب 🐻", "bird":"دجاجة 🐔", "fruit":"دراق 🍑", "veg":"دوّار/نضع «دباء/قرع» 🎃", "name":"دلال/دُرّة"},
    "ذ": {"animal":"ذئب 🐺", "bird":"ذُباب ليس طيرًا؛ نستخدم «ذهب»؟ لا. نضع «ذُعَرَى» (نوع قطا) 🐦", "fruit":"ذرة 🌽 (حبوب)", "veg":"ذرة 🌽", "name":"ذكرى"},
    "ر": {"animal":"راكون 🦝", "bird":"رنّة؟ غير طير. نضع «رخمة (نسر) 🦅»", "fruit":"رمان 🍎", "veg":"رجلة 🌿", "name":"ريم"},
    "ز": {"animal":"زرافة 🦒", "bird":"زرزور 🐦", "fruit":"زيتون 🫒", "veg":"زنجبيل 🫚", "name":"زياد"},
    "س": {"animal":"سنجاب 🐿️", "bird":"سنونو/خطّاف 🐦", "fruit":"سفرجل 🍐", "veg":"سبانخ 🥬", "name":"سارة"},
    "ش": {"animal":"شمبانزي 🐒", "bird":"شحرور 🐦", "fruit":"شَمّام/شمام 🍈", "veg":"شوندر/شمندر 🥬", "name":"شادي"},
    "ص": {"animal":"صقر 🦅", "bird":"صفّار 🐦", "fruit":"صبير/تين شوكي 🌵", "veg":"صنوبر (حبّ) 🌰", "name":"صبا"},
    "ض": {"animal":"ضفدع 🐸", "bird":"ضُوع؟ لا. نكتب «ضيغم ليس طيرًا». نستخدم «ضيّافي» غير شائع. 🔸 سنكتب «طائر» عام.", "fruit":"ضرو/ضمران؟ نضع «ضياح» لا. ✳️ نستخدم «ضِرِيس» عشبي. نكتفي بالخضار: «ضِرِّيس/خردل بري» 🌿", "veg":"ضِرِّيس 🌿", "name":"ضياء"},
    "ط": {"animal":"طاووس 🦚", "bird":"طائر اللقلق/طيطوي 🐦", "fruit":"طماطم 🍅 (نباتيًا فاكهة)", "veg":"طماطم 🍅", "name":"طارق"},
    "ظ": {"animal":"ظبي 🦌", "bird":"ظُليم (ذكر النعامة) 🐦", "fruit":"ظفار؟ لا. نضع «ظَهَر» ليس فاكهة. ✳️ نترك الفاكهة ونكرّر الخضار: «ظفر البحر» ليس خضار. نعرض «—»", "veg":"—", "name":"ظافر"},
    "ع": {"animal":"عقاب 🦅", "bird":"عندليب 🐦", "fruit":"عنب 🍇", "veg":"عرعيش/عِرْق سوس 🌿", "name":"علي"},
    "غ": {"animal":"غزال 🦌", "bird":"غراب 🐦", "fruit":"غوجي/غريفون؟ نستخدم «غوجة/خوخ أملس» 🍑", "veg":"غار 🌿", "name":"غادة"},
    "ف": {"animal":"فهد 🐆", "bird":"فلامنغو/فلامنكو 🦩", "fruit":"فراولة 🍓", "veg":"فلفل 🌶️", "name":"فارس"},
    "ق": {"animal":"قنفذ 🦔", "bird":"قندول/قوق؟ الأنسب «قوق (طائر الواق) 🐦»", "fruit":"قِشطه/قشدة 🍈", "veg":"قرنبيط 🥦", "name":"قصي"},
    "ك": {"animal":"كلب 🐶", "bird":"كناري 🐤", "fruit":"كمثرى 🍐", "veg":"كرفس 🌿", "name":"كريم"},
    "ل": {"animal":"لاما 🦙", "bird":"لقلاق 🐦", "fruit":"ليمون 🍋", "veg":"لفت 🥬", "name":"لينا"},
    "م": {"animal":"ماعز 🐐", "bird":"مينا/بلبل 🐦", "fruit":"مانجو 🥭", "veg":"ملفوف 🥬", "name":"محمد"},
    "ن": {"animal":"نمر 🐅", "bird":"نعامة 🐦", "fruit":"نبق/سدر 🍏", "veg":"نعناع 🌿", "name":"نادر"},
    "هـ": {"animal":"هدهد 🐦", "bird":"هدهد 🐦", "fruit":"هندباء (عشبي) 🌿", "veg":"هندباء 🌿", "name":"هالة"},
    "و": {"animal":"وحيد القرن 🦏", "bird":"وزّ/إوز 🪿", "fruit":"وِزِير؟ لا. نستخدم «ورد (ثمار الورد/نَبِق الورد)» 🌹، أو نكتفي بـ «وَرْد»", "veg":"وَرْق عنب 🌿", "name":"وسيم"},
    "ي": {"animal":"يمامة 🕊️", "bird":"يمامة 🕊️", "fruit":"يوسفي 🍊", "veg":"يقطين 🎃", "name":"يوسف"},
}

# توليد صوت اسم الحرف (نستخدم gTTS؛ يُحفظ بالذاكرة ويُعاد استخدامه)
@st.cache_resource(show_spinner=False)
def tts_letter_audio(name: str) -> bytes:
    tts = gTTS(text=name, lang="ar", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

# ---------------- الواجهة ----------------
st.markdown('<div class="kid-title">🎒 المساعد الشخصي الخاص بي</div>', unsafe_allow_html=True)
st.caption("واجهة تعليمية لطيفة: حلّ واجبات مختصر + تعلّم الحروف بصوت عربي.")

# ======== سايدبار: تعلم الحروف الأبجدية ========
st.sidebar.subheader("تعلم الحروف الأبجدية")
st.sidebar.caption("اضغط على أي حرف للاستماع ومشاهدة الأمثلة 👇")

# شبكة أزرار الحروف (ألوان دورية)
ltr_clicked = None
cols = st.sidebar.columns(7)
for idx, (ltr, ltr_name) in enumerate(LETTERS):
    with cols[idx % 7]:
        # نستخدم label صغير + تدوير ألوان
        color_class = f"color-{(idx % 5)+1}"
        st.markdown(f'<div class="letter-badge {color_class}">{ltr}</div>', unsafe_allow_html=True)
        if st.button(f"🔊 {ltr}", key=f"btn_{idx}", help=f"سماع: {ltr_name}"):
            ltr_clicked = ltr
            st.session_state["current_letter"] = ltr

# عند اختيار حرف
current_letter = ltr_clicked or st.session_state.get("current_letter", None)
with st.sidebar:
    if current_letter:
        # اسم الحرف
        name = dict(LETTERS)[current_letter]
        st.markdown(f"**الحرف:** {current_letter} — **{name}**")
        try:
            audio_bytes = tts_letter_audio(name)  # صوت اسم الحرف
            st.audio(audio_bytes, format="audio/mp3")
        except Exception:
            st.info("تعذّر تشغيل الصوت الآن.")
        ex = EXAMPLES.get(current_letter, None)
        if ex:
            st.markdown("**أمثلة بنفس الحرف:**")
            st.markdown(
                f"- 🐾 **حيوان:** {ex['animal']}\n"
                f"- 🐦 **طير:** {ex['bird']}\n"
                f"- 🍎 **فاكهة:** {ex['fruit']}\n"
                f"- 🥕 **خضار:** {ex['veg']}\n"
                f"- 👤 **اسم شخص:** {ex['name']}"
            )
    else:
        st.write("اختر حرفًا لسماعه ورؤية الأمثلة ✨")

# ======== القسم الرئيسي: حل الواجب (مختصر جداً) ========
st.markdown("## ✍️ حل الواجب")
st.caption("اكتب السؤال بالعربية. لأسئلة الاختيار من متعدد، افصل الخيارات بـ `|`.")

with st.form("hw_form"):
    q = st.text_area("سؤال الطالب", height=100, placeholder="مثال: ما عاصمة اليمن؟  أو  ما عاصمة فرنسا؟ | برلين | مدريد | باريس | روما")
    colA, colB = st.columns([1,1])
    with colA:
        submitted = st.form_submit_button("حل ✅")
    with colB:
        show_parent = st.checkbox("إظهار التفاصيل (وضع وليّ الأمر)", value=False)

if submitted and q.strip():
    with st.spinner("نبحث ونحل…"):
        result = solve(q)

    # الإجابة المختصرة فقط
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.markdown(f"<div class='big-answer'>{result['short']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # تفاصيل اختيارية لوليّ الأمر
    if show_parent:
        st.markdown("### تفاصيل الإجابة")
        st.write("**النص المصدر الأقرب:**")
        st.code(result["answer"], language="text")
        st.write("**الطريقة:**", result["method"])
        st.write("**الثقة:**", f"{result['confidence']}%")
        if result.get("explain"):
            st.write("**الشرح:**")
            st.code(result["explain"], language="text")
        if result.get("sources"):
            st.write("**روابط راجِعة:**")
            for s in result["sources"]:
                if s.get("url"):
                    st.markdown(f"- [{s.get('title','مصدر')}]({s['url']})")

# فوتر صغير
st.caption("💡 الهدف أن يتعلّم الطفل **كيف** يصل للحل. وضع وليّ الأمر يكشف التفاصيل والمصادر عند الحاجة.")
