#!/usr/bin/env python3
"""Clean landing HTML files per AEE workflow."""

import re
from pathlib import Path

FORM_LOCALE = {
    "RO": {
        "code": "RO",
        "name_label": "Numele dvs.:",
        "name_placeholder": "Numele dumneavoastră",
        "phone_label": "Numărul dvs. de telefon mobil:",
        "phone_placeholder": "Numărul dumneavoastră de telefon",
        "submit": "OBȚINE",
        "form_class": "order__body",
    },
    "PL": {
        "code": "PL",
        "name_label": "Imię i nazwisko:",
        "name_placeholder": "Imię i nazwisko*",
        "phone_label": "Numer telefonu:",
        "phone_placeholder": "512 345 678",
        "submit": "Zamów Detoxil water",
        "form_class": "one_order_form",
    },
    "IT": {
        "code": "IT",
        "name_label": "Nome e cognome:",
        "name_placeholder": "Nome e cognome*",
        "phone_label": "Numero di telefono:",
        "phone_placeholder": "312 345 6789",
        "submit": "Chiedere Detoxil Water",
        "form_class": "one_order_form",
    },
    "LT": {
        "code": "LT",
        "name_label": "Vardas:",
        "name_placeholder": "Įveskite savo vardą",
        "phone_label": "Telefono numeris:",
        "phone_placeholder": "Įveskite savo telefono numerį",
        "submit": "UŽSAKYTI CYSTOLAX",
        "form_class": "x_order_form form",
    },
}

PIXEL_PATTERNS = re.compile(
    r"success-php|fbevents|fbq\(|facebook\.com/tr|connect\.facebook|"
    r"height=[\"']1[\"'][^>]*width=[\"']1[\"']|width=[\"']1[\"'][^>]*height=[\"']1[\"']",
    re.I,
)

BAD_SCRIPT_PATTERNS = re.compile(
    r"vitBack|domonet|domon[^e]|history\.replaceState|history\.pushState|"
    r"document\.location\.hash|window\.location\.href|fbevents|fbq\(|"
    r"PushPigeonSDK|pigeon-sdk|clickline\.org|pingKT|_update_tokens|"
    r"GenerateCta|mod_pagespeed|TypeIt|newsFrame|showcaseFrame|"
    r"scroll_to_form|phone_strict|trk-uri|campaignkey|"
    r"new Image\(\)|success-php|scrollIntoView|addEventListener\([\"']click|"
    r"\$\([\"']a[\"']\)|to_form|vitBack|TSL_PARAGRAPH_SELECTOR|"
    r"querySelectorAll\([\"']a,\s*button",
    re.I,
)

KEEP_SCRIPT_PATTERNS = re.compile(
    r"function\s+dtime_nums|function\s+fdateTwoDigits|function\s+fdate\b|"
    r"function\s+updateTimer|setDate\(|getDate\(|getMonth\(|getFullYear\(|"
    r"getElementById\([\"'](?:h|m|s|hours|minutes|seconds|orderMinute|orderSecond|cystolax-date)|"
    r"querySelector\([\"']\.source-info|currentDate\s*=\s*new Date|formattedDate|"
    r"cystolaxFormatted|cystolaxNow|textContent\s*=|document\.write\(|"
    r"padStart\(|getTime\(\)",
    re.I,
)


def build_form_inner(locale: dict) -> str:
    code = locale["code"]
    return f"""            <input type="hidden" name="SUB_4" value="{{ad_name}}">
            <input type="hidden" name="LI" value="{{landing_id}}">
            <input type="hidden" id="utc-time-input" name="time" value="{{date:Y-m-d H:i:s,UTC}}">
            <input type="hidden" id="up" name="UP" value="{{utm_placement}}">
            <input type="hidden" name="subid" value="{{subid}}">
            <input type="hidden" name="utm_campaign" value="{{utm_campaign}}">
            <input type="hidden" name="subhype" value="{{subhype}}">
            <input type="hidden" name="pixel" value="{{pixel}}">
            <input type="hidden" name="language" value="{{language}}">
            <input type="hidden" name="pod" value="{{pod}}">
            <input type="hidden" name="offer_id" value="{{offer_id}}">
            <div class="order_form_pole">
                <label>{locale['name_label']}</label>
                <input class="name-black" placeholder="{locale['name_placeholder']}" type="text" minlength="2" name="name" required>
            </div>
            <div class="order_form_pole">
                <label>{locale['phone_label']}</label>
                <input class="phone-black" type="tel" name="phone" required placeholder="{locale['phone_placeholder']}" code="{code}">
            </div>
            <div style="margin-bottom: 20px; display: flex; flex-direction: column; align-items: center;">
                <button class="submit-btn" type="submit">{locale['submit']}</button>
            </div>
            <div class="ring-loading"></div>"""


