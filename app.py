# -*- coding: utf-8 -*-
# تعليم الحروف العربية — شبكة 3xN + نطق على نفس البلاطة + أمثلة + اختبار جملة بالصوت والمؤثرات + نقاط
import json
import streamlit as st
import textwrap

st.set_page_config(page_title="تعليم الحروف العربية", page_icon="🔤", layout="wide")

# ---------------- بيانات الحروف والأمثلة ----------------
LETTERS = [
    ("أ","ألف"),("ب","باء"),("ت","تاء"),("ث","ثاء"),("ج","جيم"),
    ("ح","حاء"),("خ","خاء"),("د","دال"),("ذ","ذال"),
    ("ر","راء"),("ز","زاي"),("س","سين"),("ش","شين"),
    ("ص","صاد"),("ض","ضاد"),("ط","طاء"),("ظ","ظاء"),
    ("ع","عين"),("غ","غين"),("ف","فاء"),("ق","قاف"),
    ("ك","كاف"),("ل","لام"),("م","ميم"),("ن","نون"),
    ("هـ","هاء"),("و","واو"),("ي","ياء")
]
EX = {
 "أ":{"animal":"أسد 🦁","bird":"أوز 🪿","fruit":"أناناس 🍍","veg":"أرضي شوكي 🌿","name":"أحمد"},
 "ب":{"animal":"بقرة 🐄","bird":"بط 🦆","fruit":"برتقال 🍊","veg":"باذنجان 🍆","name":"بسام"},
 "ت":{"animal":"تمساح 🐊","bird":"ترغل 🐦","fruit":"تفاح 🍎","veg":"تُرمس 🌱","name":"تيم"},
 "ث":{"animal":"ثعلب 🦊","bird":"طائر 🐦","fruit":"ثوم 🧄","veg":"ثوم 🧄","name":"ثائر"},
 "ج":{"animal":"جمل 🐫","bird":"طائر جارح 🦅","fruit":"جوافة 🍈","veg":"جزر 🥕","name":"جهاد"},
 "ح":{"animal":"حصان 🐎","bird":"حمامة 🕊️","fruit":"حبحب 🍉","veg":"حلبة 🌿","name":"حسن"},
 "خ":{"animal":"خروف 🐑","bird":"خُضيري 🐦","fruit":"خوخ 🍑","veg":"خس 🥬","name":"خالد"},
 "د":{"animal":"دب 🐻","bird":"دجاجة 🐔","fruit":"دراق 🍑","veg":"دُباء 🎃","name":"دلال"},
 "ذ":{"animal":"ذئب 🐺","bird":"ذُعَرَى 🐦","fruit":"ذرة 🌽","veg":"ذرة 🌽","name":"ذكرى"},
 "ر":{"animal":"راكون 🦝","bird":"رخمة 🦅","fruit":"رمان 🍎","veg":"رجلة 🌿","name":"ريم"},
 "ز":{"animal":"زرافة 🦒","bird":"زرزور 🐦","fruit":"زيتون 🫒","veg":"زنجبيل 🫚","name":"زياد"},
 "س":{"animal":"سنجاب 🐿️","bird":"سنونو 🐦","fruit":"سفرجل 🍐","veg":"سبانخ 🥬","name":"سارة"},
 "ش":{"animal":"شمبانزي 🐒","bird":"شحرور 🐦","fruit":"شمام 🍈","veg":"شمندر 🥬","name":"شادي"},
 "ص":{"animal":"صقر 🦅","bird":"صفّار 🐦","fruit":"صبير 🌵","veg":"صنوبر 🌰","name":"صبا"},
 "ض":{"animal":"ضفدع 🐸","bird":"طائر 🐦","fruit":"—","veg":"ضِرِّيس 🌿","name":"ضياء"},
 "ط":{"animal":"طاووس 🦚","bird":"طيطوي 🐦","fruit":"طماطم 🍅","veg":"طماطم 🍅","name":"طارق"},
 "ظ":{"animal":"ظبي 🦌","bird":"ظُليم 🐦","fruit":"—","veg":"—","name":"ظافر"},
 "ع":{"animal":"عقاب 🦅","bird":"عندليب 🐦","fruit":"عنب 🍇","veg":"عرقسوس 🌿","name":"علي"},
 "غ":{"animal":"غزال 🦌","bird":"غراب 🐦","fruit":"غوجة/خوخ 🍑","veg":"غار 🌿","name":"غادة"},
 "ف":{"animal":"فهد 🐆","bird":"فلامنغو 🦩","fruit":"فراولة 🍓","veg":"فلفل 🌶️","name":"فارس"},
 "ق":{"animal":"قنفذ 🦔","bird":"قوق/واق 🐦","fruit":"قِشطه 🍈","veg":"قرنبيط 🥦","name":"قصي"},
 "ك":{"animal":"كلب 🐶","bird":"كناري 🐤","fruit":"كمثرى 🍐","veg":"كرفس 🌿","name":"كريم"},
 "ل":{"animal":"لاما 🦙","bird":"لقلاق 🐦","fruit":"ليمون 🍋","veg":"لفت 🥬","name":"لينا"},
 "م":{"animal":"ماعز 🐐","bird":"بلبل 🐦","fruit":"مانجو 🥭","veg":"ملفوف 🥬","name":"محمد"},
 "ن":{"animal":"نمر 🐅","bird":"نعامة 🐦","fruit":"نبق 🍏","veg":"نعناع 🌿","name":"نادر"},
 "هـ":{"animal":"هدهد 🐦","bird":"هدهد 🐦","fruit":"هندباء 🌿","veg":"هندباء 🌿","name":"هالة"},
 "و":{"animal":"وحيد القرن 🦏","bird":"إوز 🪿","fruit":"ورد (ثمر) 🌹","veg":"ورق عنب 🌿","name":"وسيم"},
 "ي":{"animal":"يمامة 🕊️","bird":"يمامة 🕊️","fruit":"يوسفي 🍊","veg":"يقطين 🎃","name":"يوسف"}
}

