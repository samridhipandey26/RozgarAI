"""utils/pdf_gen.py — Production Resume Generator (ReportLab)
Generates a polished, professional one-page Hindi+English resume
matching the RozgarAI spec: 7 sections, dark theme, Devanagari font support.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).parent.parent
FONT_PATH = ROOT / "fonts" / "NotoSansDevanagari-Regular.ttf"
FONT_BOLD_PATH = ROOT / "fonts" / "NotoSansDevanagari-Bold.ttf"
RESUMES_DIR = ROOT / "data" / "resumes"

# ── Brand palette ──────────────────────────────────────────────────────────────
ORANGE   = (0.969, 0.478, 0.008)   # #F77A02
DARK_BG  = (0.051, 0.051, 0.051)   # #0D0D0D
SURFACE  = (0.110, 0.110, 0.118)   # #1C1C1E
CARD_BG  = (0.133, 0.133, 0.145)   # #222225
WHITE    = (0.953, 0.953, 0.953)   # #F3F3F3
MUTED    = (0.580, 0.600, 0.620)   # #949DA0
ACCENT2  = (0.298, 0.839, 0.635)   # #4CD6A2  (green for availability)
PILL_BG  = (0.200, 0.118, 0.047)   # #331E0C  (dark orange pill bg)


def _register_fonts():
    """Register NotoSansDevanagari if available, else use Helvetica."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if FONT_PATH.exists():
        try:
            pdfmetrics.registerFont(TTFont("Hindi", str(FONT_PATH)))
            pdfmetrics.registerFont(TTFont("Hindi-Bold", str(FONT_BOLD_PATH) if FONT_BOLD_PATH.exists() else str(FONT_PATH)))
            return "Hindi", "Hindi-Bold"
        except Exception as e:
            print(f"[PDF] Font registration failed: {e}")
    return "Helvetica", "Helvetica-Bold"


def _llm_generate_content(
    name: str, role: str, city: str, years_exp: int,
    skills: list, education: str, languages: list,
    expected_wage: int, raw_transcript: str,
) -> dict:
    """
    Ask Claude to generate:
    - professional_summary: 2-3 sentence bilingual summary
    - work_bullets: list of 3-4 bullet points for work experience
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return _fallback_content(name, role, city, years_exp, skills)

    prompt = f"""You are writing a professional resume for an Indian blue-collar worker.
Worker details:
- Name: {name}
- Primary Role: {role}
- City: {city}, Uttar Pradesh
- Experience: {years_exp} years
- Skills: {', '.join(skills)}
- Education: {education}
- Expected wage: ₹{expected_wage}/day
- Raw introduction: "{raw_transcript[:300]}"

Generate ONLY a JSON with these fields:
{{
  "professional_summary": "2-3 sentences in simple English highlighting experience, skills, and work ethic. Professional yet warm tone.",
  "summary_hindi": "Same 2-3 sentences translated to Hindi (Devanagari script).",
  "work_bullets": ["bullet 1", "bullet 2", "bullet 3", "bullet 4"],
  "role_display": "Proper display title (e.g. 'Electrician / बिजली मिस्त्री')"
}}

