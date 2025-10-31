import re
PRICE_RE = re.compile(r"(?:Rs\.?|[$€£₩])\s?\d[\d.,]*", re.I)

"""
Extract price-like string from a page
"""
def extract_price_from_scope(scope):
    # Go with places where prices are likely to be shown (to avoid matching numbers like page numbers)
    for sel in ("h2", ".price", ".product-information span", "span"):
        loc = scope.locator(sel).first
        if loc.count():
            txt = loc.inner_text().strip()
            m = PRICE_RE.search(txt)
            if m:
                return m.group(0)
    # Scan all texts if above doesn't work
    try:
        all_txt = " | ".join(scope.locator("*").all_inner_texts())
        m = PRICE_RE.search(all_txt)
        if m:
            return m.group(0)
    except Exception:
        pass
    return None