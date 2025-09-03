# -*- coding: utf-8 -*-
# المساعد الشخصي — تعليم الحروف العربية والإنجليزية + الأرقام + نطق تلقائي + اختبار تكوين جملة

import io, base64
import streamlit as st
from gtts import gTTS

st.set_page_config(page_title="المساعد الشخصي — تعليم الحروف", page_icon="🎨", layout="wide")

# ========= ستايل طفولي لطيف =========
st.markdown("""
<style>
html, body { direction: rtl; }
.stApp {
  background: linear-gradient(135deg,#fff9f2 0%, #f3fffe 50%, #f4f7ff 100%);
  background-attachment: fixed;
}
.block-container { padding-top: 1rem; }
.kid-title{ text-align:center;font-weight:900;font-size:2.1rem; }
.kid-card{ background:#ffffffd9;border:1px solid #eef1f6;border-radius:18px;padding:14px 16px;box-shadow:0 10px 26px rgba(0,0,0,.06); }
.badge{ display:inline-block;margin:6px;padding:10px 14px;border-radius:14px;font-weight:800;border:1px solid rgba(0,0,0,.06);background:#fff; }
.c1{background:#ffe9ec;} .c2{background:#e7f4ff;} .c3{background:#eaffe9;} .c4{background:#fff6d9;} .c5{background:#f4e9ff;}
.grid7 > div{display:inline-block;margin:4px}
audio{ width:100%; outline:none; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="kid-title">🎨 المساعد الشخصي — تعليم الحروف</div>', unsafe_allow_html=True)
st.caption("انقر على أي حرف أو رقم لسماع نُطقه فورًا، وشاهد الأمثلة المناسبة لأول حرف. في الأسفل اختبار لتكوين جملة ونطقها.")

# ========= أدوات الصوت =========
@st.cache_resource(show_spinner=False)
def tts_bytes(text: str, lang: str = "ar", slow: bool = False) -> bytes:
    tts = gTTS(text=text, lang=lang, slow=slow)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

def autoplay_audio(audio_bytes: bytes):
    """تشغيل تلقائي عبر <audio autoplay> لتفادي ضغط زر التشغيل."""
    b64 = base64.b64encode(audio_bytes).decode()
    html_audio = f"""
    <audio autoplay controls>
      <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(html_audio, unsafe_allow_html=True)

# ========= بيانات الحروف والأرقام + أمثلة =========
AR_LETTERS = [
    ("أ","ألف"),("ب","باء"),("ت","تاء"),("ث","ثاء"),("ج","جيم"),("ح","حاء"),("خ","خاء"),
    ("د","دال"),("ذ","ذال"),("ر","راء"),("ز","زاي"),("س","سين"),("ش","شين"),
    ("ص","صاد"),("ض","ضاد"),("ط","طاء"),("ظ","ظاء"),("ع","عين"),("غ","غين"),
    ("ف","فاء"),("ق","قاف"),("ك","كاف"),("ل","لام"),("م","ميم"),("ن","نون"),("هـ","هاء"),("و","واو"),("ي","ياء")
]

# أمثلة عربية لكل حرف: حيوان، طير، فاكهة، خضار، اسم شخص
AR_EX = {
 "أ":{"animal":"أسد 🦁","bird":"أوز 🪿","fruit":"أناناس 🍍","veg":"أرضي شوكي 🌿","name":"أحمد"},
 "ب":{"animal":"بقرة 🐄","bird":"بط 🦆","fruit":"برتقال 🍊","veg":"باذنجان 🍆","name":"بسام"},
 "ت":{"animal":"تمساح 🐊","bird":"ترغل 🐦","fruit":"تفاح 🍎","veg":"تُرمس 🌱","name":"تيم"},
 "ث":{"animal":"ثعلب 🦊","bird":"ثُرَيّا (نستخدم طائر عام) 🐦","fruit":"ثوم 🧄","veg":"ثوم 🧄","name":"ثائر"},
 "ج":{"animal":"جمل 🐫","bird":"جَلم/طائر جارح 🦅","fruit":"جوافة 🍈","veg":"جزر 🥕","name":"جهاد"},
 "ح":{"animal":"حصان 🐎","bird":"حمامة 🕊️","fruit":"حبحب 🍉","veg":"حلبة 🌿","name":"حسن"},
 "خ":{"animal":"خروف 🐑","bird":"خُضيري 🐦","fruit":"خوخ 🍑","veg":"خس 🥬","name":"خالد"},
 "د":{"animal":"دب 🐻","bird":"دجاجة 🐔","fruit":"دراق 🍑","veg":"دُباء 🎃","name":"دلال"},
 "ذ":{"animal":"ذئب 🐺","bird":"ذُعَرَى 🐦","fruit":"ذرة 🌽","veg":"ذرة 🌽","name":"ذكرى"},
 "ر":{"animal":"راكون 🦝","bird":"رخمة 🦅","fruit":"رمان 🍎","veg":"رجلة 🌿","name":"ريم"},
 "ز":{"animal":"زرافة 🦒","bird":"زرزور 🐦","fruit":"زيتون 🫒","veg":"زنجبيل 🫚","name":"زياد"},
 "س":{"animal":"سنجاب 🐿️","bird":"سنونو 🐦","fruit":"سفرجل 🍐","veg":"سبانخ 🥬","name":"سارة"},
 "ش":{"animal":"شمبانزي 🐒","bird":"شحرور 🐦","fruit":"شمام 🍈","veg":"شمندر 🥬","name":"شادي"},
 "ص":{"animal":"صقر 🦅","bird":"صفّار 🐦","fruit":"صبير 🌵","veg":"صنوبر 🌰","name":"صبا"},
 "ض":{"animal":"ضفدع 🐸","bird":"(طائر عام) 🐦","fruit":"—","veg":"ضِرِّيس 🌿","name":"ضياء"},
 "ط":{"animal":"طاووس 🦚","bird":"طيطوي 🐦","fruit":"طماطم 🍅","veg":"طماطم 🍅","name":"طارق"},
 "ظ":{"animal":"ظبي 🦌","bird":"ظُليم 🐦","fruit":"—","veg":"—","name":"ظافر"},
 "ع":{"animal":"عقاب 🦅","bird":"عندليب 🐦","fruit":"عنب 🍇","veg":"عرقسوس 🌿","name":"علي"},
 "غ":{"animal":"غزال 🦌","bird":"غراب 🐦","fruit":"غوجة/خوخ 🍑","veg":"غار 🌿","name":"غادة"},
 "ف":{"animal":"فهد 🐆","bird":"فلامنغو 🦩","fruit":"فراولة 🍓","veg":"فلفل 🌶️","name":"فارس"},
 "ق":{"animal":"قنفذ 🦔","bird":"قوق (واق) 🐦","fruit":"قِشطه 🍈","veg":"قرنبيط 🥦","name":"قصي"},
 "ك":{"animal":"كلب 🐶","bird":"كناري 🐤","fruit":"كمثرى 🍐","veg":"كرفس 🌿","name":"كريم"},
 "ل":{"animal":"لاما 🦙","bird":"لقلاق 🐦","fruit":"ليمون 🍋","veg":"لفت 🥬","name":"لينا"},
 "م":{"animal":"ماعز 🐐","bird":"مينا/بلبل 🐦","fruit":"مانجو 🥭","veg":"ملفوف 🥬","name":"محمد"},
 "ن":{"animal":"نمر 🐅","bird":"نعامة 🐦","fruit":"نبق 🍏","veg":"نعناع 🌿","name":"نادر"},
 "هـ":{"animal":"هدهد 🐦","bird":"هدهد 🐦","fruit":"هندباء 🌿","veg":"هندباء 🌿","name":"هالة"},
 "و":{"animal":"وحيد القرن 🦏","bird":"وزّ/إوز 🪿","fruit":"ورد (ثمر الورد) 🌹","veg":"ورق عنب 🌿","name":"وسيم"},
 "ي":{"animal":"يمامة 🕊️","bird":"يمامة 🕊️","fruit":"يوسفي 🍊","veg":"يقطين 🎃","name":"يوسف"},
}

EN_LETTERS = [chr(c) for c in range(ord('A'), ord('Z')+1)]
EN_EX = {
 "A":{"animal":"Ant 🐜","bird":"Albatross 🐦","fruit":"Apple 🍎","veg":"Asparagus 🌿","name":"Adam"},
 "B":{"animal":"Bear 🐻","bird":"Bluebird 🐦","fruit":"Banana 🍌","veg":"Broccoli 🥦","name":"Bella"},
 "C":{"animal":"Cat 🐱","bird":"Crow 🐦","fruit":"Cherry 🍒","veg":"Carrot 🥕","name":"Chris"},
 # (نكتفي بنماذج… والبقية تُعرض بلا أمثلة إذا غير مذكورة)
}

AR_NUMS = ["٠","١","٢","٣","٤","٥","٦","٧","٨","٩"]
EN_NUMS = [str(i) for i in range(10)]

# ========= واجهة التبويبات =========
tabs = st.tabs(["الحروف العربية", "Alphabet (A-Z)", "الأرقام العربية", "English Numbers", "اختبار تكوين جملة"])

# ----- تبويب: الحروف العربية -----
with tabs[0]:
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("الحروف العربية")
    st.caption("اضغط على أي حرف لسماع اسم الحرف فورًا ومشاهدة الأمثلة.")
    cols = st.columns(7)
    if "ar_letter" not in st.session_state: st.session_state["ar_letter"] = None

    # شبكة الحروف
    for i, (ltr, name) in enumerate(AR_LETTERS):
        with cols[i % 7]:
            color = f"c{(i % 5)+1}"
            st.markdown(f'<div class="badge {color}">{ltr}</div>', unsafe_allow_html=True)
            if st.button(f"🔊 {ltr}", key=f"ar_{i}", help=f"سماع: {name}"):
                st.session_state["ar_letter"] = (ltr, name)

    # عرض الصوت + الأمثلة
    chosen = st.session_state.get("ar_letter")
    if chosen:
        ltr, name = chosen
        try:
            autoplay_audio(tts_bytes(name, "ar", slow=False))
        except Exception:
            st.info("تعذّر تشغيل الصوت الآن.")
        ex = AR_EX.get(ltr, None)
        if ex:
            st.markdown("**أمثلة تبدأ بنفس الحرف:**")
            st.markdown(
                f"- 🐾 **حيوان:** {ex['animal']}\n"
                f"- 🐦 **طير:** {ex['bird']}\n"
                f"- 🍎 **فاكهة:** {ex['fruit']}\n"
                f"- 🥕 **خضار:** {ex['veg']}\n"
                f"- 👤 **اسم شخص:** {ex['name']}"
            )
    st.markdown('</div>', unsafe_allow_html=True)

# ----- تبويب: الحروف الإنجليزية -----
with tabs[1]:
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("English Alphabet (A–Z)")
    st.caption("Click a letter to hear its name and see simple examples.")
    cols = st.columns(7)
    if "en_letter" not in st.session_state: st.session_state["en_letter"] = None

    for i, ltr in enumerate(EN_LETTERS):
        with cols[i % 7]:
            color = f"c{(i % 5)+1}"
            st.markdown(f'<div class="badge {color}">{ltr}</div>', unsafe_allow_html=True)
            if st.button(f"🔊 {ltr}", key=f"en_{i}", help=f"Hear: {ltr}"):
                st.session_state["en_letter"] = ltr

    chosen = st.session_state.get("en_letter")
    if chosen:
        try:
            autoplay_audio(tts_bytes(chosen, "en", slow=False))
        except Exception:
            st.info("Audio unavailable.")
        ex = EN_EX.get(chosen, None)
        st.markdown("**Examples:**")
        if ex:
            st.markdown(
                f"- 🐾 Animal: {ex['animal']}\n"
                f"- 🐦 Bird: {ex['bird']}\n"
                f"- 🍎 Fruit: {ex['fruit']}\n"
                f"- 🥕 Vegetable: {ex['veg']}\n"
                f"- 👤 Name: {ex['name']}"
            )
        else:
            st.markdown("- (Add your own examples later)")

    st.markdown('</div>', unsafe_allow_html=True)

# ----- تبويب: الأرقام العربية -----
with tabs[2]:
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("الأرقام العربية (٠–٩)")
    cols = st.columns(10)
    for i, num in enumerate(AR_NUMS):
        with cols[i]:
            st.markdown(f'<div class="badge c{(i%5)+1}" style="text-align:center;font-size:1.4rem">{num}</div>', unsafe_allow_html=True)
            if st.button(f"🔊 {num}", key=f"ar_num_{i}"):
                try:
                    autoplay_audio(tts_bytes(num, "ar"))
                except Exception:
                    st.info("تعذّر تشغيل الصوت.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----- تبويب: English Numbers -----
with tabs[3]:
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("English Numbers (0–9)")
    cols = st.columns(10)
    for i, num in enumerate(EN_NUMS):
        with cols[i]:
            st.markdown(f'<div class="badge c{(i%5)+1}" style="text-align:center;font-size:1.4rem">{num}</div>', unsafe_allow_html=True)
            if st.button(f"🔊 {num}", key=f"en_num_{i}"):
                try:
                    autoplay_audio(tts_bytes(num, "en"))
                except Exception:
                    st.info("Audio unavailable.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----- تبويب: اختبار تكوين جملة -----
with tabs[4]:
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.subheader("🧪 اختبار: كوّن جملة وانطقها")
    lang = st.radio("لغة النطق:", ["العربية", "English"], horizontal=True)
    sentence = st.text_area("اكتب جملة بسيطة هنا:", placeholder="مثال: أحبُ البرتقال 🍊", height=100)
    col1, col2 = st.columns([1,2])
    with col1:
        if st.button("🔊 نطق الجملة"):
            if sentence.strip():
                try:
                    autoplay_audio(tts_bytes(sentence, "ar" if lang == "العربية" else "en"))
                except Exception:
                    st.info("تعذّر تشغيل الصوت.")
            else:
                st.warning("اكتب جملة أولاً.")
    with col2:
        st.caption("نصيحة: استخدم كلمات من الأمثلة التي تعلّمها طفلك للتو ✨")
    st.markdown('</div>', unsafe_allow_html=True)

# فوتر
st.caption("💡 لو حاب تضيف صورًا بدل النصوص أو بطاقات تفاعلية، نطوّرها في الإصدار القادم.")