Work bullets should be achievement/skill statements, 1 sentence each, starting with action verbs.
Example: "Completed wiring for 50+ residential units in Lucknow with zero callbacks"
"""
    try:
        import json
        import re
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"[PDF] LLM content generation failed: {e}")

    return _fallback_content(name, role, city, years_exp, skills)


def _fallback_content(name: str, role: str, city: str, years_exp: int, skills: list) -> dict:
    skill_str = ", ".join(skills[:3]) if skills else role
    return {
        "professional_summary": (
            f"Experienced {role} with {years_exp} years of hands-on work in {city}. "
            f"Skilled in {skill_str}. Available for immediate placement at competitive daily rates."
        ),
        "summary_hindi": (
            f"{years_exp} saal ke anubhav ke saath {city} mein kaam karne wale {role}. "
            f"Saaf kaam, samay par aana aur imandaar kaarya-shaili ke liye jaane jaate hain."
        ),
        "work_bullets": [
            f"Completed {role} work across residential and commercial projects in {city}",
            f"Experienced in {skill_str} with strong attention to safety",
            f"Consistently delivered quality work within deadlines",
            "Available for both short-term contracts and long-term engagements",
        ],
        "role_display": role.replace("_", " ").title(),
    }


SKILL_HINDI_MAP = {
    "electrician":        "बिजली मिस्त्री",
    "plumber":            "नल मिस्त्री",
    "construction_helper":"निर्माण सहायक",
    "warehouse_loader":   "गोदाम मज़दूर",
    "driver":             "ड्राइवर",
    "mason":              "राज मिस्त्री",
    "painter":            "पेंटर",
    "welder":             "वेल्डर",
    "security_guard":     "सुरक्षा गार्ड",
    "domestic_help":      "घरेलू सहायक",
    "helper":             "मज़दूर",
    "carpenter":          "बढ़ई",
}


# ── Main entry point ─────────────────────────────────────────────────────────

def generate_resume_pdf_v2(
    worker_id: str,
    name: str,
    role: str,
    city: str,
    years_exp: int,
    phone: str,
    skills: List[str],
    education: str = "Not specified",
    languages: List[str] = None,
    expected_wage: int = 500,
    raw_transcript: str = "",
    version: int = 1,
) -> str:
    """
    Generate a full-spec one-page resume PDF.
    Returns path to the generated PDF.
    """
    if languages is None:
        languages = ["Hindi"]

    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = worker_id.replace("-", "")[:16]
    out_path = str(RESUMES_DIR / f"{safe_id}_v{version}.pdf")

    # LLM content
    content = _llm_generate_content(
        name=name, role=role, city=city, years_exp=years_exp,
        skills=skills, education=education, languages=languages,
        expected_wage=expected_wage, raw_transcript=raw_transcript,
    )

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    hindi_font, hindi_bold = _register_fonts()

    W, H = A4
    c = canvas.Canvas(out_path, pagesize=A4)

    y = H  # current drawing y (top of page)

    # ─────────────────────────────────────────────────────────────
    # SECTION 0: Full dark background
    # ─────────────────────────────────────────────────────────────
    c.setFillColorRGB(*DARK_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ─────────────────────────────────────────────────────────────
    # SECTION 1: Header Strip (orange top bar)
    # ─────────────────────────────────────────────────────────────
    header_h = 105
    c.setFillColorRGB(*ORANGE)
    c.rect(0, H - header_h, W, header_h, fill=1, stroke=0)

    # Left accent stripe
    c.setFillColorRGB(0.800, 0.350, 0.0)
    c.rect(0, H - header_h, 6, header_h, fill=1, stroke=0)

    # RozgarAI brand (top-right)
    c.setFillColorRGB(*DARK_BG)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(W - 14, H - 16, "RozgarAI")
    c.setFont("Helvetica", 7)
    c.drawRightString(W - 14, H - 27, "rozgarai.in")

    # Name
    c.setFillColorRGB(0.06, 0.06, 0.06)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(18, H - 52, name)

    # Role display (Hindi + English)
    role_display = content.get("role_display", role.replace("_", " ").title())
    role_hindi = SKILL_HINDI_MAP.get(role, role)
    c.setFont(hindi_font, 13)
    c.setFillColorRGB(0.15, 0.08, 0.0)
    c.drawString(18, H - 70, f"{role_display}  |  {role_hindi}")

    # City + Experience badges
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.1, 0.05, 0.0)
    badge_y = H - 89
    # Location badge
    c.setFillColorRGB(0.0, 0.0, 0.0, 0.2)
    c.roundRect(18, badge_y - 3, 95, 18, 5, fill=1, stroke=0)
    c.setFillColorRGB(0.98, 0.98, 0.98)
    c.setFont("Helvetica", 9)
    c.drawString(24, badge_y + 3, f"📍 {city}, UP")
    # Experience badge
    c.setFillColorRGB(0.0, 0.0, 0.0, 0.2)
    c.roundRect(122, badge_y - 3, 100, 18, 5, fill=1, stroke=0)
    c.drawString(128, badge_y + 3, f"⏳ {years_exp} Years Experience")

    y = H - header_h - 8

    # ─────────────────────────────────────────────────────────────
    # SECTION 2: Professional Summary
    # ─────────────────────────────────────────────────────────────
    section_h = 74
    c.setFillColorRGB(*SURFACE)
    c.rect(12, y - section_h, W - 24, section_h, fill=1, stroke=0)
    # Left orange accent
    c.setFillColorRGB(*ORANGE)
    c.rect(12, y - section_h, 4, section_h, fill=1, stroke=0)

    # Section label
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(*ORANGE)
    c.drawString(24, y - 14, "PROFESSIONAL SUMMARY")
    c.setFont(hindi_font, 8)
    c.setFillColorRGB(*MUTED)
    c.drawString(24, y - 24, "पेशेवर परिचय")

    # English summary
    summary = content.get("professional_summary", "")
    _draw_wrapped_text(c, summary, "Helvetica", 9, WHITE, 24, y - 38, W - 50, 14)

    y -= section_h + 6

    # ─────────────────────────────────────────────────────────────
    # SECTION 3: Work Experience
    # ─────────────────────────────────────────────────────────────
    bullets = content.get("work_bullets", [])
    exp_h = 20 + len(bullets) * 16 + 14
    c.setFillColorRGB(*CARD_BG)
    c.rect(12, y - exp_h, W - 24, exp_h, fill=1, stroke=0)
    c.setFillColorRGB(*ORANGE)
    c.rect(12, y - exp_h, 4, exp_h, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(*ORANGE)
    c.drawString(24, y - 14, "WORK EXPERIENCE")
    c.setFont(hindi_font, 8)
    c.setFillColorRGB(*MUTED)
    c.drawString(24, y - 24, "कार्य अनुभव")

    # Role line
    year_from = max(2024 - years_exp, 2010)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(*WHITE)
    c.drawString(24, y - 38, f"{role.replace('_', ' ').title()}  |  {year_from}–Present  |  Freelance / Daily Wage")
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(*MUTED)
    c.drawString(24, y - 49, city)

    by = y - 63
    for bullet in bullets[:4]:
        c.setFillColorRGB(*ORANGE)
        c.circle(30, by + 3, 2, fill=1, stroke=0)
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(*WHITE)
        _draw_wrapped_text(c, bullet, "Helvetica", 9, WHITE, 38, by, W - 70, 13)
        by -= 16

    y -= exp_h + 6

    # ─────────────────────────────────────────────────────────────
    # SECTION 4: Skills & Certifications
    # ─────────────────────────────────────────────────────────────
    pills_per_row = 4
    n_rows = (len(skills) + pills_per_row - 1) // pills_per_row
    skills_h = 22 + n_rows * 28 + 10
    c.setFillColorRGB(*SURFACE)
    c.rect(12, y - skills_h, W - 24, skills_h, fill=1, stroke=0)
    c.setFillColorRGB(*ORANGE)
    c.rect(12, y - skills_h, 4, skills_h, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(*ORANGE)
    c.drawString(24, y - 14, "SKILLS & CERTIFICATIONS")
    c.setFont(hindi_font, 8)
    c.setFillColorRGB(*MUTED)
    c.drawString(24, y - 24, "कौशल एवं प्रमाणपत्र")

    px, py_skill = 24, y - 42
    for i, skill in enumerate(skills):
        label_en = skill.replace("_", " ").title()
        label_hi = SKILL_HINDI_MAP.get(skill, "")
        label = f"{label_en}  {label_hi}" if label_hi else label_en
        pill_w = max(len(label) * 5.8 + 20, 80)

        if px + pill_w > W - 30:
            px = 24
            py_skill -= 26

        c.setFillColorRGB(*PILL_BG)
        c.roundRect(px, py_skill - 4, pill_w, 20, 8, fill=1, stroke=0)
        c.setStrokeColorRGB(*ORANGE)
        c.setLineWidth(0.7)
        c.roundRect(px, py_skill - 4, pill_w, 20, 8, fill=0, stroke=1)
        c.setFont(hindi_font, 8)
        c.setFillColorRGB(*ORANGE)
        c.drawString(px + 8, py_skill + 3, label)
        px += pill_w + 8

    y -= skills_h + 6

    # ─────────────────────────────────────────────────────────────
    # SECTION 5 + 6: Education & Languages (two columns)
    # ─────────────────────────────────────────────────────────────
    col_w = (W - 30) / 2
    row_h = 54

    # Education (left)
    c.setFillColorRGB(*CARD_BG)
    c.rect(12, y - row_h, col_w, row_h, fill=1, stroke=0)
    c.setFillColorRGB(*ORANGE)
    c.rect(12, y - row_h, 4, row_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(*ORANGE)
    c.drawString(24, y - 14, "EDUCATION")
    c.setFont(hindi_font, 8)
    c.setFillColorRGB(*MUTED)
    c.drawString(24, y - 24, "शिक्षा")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(*WHITE)
    c.drawString(24, y - 38, education)

    # Languages & Availability (right)
    rx = 18 + col_w
    c.setFillColorRGB(*CARD_BG)
    c.rect(rx, y - row_h, col_w, row_h, fill=1, stroke=0)
    c.setFillColorRGB(*ACCENT2)
    c.rect(rx, y - row_h, 4, row_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(*ACCENT2)
    c.drawString(rx + 12, y - 14, "LANGUAGES & AVAILABILITY")
    c.setFont(hindi_font, 8)
    c.setFillColorRGB(*MUTED)
    c.drawString(rx + 12, y - 24, "भाषा एवं उपलब्धता")
    lang_str = " • ".join(languages) if languages else "Hindi"
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(*WHITE)
    c.drawString(rx + 12, y - 38, lang_str)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(*ACCENT2)
    c.drawString(rx + 12, y - 50, "✓ Available Immediately / तुरंत")

    y -= row_h + 6

    # ─────────────────────────────────────────────────────────────
    # SECTION 7: Contact Info strip
    # ─────────────────────────────────────────────────────────────
    if phone:
        contact_h = 28
        c.setFillColorRGB(*SURFACE)
        c.rect(12, y - contact_h, W - 24, contact_h, fill=1, stroke=0)
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(*MUTED)
        c.drawString(24, y - 12, "CONTACT")
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(*WHITE)
        c.drawString(90, y - 12, phone)
        y -= contact_h + 6

    # ─────────────────────────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────────────────────────
    import datetime
    gen_date = datetime.date.today().strftime("%d %b %Y")

    footer_h = 28
    c.setFillColorRGB(0.078, 0.078, 0.086)
    c.rect(0, 0, W, footer_h, fill=1, stroke=0)

    c.setFont(hindi_font, 8)
    c.setFillColorRGB(*ORANGE)
    c.drawCentredString(W / 2, 16, "Har haath ko kaam, har kaam ko samman")
    c.setFont(hindi_font, 7)
    c.setFillColorRGB(*MUTED)
    c.drawCentredString(W / 2, 7, f"हर हाथ को काम, हर काम को सम्मान  •  Generated by RozgarAI  •  {gen_date}")

    c.save()
    return out_path


def _draw_wrapped_text(c, text: str, font: str, size: int, color: tuple,
                        x: float, y: float, max_w: float, line_h: float) -> float:
    """Draw text with word wrapping. Returns y after last line."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    c.setFont(font, size)
    c.setFillColorRGB(*color)

    words = text.split()
    line = ""
    cur_y = y
    for word in words:
        test = (line + " " + word).strip()
        if stringWidth(test, font, size) < max_w:
            line = test
        else:
            if line:
                c.drawString(x, cur_y, line)
                cur_y -= line_h
            line = word
    if line:
        c.drawString(x, cur_y, line)
        cur_y -= line_h
    return cur_y


# ── Legacy wrapper (kept for backward compatibility) ──────────────────────────

def generate_resume_pdf(
    worker_id: str, name: str, phone: str, city: str, pin_code: str,
    skills: List[str], experience_years: int, preferred_wage_per_day: int,
) -> str:
    """Legacy API — wraps generate_resume_pdf_v2."""
    return generate_resume_pdf_v2(
        worker_id=worker_id,
        name=name,
        role=skills[0] if skills else "helper",
        city=city,
        years_exp=experience_years,
        phone=phone,
        skills=skills,
        expected_wage=preferred_wage_per_day,
    )
