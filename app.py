# -*- coding: utf-8 -*-
# تعليم الحروف العربية — بلاطات كبيرة (3 في الصف) + نطق في موضع الحرف + أمثلة + اختبار جملة ونقاط

import io, base64, itertools
import streamlit as st
from gtts import gTTS

st.set_page_config(page_title="تعليم الحروف العربية", page_icon="🔤", layout="wide")

# ========= تنسيقات =========
st.markdown("""
<style>
html, body { direction: rtl; }
.stApp { background: linear-gradient(135deg,#fff9f2 0%, #f3fffe 55%, #f4f7ff 100%); }
.block-container { padding-top: 0.8rem; }
.title{ text-align:center;font-weight:900;font-size:2.2rem;margin:.4rem 0 .6rem }
.grid-row { display:flex; gap:12px; justify-content:center; margin-bottom:12px; }
.tile {
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  width:110px; height:110px; border-radius:18px; font-size:2.6rem; font-weight:900;
  border:1px solid #e9eef5; user-select:none; cursor:pointer;
  box-shadow:0 10px 22px rgba(0,0,0,.06); transition: transform .08s ease;
}
.tile:active { transform: scale(.98); }
.c1{background:#ffe9ec;} .c2{background:#e7f4ff;} .c3{background:#eaffe9;}
.c4{background:#fff6d9;} .c5{background:#f4e9ff;}
.tile-audio { height:0; overflow:hidden; width:100%; margin:0; padding:0; }
.card {
  background:#ffffffdd; border:1px solid #eef1f6; border-radius:18px;
  padding:16px 18px; box-shadow:0 10px 26px rgba(0,0,0,.06);
}
.examples span{ display:block; margin:.15rem 0;}
.score-badge{
  display:inline-block; background:#e9f8f1; border:1px solid #cdeede;
  padding:6px 12px; border-radius:12px; font-weight:800;
}
@media (max-width: 640px){
  .tile{ width:96px; height:96px; font-size:2.2rem }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔤 تعليم الحروف العربية</div>', unsafe_allow_html=True)
st.caption("اضغط على أي حرف — النطق يخرج من نفس البلاطة. أسفل الشبكة تظهر أمثلة للحرف المختار. بالأسفل اختبار جملة مع نقاط تحفيزية.")

# ========= أدوات الصوت =========
@st.cache_resource(show_spinner=False)
def tts_bytes(text: str, slow: bool = True, lang: str = "ar") -> bytes:
    tts = gTTS(text=text, lang=lang, slow=slow)  # slow=True لنطقٍ فصيح وواضح
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

def tile_autoplay(audio_bytes: bytes):
    """عنصر صوت يُحقن أسفل البلاطة نفسها."""
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f"""<audio class="tile-audio" autoplay>
              <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>""",
        unsafe_allow_html=True
    )

# ========= بيانات الحروف + أسماء الحروف بنطقٍ ساكن =========
LETTERS = [
    ("أ","ألفْ"),("ب","باءْ"),("ت","تاءْ"),("ث","ثاءْ"),("ج","جيمْ"),
    ("ح","حاءْ"),("خ","خاءْ"),("د","دالْ"),("ذ","ذالْ"),
    ("ر","راءْ"),("ز","زايْ"),("س","سينْ"),("ش","شينْ"),
    ("ص","صادْ"),("ض","ضادْ"),("ط","طاءْ"),("ظ","ظاءْ"),
    ("ع","عينْ"),("غ","غينْ"),("ف","فاءْ"),("ق","قافْ"),
    ("ك","كافْ"),("ل","لامْ"),("م","ميمْ"),("ن","نونْ"),
    ("هـ","هاءْ"),("و","واوْ"),("ي","ياءْ")
]

EX = {
 "أ":{"animal":"أسد 🦁","bird":"أوز 🪿","fruit":"أناناس 🍍","veg":"أرضي شوكي 🌿","name":"أحمد"},
 "ب":{"animal":"بقرة 🐄","bird":"بط 🦆","fruit":"برتقال 🍊","veg":"باذنجان 🍆","name":"بسام"},
 "ت":{"animal":"تمساح 🐊","bird":"ترغل 🐦","fruit":"تفاح 🍎","veg":"تُرمس 🌱","name":"تيم"},
 "ث":{"animal":"ثعلب 🦊","bird":"(طائر عام) 🐦","fruit":"ثوم 🧄","veg":"ثوم 🧄","name":"ثائر"},
 "ج":{"animal":"جمل 🐫","bird":"(طائر جارح) 🦅","fruit":"جوافة 🍈","veg":"جزر 🥕","name":"جهاد"},
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

# ========= حالة ونقاط =========
if "chosen" not in st.session_state:
    st.session_state["chosen"] = None
if "points" not in st.session_state:
    st.session_state["points"] = 0

# ========= شبكة الحروف — 3 في كل صف =========
def chunked(seq, n):
    it = iter(seq)
    while True:
        chunk = list(itertools.islice(it, n))
        if not chunk: break
        yield chunk

color_cycle = ["c1","c2","c3","c4","c5"]
color_idx = 0

for row in chunked(LETTERS, 3):
    cols = st.columns(3, vertical_alignment="top")
    for col, (ltr, name) in zip(cols, row):
        with col:
            # البلاطة نفسها زرّ — نستخدم form لضبط النقر
            with st.form(f"tile_{ltr}"):
                st.markdown(f'<div class="tile {color_cycle[color_idx%5]}">{ltr}</div>', unsafe_allow_html=True)
                color_idx += 1
                clicked = st.form_submit_button("", use_container_width=True)
                if clicked:
                    st.session_state["chosen"] = (ltr, name)
                    # نطق داخل البلاطة نفسها
                    try:
                        tile_autoplay(tts_bytes(name, slow=True))
                    except Exception:
                        pass

# ========= أمثلة الحرف المختار =========
chosen = st.session_state.get("chosen")
if chosen:
    ltr, name = chosen
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### الحرف: **{ltr}** — *{name}*")
    ex = EX.get(ltr, {})
    st.markdown('<div class="examples">', unsafe_allow_html=True)
    st.markdown(
        f"<span>🐾 <b>حيوان:</b> {ex.get('animal','—')}</span>"
        f"<span>🐦 <b>طير:</b> {ex.get('bird','—')}</span>"
        f"<span>🍎 <b>فاكهة:</b> {ex.get('fruit','—')}</span>"
        f"<span>🥕 <b>خضار:</b> {ex.get('veg','—')}</span>"
        f"<span>👤 <b>اسم شخص:</b> {ex.get('name','—')}</span>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ========= اختبار الجملة + نقاط =========
st.markdown("---")
st.subheader("🧪 اختبار: كوّن جملة وسنقرؤها لك")
sent = st.text_input("اكتب جملة قصيرة:", placeholder="مثال: أنا أحب التفاح 🍎")
colA, colB, colC = st.columns([1,1,2], vertical_alignment="center")
with colA:
    read = st.button("🔊 اقرأ الجملة")
with colB:
    st.markdown(f"<span class='score-badge'>نقاطك: {st.session_state['points']}</span>", unsafe_allow_html=True)

if read:
    if sent.strip():
        # نطق الجملة
        try:
            audio = tts_bytes(sent, slow=False)
            # نشغّل الصوت (تحت زر القراءة)
            b64 = base64.b64encode(audio).decode()
            st.markdown(
                f"""<audio autoplay>
                       <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>""",
                unsafe_allow_html=True
            )
        except Exception:
            st.info("تعذّر تشغيل الصوت.")
        # تحفيز بصري + صوت مدح
        st.balloons()
        try:
            praise = tts_bytes("أحسنت! ممتاز!", slow=False)
            b64p = base64.b64encode(praise).decode()
            st.markdown(
                f"""<audio autoplay>
                       <source src="data:audio/mp3;base64,{b64p}" type="audio/mp3">
                    </audio>""",
                unsafe_allow_html=True
            )
        except Exception:
            pass
        # نقاط
        st.session_state["points"] += 10
        st.toast("🎉 رائع! +10 نقاط", icon="🎯")
    else:
        st.warning("اكتب جملة أولاً.")
