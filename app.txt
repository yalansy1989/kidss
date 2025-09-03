# -*- coding: utf-8 -*-
# واجبات-بوت (ابتدائي) — واجهة Streamlit
# Kid Mode + Parent Mode + بحث ويب + حل رياضيات محلي
import re, html, requests
import streamlit as st
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from sympy import sympify
from sympy.core.sympify import SympifyError

st.set_page_config(page_title="واجبات-بوت (ابتدائي)", page_icon="🧠", layout="centered")

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# ---------------- أدوات مساعدة ----------------
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
        return text[:12000]
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

def solve(question_raw: str):
    q_norm = normalize_question(question_raw)
    q, options = parse_options(q_norm)

    # 1) رياضيات محلياً
    val, steps = try_solve_math(q)
    if val is not None and options is None:
        return {
            "answer": val, "confidence": 95, "method": "حساب مباشر (محلي)",
            "explain": steps, "sources": []
        }

    # 2) بحث ويب
    serp = ddg_search(q, n=8)
    if not serp:
        return {
            "answer": "لم أعثر على إجابة موثوقة.",
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
        return {
            "answer": html.unescape(top.get("body", "لم أعثر على إجابة.")),
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
            "answer": pick, "confidence": min(95, max(50, int(score))),
            "method": "بحث ويب + ترجيح خيارات",
            "explain": explain, "sources": sources[:4]
        }

    return {
        "answer": sent if sent else "لم أعثر على جملة حاسمة، راجع المصادر.",
        "confidence": min(95, max(45, int(score))),
        "method": "بحث ويب + استخراج جملة",
        "explain": "اخترنا الجملة الأعلى تشابهاً مع السؤال.",
        "sources": sources[:4]
    }

# ---------------- واجهة Streamlit ----------------
st.markdown("<h1 style='text-align:center'>🧠 واجبات-بوت (ابتدائي)</h1>", unsafe_allow_html=True)
mode = st.radio("الوضع:", ["👧 وضع الأطفال (مبسّط)", "🧑‍💼 وضع وليّ الأمر (تفصيلي)"], index=0)

st.caption("ملاحظة: الأداة للتعلّم لا للغش. الفكرة نشرح *كيف* وصلنا للحل.")

with st.form("hw_form"):
    st.write("أدخل السؤال (يمكن استخدام الاختيار من متعدد بهذه الصيغة: السؤال | خيار1 | خيار2 | خيار3 ...)")
    q = st.text_area("سؤال الطالب", height=120, placeholder="مثال: ما عاصمة فرنسا؟ | برلين | مدريد | باريس | روما")
    submitted = st.form_submit_button("حل ✅")

if submitted and q.strip():
    with st.spinner("نبحث ونحل السؤال…"):
        result = solve(q)

    # بطاقة الإجابة
    st.success(f"**الإجابة المقترحة:** {result['answer']}")
    st.metric("نسبة الثقة", f"{result['confidence']}%")
    st.info(f"الطريقة: {result['method']}")

    # وضع ولي الأمر: إظهار الشرح + المصادر
    if mode.endswith("تفصيلي"):
        if result.get("explain"):
            st.write("**الشرح:**")
            st.code(result["explain"], language="text")
        if result.get("sources"):
            st.divider()
            st.write("**المصادر (للمراجعة):**")
            for s in result["sources"]:
                if s.get("url"):
                    st.markdown(f"- [{s.get('title','مصدر')}]({s['url']})")
                else:
                    st.markdown(f"- {s.get('title','مصدر')}")

# فوتر تربوي لطيف
st.caption("💡 تلميح تربوي: اسأل طفلك يشرح لك خطوة الحساب بصوته قبل الضغط على 'حل'.")