# ---------------- واجهة مخصّصة داخل مكوّن HTML/JS ----------------
from streamlit.components.v1 import html

html_css_js = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8" />
<style>
:root {{
  --bg1:#fff9f2; --bg2:#f3fffe; --bg3:#f4f7ff;
  --tile-b:#e9eef5; --shadow:rgba(0,0,0,.07);
}}
body {{ margin:0; font-family: system-ui, -apple-system, "Segoe UI", "Noto Sans Arabic", Tahoma, Arial; }}
.wrapper {{
  background: linear-gradient(135deg,var(--bg1) 0%, var(--bg2) 55%, var(--bg3) 100%);
  min-height:100vh; padding: 8px 10px 40px;
}}
.title {{ text-align:center; font-weight:900; font-size:2.0rem; margin:.4rem 0 .6rem }}
.grid {{
  display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; max-width:720px; margin:0 auto 12px;
}}
.tile {{
  display:flex; align-items:center; justify-content:center; position:relative;
  height:108px; border-radius:18px; font-size:2.6rem; font-weight:900;
  border:1px solid var(--tile-b); user-select:none; cursor:pointer;
  box-shadow:0 12px 26px var(--shadow); transition:transform .08s ease;
}}
.tile:active {{ transform:scale(.98); }}
.c1{{background:#ffe9ec}} .c2{{background:#e7f4ff}} .c3{{background:#eaffe9}} .c4{{background:#fff6d9}} .c5{{background:#f4e9ff}}
.examples {{
  max-width:720px; margin:10px auto 0; background:#ffffffdd; border:1px solid #eef1f6;
  border-radius:18px; padding:14px 16px; box-shadow:0 10px 26px var(--shadow); line-height:1.9;
}}
.examples h3 {{ margin:0 0 6px 0; }}
.examples .row span {{ display:block; }}
.scorebar {{ max-width:720px; margin:10px auto; display:flex; justify-content:space-between; align-items:center; }}
.score {{
  background:#e9f8f1; border:1px solid #cdeede; padding:6px 12px; border-radius:12px; font-weight:800;
}}
.testbox {{
  max-width:720px; margin:8px auto; background:#ffffffdd; border:1px solid #eef1f6; border-radius:18px;
  padding:14px 16px; box-shadow:0 10px 26px var(--shadow);
}}
textarea {{
  width:100%; border:1px solid #e0e5ee; border-radius:12px; padding:10px; font-size:1.05rem; resize:vertical;
}}
.button {{
  background:#2f7bf6; color:#fff; border:none; border-radius:12px; padding:10px 14px; cursor:pointer; font-weight:800;
}}
.button:active {{ transform: translateY(1px); }}
@media (max-width:520px){{
  .tile{{ height:90px; font-size:2.2rem }}
}}
</style>
</head>
<body>
<div class="wrapper">
  <div class="title">🔤 تعليم الحروف العربية</div>

  <div id="grid" class="grid"></div>

  <div id="examples" class="examples" style="display:none">
    <h3 id="ex-title">الحرف:</h3>
    <div class="row">
      <span id="ex-animal"></span>
      <span id="ex-bird"></span>
      <span id="ex-fruit"></span>
      <span id="ex-veg"></span>
      <span id="ex-name"></span>
    </div>
  </div>

  <div class="scorebar">
    <div class="score" id="score">نقاطك: 0</div>
  </div>

  <div class="testbox">
    <label>🧪 اختبار: اكتب جملة وسيتم نطقها</label>
    <textarea id="sentence" rows="2" placeholder="مثال: أنا أحب التفاح 🍎"></textarea>
    <div style="margin-top:8px; display:flex; gap:10px">
      <button class="button" id="speakBtn">🔊 اقرأ الجملة</button>
      <small>سيتم تشغيل المدح بعد انتهاء القراءة، وتُحتسب نقاط فقط إذا غيّرت الجملة.</small>
    </div>
  </div>
</div>

<script>
const LETTERS = {json_letters};
const EX = {json_examples};

// ====== شبكة الحروف (3 في الصف) ======
const grid = document.getElementById('grid');
const colors = ['c1','c2','c3','c4','c5'];
LETTERS.forEach((item, idx) => {{
  const [ltr, name] = item;
  const tile = document.createElement('div');
  tile.className = 'tile ' + colors[idx % 5];
  tile.textContent = ltr;

  // نطق على نفس البلاطة
  tile.addEventListener('click', () => {{
    speakNow(name);             // نطق فوري لاسم الحرف (فصيح)
    showExamples(ltr, name);    // إظهار الأمثلة
    // تأثير بصري خفيف
    tile.style.transform = 'scale(0.98)';
    setTimeout(() => tile.style.transform = '', 120);
  }});

  grid.appendChild(tile);
}});

// ====== الأمثلة ======
function showExamples(ltr, name) {{
  const box = document.getElementById('examples');
  const title = document.getElementById('ex-title');
  const ex = EX[ltr] || {{}};
  title.textContent = `الحرف: ${ltr} — ${name}`;
  document.getElementById('ex-animal').textContent = `🐾 حيوان: ${ex.animal || '—'}`;
  document.getElementById('ex-bird').textContent   = `🐦 طير: ${ex.bird || '—'}`;
  document.getElementById('ex-fruit').textContent  = `🍎 فاكهة: ${ex.fruit || '—'}`;
  document.getElementById('ex-veg').textContent    = `🥕 خضار: ${ex.veg || '—'}`;
  document.getElementById('ex-name').textContent   = `👤 اسم شخص: ${ex.name || '—'}`;
  box.style.display = 'block';
  box.scrollIntoView({{behavior:'smooth', block:'nearest'}});
}}

// ====== نطق عربي فصيح باستخدام Web Speech API ======
function speakNow(text) {{
  try {{
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    // أصوات عربية متوفرة عادة: "ar-SA", "ar-XA"
    u.lang = "ar-SA";
    u.rate = 0.9;   // أبطأ قليلاً للوضوح
    u.pitch = 1.0;
    window.speechSynthesis.speak(u);
  }} catch(e) {{ console.log(e); }}
}}

// ====== اختبار الجملة: قراءة -> عند الانتهاء تشغيل المدح والتأثيرات ======
const scoreEl = document.getElementById('score');
const input = document.getElementById('sentence');
const btn = document.getElementById('speakBtn');
let lastSentence = localStorage.getItem('lastSentence') || '';
let points = parseInt(localStorage.getItem('points') || '0', 10);
updateScore();

btn.addEventListener('click', () => {{
  const text = (input.value || '').trim();
  if (!text) return;

  // 1) أوقف أي نطق سابق
  window.speechSynthesis.cancel();

  // 2) انطق الجملة أولاً
  const u1 = new SpeechSynthesisUtterance(text);
  u1.lang = "ar-SA"; u1.rate = 1.0; u1.pitch = 1.0;

  // 3) بعد الانتهاء: مدح + مؤثرات
  u1.onend = () => {{
    playApplauseAndPops();  // مؤثرات
    const u2 = new SpeechSynthesisUtterance("أحسنت! ممتاز!");
    u2.lang = "ar-SA"; u2.rate = 1.0; u2.pitch = 1.0;
    window.speechSynthesis.speak(u2);

    // نقاط تُحتسب فقط إذا تغيّرت الجملة
    if (text && text !== lastSentence) {{
      points += 10;
      lastSentence = text;
      localStorage.setItem('lastSentence', lastSentence);
      localStorage.setItem('points', String(points));
      updateScore();
    }}
  }};

  window.speechSynthesis.speak(u1);
}});

function updateScore() {{
  scoreEl.textContent = "نقاطك: " + points;
}}

// ====== مؤثرات "تصفيق + فرقعات" (WebAudio توليدياً) ======
function playApplauseAndPops() {{
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  // تصفيق: نبضات ضوضاء قصيرة متعدّدة
  for (let i=0; i<14; i++) {{
    const start = ctx.currentTime + 0.05 * i;
    noiseBurst(ctx, start, 0.08, 0.2);
  }}
  // فرقعات: نغمات قصيرة متفاوتة
  for (let i=0; i<6; i++) {{
    const t = ctx.currentTime + 0.9 + i*0.08;
    pop(ctx, t, 300 + Math.random()*600);
  }}
  // إيقاف بعد ثانيتين لتوفير البطارية
  setTimeout(() => ctx.close(), 2200);
}}

function noiseBurst(ctx, when, duration, gainVal) {{
  const bufferSize = ctx.sampleRate * duration;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i=0; i<bufferSize; i++) {{ data[i] = (Math.random()*2-1) * (1 - i/bufferSize); }}
  const src = ctx.createBufferSource(); src.buffer = buffer;
  const gain = ctx.createGain(); gain.gain.value = gainVal;
  src.connect(gain).connect(ctx.destination);
  src.start(when); src.stop(when + duration);
}}

function pop(ctx, when, freq) {{
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = 'sine'; osc.frequency.setValueAtTime(freq, when);
  gain.gain.setValueAtTime(0.0001, when);
  gain.gain.exponentialRampToValueAtTime(0.4, when + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.0001, when + 0.12);
  osc.connect(gain).connect(ctx.destination);
  osc.start(when); osc.stop(when + 0.15);
}}
</script>
</body>
</html>
"""

# حقن البيانات في الـ HTML
html_page = html_css_js.replace(
    "{json_letters}", json.dumps(LETTERS, ensure_ascii=False)
).replace(
    "{json_examples}", json.dumps(EX, ensure_ascii=False)
)

# نعرض المكوّن (ارتفاع كافي، يتكيّف مع الجوال)
st.components.v1.html(html_page, height=900, scrolling=True)
