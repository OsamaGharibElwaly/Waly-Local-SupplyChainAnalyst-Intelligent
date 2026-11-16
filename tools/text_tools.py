"""Text utilities — tokenization, keyword extraction, sentiment lexicon."""
import re
from collections import Counter

STOP = set("""a an the and or but if then of to in on at for with by from is are was
were be been being this that these those it its as not no yes i you we they he she""".split())

POSITIVE = {"good","great","excellent","satisfied","fast","reliable","perfect","happy",
            "prompt","amazing","recommend","quality","love","outstanding","superb",
            "efficient","helpful","responsive","smooth"}
NEGATIVE = {"bad","late","delay","poor","broken","damaged","slow","missing","terrible",
            "worst","angry","refund","problem","issue","defective","unacceptable",
            "rude","lost","cancel","fail","failed","frustrating"}


def tokenize(text):
    if not isinstance(text, str):
        return []
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 2]


def sentiment_score(text):
    """Lexicon sentiment: (pos-neg)/total in [-1, 1]."""
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    pos = sum(1 for w in tokens if w in POSITIVE)
    neg = sum(1 for w in tokens if w in NEGATIVE)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 3)


def keywords(series, top_k=15):
    counter = Counter()
    for txt in series.dropna().astype(str):
        counter.update(tokenize(txt))
    return counter.most_common(top_k)


def flag_text(text):
    """Return list of issues found in text."""
    if not isinstance(text, str):
        return []
    t = text.lower()
    flags = []
    if any(w in t for w in ("late", "delay", "delayed")): flags.append("LATE")
    if "damag" in t: flags.append("DAMAGED")
    if "defect" in t: flags.append("DEFECT")
    if "refund" in t: flags.append("REFUND")
    if "missing" in t: flags.append("MISSING")
    if "broken" in t: flags.append("BROKEN")
    return flags
