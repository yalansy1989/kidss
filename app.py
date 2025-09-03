# -*- coding: utf-8 -*-
# المساعد الشخصي — تعليم الحروف العربية فقط (كبيرة + نطق تلقائي + أمثلة)

import io, base64
import streamlit as st
from gtts import gTTS

st.set_page_config(page_title="تعليم الحروف العربية", page_icon="🔤", layout="wide")

# ---------- ستايل طفولي وبلاطات كبيرة ----------
st.markdown("""
<style>
html, body { direction: rtl; }
.stApp {
  background: linear-gradient(135deg,#fff9f2 0%, #f3fffe 55%, #f4f7ff 100%);
  background-attachment: fixed;
}
.block-container { padding-top: 1rem; }
.title{ text-align:center;font-weight:900;font-size:2.2rem; margin-bottom:.6rem }
.grid { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; }
.tile {
  display:flex; align-items:center; justify-content:center;
  width:92px; height:92px; border-radius:18px; font-size:2.2rem; font-weight:900;
  border:1px solid #e9eef5; user-select:none; cursor:pointer;
  box-shadow:0 10px 22px rgba(0,0,0,.06); transition:.12s transform ease;
}
.tile:active { transform: scale(.98); }
.c1{background:#ffe9ec;} .c2{background:#e7f4ff;} .c3{background:#eaffe9;}
.c4{background:#fff6d9;} .c5{background:#f4e9ff;}
.card {
  background:#ffffffdd; border:1px solid #eef1f6; border-radius:18px;
  padding:16px 18px; box-shadow:0 10px 26px rgba(0,0,0,.06);
}
.examples b{display:inline-block; width:92px}
.hidden-audio {height:0; overflow:hidden}
@media (max-width: 640px){
  .tile{ width:78px; height:78px; font-size:1.9rem }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔤 تعليم الحروف العربية</div>', unsafe_allow_html=True)
st.caption("اضغط أي حرف لسماع اسمه فورًا، وستظهر أمثلة تبدأ بنفس الحرف.")

# ---------- TTS: نطق واضح مع سكون ----------
@st.cache_resource(show_spinner=False)
def tts_bytes(text: str) -> bytes:
    # نستخدم أسماء الحروف بصيغة مشكّلة مع سكون لنُطق واضح
    tts = gTTS(text=text, lang="ar", slow=True)  # slow=True لزيادة الوضوح للأطفال
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

def autoplay(audio_bytes: bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f"""<audio class="hidden-audio" autoplay>
              <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>""",
        unsafe_allow_html=True
    )

# ---------- بيانات الحروف + أمثلة ----------
LETTERS = [
    ("أ","ألفْ"),("ب","باءْ"),("ت","تاءْ"),("ث","ثاءْ"),("ج","جيمْ"),("ح","حاءْ"),("خ","خاءْ"),
    ("د","دالْ"),("ذ","ذالْ"),("ر","راءْ"),("ز","زايْ"),("س","سينْ"),("ش","شينْ"),
    ("ص","صادْ"),("ض","ضادْ"),("ط","طاءْ"),("ظ","ظاءْ"),("ع","عينْ"),("غ","غينْ"),
    ("ف","فاءْ"),("ق","قافْ"),("ك","كافْ"),("ل","لامْ"),("م","ميمْ"),("ن","نونْ"),
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

# ---------- حالة التحديد ----------
if "chosen" not in st.session_state:
    st.session_state["chosen"] = None

# ---------- شبكة الحروف (بلاطات كبيرة فقط) ----------
st.write("")  # مسافة صغيرة
st.markdown('<div class="grid">', unsafe_allow_html=True)

for i, (ltr, name) in enumerate(LETTERS):
    color = f"c{(i%5)+1}"
    # نستخدم form لكل بلاطة للحصول على حدث click نظيف
    with st.form(f"f_{i}"):
        st.markdown(f'<div class="tile {color}">{ltr}</div>', unsafe_allow_html=True)
        clicked = st.form_submit_button("", use_container_width=True)
        if clicked:
            st.session_state["chosen"] = (ltr, name)
            # تشغيل الصوت فورًا
            try:
                autoplay(tts_bytes(name))
            except Exception:
                pass
st.markdown('</div>', unsafe_allow_html=True)

# ---------- عرض الأمثلة بعد الضغط ----------
chosen = st.session_state.get("chosen")
st.write("")  # مسافة
if chosen:
    ltr, name = chosen
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1,2], vertical_alignment="top")
        with col1:
            st.markdown(f"### الحرف: **{ltr}** — *{name}*")
        with col2:
            ex = EX.get(ltr, {})
            st.markdown('<div class="examples">', unsafe_allow_html=True)
            st.markdown(
                f"**🐾 حيوان:** {ex.get('animal','—')}  \n"
                f"**🐦 طير:** {ex.get('bird','—')}  \n"
                f"**🍎 فاكهة:** {ex.get('fruit','—')}  \n"
                f"**🥕 خضار:** {ex.get('veg','—')}  \n"
                f"**👤 اسم شخص:** {ex.get('name','—')}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- فوتر ----------
st.caption("نطق فصيح بأسماء الحروف مع سكون. لمزيد من الدقّة يمكن لاحقًا تبديل محرك الصوت بمحرك احترافي.")