def replace_forms(html: str, locale: dict) -> str:
    inner = build_form_inner(locale)
    form_class = locale["form_class"]

    pattern = re.compile(
        r"<form\b[^>]*\bid=[\"']order_form[\"'][^>]*>.*?</form>",
        re.I | re.S,
    )

    def replacer(match: re.Match) -> str:
        tag = match.group(0)
        open_tag = re.match(r"<form\b[^>]*>", tag, re.I).group(0)
        action_match = re.search(r'\baction=(["\'])(.*?)\1', open_tag, re.I)
        method_match = re.search(r'\bmethod=(["\'])(.*?)\1', open_tag, re.I)
        action = action_match.group(2) if action_match else ""
        method = method_match.group(2) if method_match else "post"

        if 'action=""' in open_tag or re.search(r"\baction\s+method=", open_tag, re.I):
            return f'<form action method="{method}" class="{form_class}" id="order_form">\n{inner}\n</form>'

        action_attr = f'action="{action}"' if action else "action"
        return (
            f'<form id="order_form" class="{form_class}" {action_attr} method="{method}">\n'
            f"{inner}\n</form>"
        )

    html = pattern.sub(replacer, html, count=1)

    comment_pattern = re.compile(
        r"<form\b[^>]*\bid=[\"']comment_form[\"'][^>]*>.*?</form>",
        re.I | re.S,
    )
    comment_inner = """            <input type="hidden" name="subid" value="{subid}">
            <input type="hidden" name="pixel" value="{pixel}">
            <div class="order_form_pole">
                <input type="tel" name="phone" required placeholder="Numărul de telefon">
            </div>
            <button type="submit">Trimite</button>"""
    html = comment_pattern.sub(
        f'<form action method="POST" id="comment_form">\n{comment_inner}\n</form>',
        html,
        count=1,
    )
    return html


def should_keep_script(content: str) -> bool:
    if PIXEL_PATTERNS.search(content):
        return False
    if BAD_SCRIPT_PATTERNS.search(content):
        return False
    if KEEP_SCRIPT_PATTERNS.search(content):
        return True
    if re.search(r"fdateTwoDigits\s*\(|dtime_nums\s*\(", content):
        return True
    return False


def clean_scripts(html: str) -> str:
    html = re.sub(
        r"<script[^>]*\bsrc=[\"'][^\"']+[\"'][^>]*>\s*</script>",
        "",
        html,
        flags=re.I,
    )

    def inline_replacer(match: re.Match) -> str:
        body = match.group(2)
        if should_keep_script(body):
            return match.group(0)
        return ""

    html = re.sub(
        r"<script(\s[^>]*)?>(.*?)</script>",
        inline_replacer,
        html,
        flags=re.I | re.S,
    )
    return html


def clean_tag_attrs(html: str) -> str:
    def tag_replacer(match: re.Match) -> str:
        tag = match.group(0)
        tag = re.sub(r"\s+onclick=(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", "", tag, flags=re.I)
        tag = re.sub(r"\s+target(?:=(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?", "", tag, flags=re.I)
        return tag

    return re.sub(r"<[^>]+>", tag_replacer, html)


def clean_html(content: str, locale_key: str) -> str:
    html = content
    locale = FORM_LOCALE[locale_key]

    html = clean_tag_attrs(html)

    html = re.sub(
        r"(<a\b[^>]*?\s)href=(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
        r'\1href="#"',
        html,
        flags=re.I,
    )

    html = re.sub(
        r"(<link\b(?:(?!>).)*\brel=[\"']canonical[\"'])(?:(?!>).)*\bhref=(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
        r'\1 href="#"',
        html,
        flags=re.I,
    )
    html = re.sub(
        r"(<link\b(?:(?!>).)*\bhref=(?:\"[^\"]*\"|'[^']*'|[^\s>]+))(?:(?!>).)*\brel=[\"']canonical[\"']",
        r'\1 href="#" rel="canonical"',
        html,
        flags=re.I,
    )

    while re.search(r"<html\b[^>]*\sdata-", html, re.I):
        html = re.sub(
            r"(<html\b[^>]*?)\s+data-[a-z0-9_-]+(?:=(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?",
            r"\1",
            html,
            flags=re.I,
        )

    html = re.sub(
        r"<meta[^>]*(?:name=[\"']referrer[\"']|http-equiv=[\"']Content-Security-Policy[\"']|name=[\"']policy[\"'])[^>]*>",
        "",
        html,
        flags=re.I,
    )

    html = re.sub(r"<noscript[^>]*>.*?</noscript>", "", html, flags=re.I | re.S)
    html = re.sub(
        r"<img[^>]*(?:height=[\"']1[\"'][^>]*width=[\"']1[\"']|width=[\"']1[\"'][^>]*height=[\"']1[\"'])[^>]*>",
        "",
        html,
        flags=re.I,
    )
    html = re.sub(r"<iframe[^>]*>.*?</iframe>", "", html, flags=re.I | re.S)
    html = re.sub(r"<embed[^>]*class=[\"']search-img[\"'][^>]*>", "", html, flags=re.I)

    html = clean_scripts(html)
    html = replace_forms(html, locale)

    html = html.replace("&amp;", "&")
    html = html.replace("&nbsp; &nbsp;", " ")
    html = html.replace("&nbsp;&nbsp;", " ")
    html = html.replace("&quot;&quot;", "&quot;")
    html = html.replace("\\u200b\\u200b", " ")

    html = re.sub(
        r"(?:\s*<script[^>]*>.*?</script>)+\s*(?=</body>)",
        "\n",
        html,
        flags=re.I | re.S,
    )

    if "integrations/js/utils.js" not in html:
        html = re.sub(
            r"</body>",
            '\n<script src="integrations/js/utils.js"></script>\n</body>',
            html,
            flags=re.I,
        )

    return html


def main():
    files = ["RO.html", "PL.html", "IT.html", "LT.html"]
    for name in files:
        locale_key = name.replace(".html", "")
        path = Path(name)
        original = path.read_text(encoding="utf-8", errors="replace")
        cleaned = clean_html(original, locale_key)
        path.write_text(cleaned, encoding="utf-8")
        print(f"Processed {name}: {len(original)} -> {len(cleaned)} bytes")


if __name__ == "__main__":
    main()
