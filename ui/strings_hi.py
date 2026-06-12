# strings_hi.py — RozgarAI Hindi String Constants
# ALL worker-facing strings live here. No Hindi literals anywhere else.

# ── Demo seed ────────────────────────────────────────────────────────────────
DEMO_WORKER_INTRO = (
    "Namaste, mera naam Raju hai. "
    "Main Lucknow mein rehta hoon. "
    "Main electrician hoon, 5 saal ka experience hai. "
    "Mujhe 600 rupaye roz chahiye."
)

# ── Pipeline stage labels ─────────────────────────────────────────────────────
PIPELINE_STAGE_LABELS = {
    "voice_intake":     "Awaaz sun raha hai...",
    "skill_extract":    "Kaam dhundh raha hai...",
    "resume_build":     "Resume bana raha hai...",
    "job_match":        "Kaam match kar raha hai...",
    "interview_coach":  "Tips taiyar kar raha hai...",
    "apply":            "Apply kar raha hai...",
    "status_track":     "Status bhej raha hai...",
    "done":             "Ho gaya!",
    "error":            "Kuch galat hua",
}

PIPELINE_STAGE_EMOJI = {
    "voice_intake":     "🎤",
    "skill_extract":    "🔍",
    "resume_build":     "📄",
    "job_match":        "📍",
    "interview_coach":  "💡",
    "apply":            "✅",
    "status_track":     "📱",
    "done":             "🎉",
    "error":            "❌",
}

# ── Apply agent ───────────────────────────────────────────────────────────────
APPLY_CONSENT_REQUIRED = (
    "Kya aap is kaam ke liye apply karna chahte hain? "
    "Haan ya Nahi batayein."
)
APPLY_CONFIRMED_MSG = "Bahut achha! Aapka application bheja ja raha hai..."
APPLY_SUCCESS_TEMPLATE = (
    "Badhai ho {name} ji! {job_title} ke liye confirm ho gaya.\n"
    "OTP: {otp}\n"
    "Kal {date} ko {location} pahunchen."
)

# ── Resume labels ─────────────────────────────────────────────────────────────
RESUME_SKILLS_LABEL   = "कौशल (Skills)"
RESUME_EXP_LABEL      = "अनुभव (Experience)"
RESUME_CITY_LABEL     = "शहर (City)"
RESUME_WAGE_LABEL     = "दैनिक मजदूरी (Daily Wage)"
RESUME_PHONE_LABEL    = "मोबाइल (Phone)"
RESUME_HEADER_TAG     = "RozgarAI — Aapki Pehchaan"

# ── Error / empty states ──────────────────────────────────────────────────────
NO_JOBS_FOUND   = "Abhi aapke area mein koi kaam nahi hai. Kal dobara try karein."
ERROR_GENERIC   = "Kuch technical gadbad hui. Thodi der mein phir koshish karein."
ERROR_NO_AUDIO  = "Koi awaaz nahi mili. Text mein batayein."

# ── WhatsApp messages ─────────────────────────────────────────────────────────
WHATSAPP_GREETING = (
    "Namaste! Main RozgarAI hoon.\n"
    "Apna naam, kaam aur city batao — main aapke liye job dhundhunga!"
)
WHATSAPP_JOB_ALERT = (
    "Nayi job aapke paas!\n\n"
    "{title}\n"
    "Rs. {wage}/din\n"
    "{distance} km door  •  Kal se shuru\n\n"
    "Kya aap interested hain?"
)
WHATSAPP_CONFIRM_PROMPT = "Haan likhein apply karne ke liye, Nahi likhein chhodne ke liye."
WHATSAPP_OTP_MESSAGE = (
    "Aapka OTP:\n\n"
    "{otp}\n\n"
    "Yeh OTP contractor ko dikhayen jab aap {location} pahunchen."
)
WHATSAPP_STATUS_DONE = (
    "Aapka kaam confirm ho gaya!\n"
    "{job_title} ke liye.\n"
    "OTP: {otp}\n"
    "Kal {date} ko {location} pahunchen."
)

# ── UI labels ─────────────────────────────────────────────────────────────────
UI_DEMO_MODE_LABEL   = "Demo Mode (Raju ka profile)"
UI_NAME_LABEL        = "Aapka naam"
UI_CITY_LABEL        = "Aapka shehar"
UI_SKILLS_LABEL      = "Aapka kaam (Skills)"
UI_WAGE_LABEL        = "Roz ki mazdoori (Rs/din)"
UI_CTA_PRIMARY       = "Kaam Dhundo"
UI_CTA_VOICE         = "Voice Input Upload"
UI_CONSENT_HAAN      = "Haan — Apply Karo"
UI_CONSENT_NAHI      = "Nahi — Chhoddo"

# ── Trace log messages (appended by agents) ───────────────────────────────────
TRACE_VOICE_DONE    = "Voice intake complete — transcript ready"
TRACE_SKILLS_DONE   = "Skills extracted — WorkerProfile populated"
TRACE_RESUME_DONE   = "Resume PDF generated"
TRACE_MATCH_DONE    = "Job matching complete — top matches ready"
TRACE_COACH_DONE    = "Interview tips generated"
TRACE_APPLY_DONE    = "Application submitted — OTP issued"
TRACE_STATUS_DONE   = "Status updated — pipeline complete"

# ── City → pin-code prefix map (top 10 UP districts) ─────────────────────────
UP_CITY_PINCODE = {
    "Lucknow":    "226",
    "Kanpur":     "208",
    "Agra":       "282",
    "Varanasi":   "221",
    "Allahabad":  "211",
    "Meerut":     "250",
    "Gorakhpur":  "273",
    "Bareilly":   "243",
    "Aligarh":    "202",
    "Moradabad":  "244",
}

SKILL_CANONICAL = [
    "electrician", "plumber", "loader", "driver", "mason",
    "helper", "welder", "carpenter", "painter", "security_guard",
]

SKILL_LABELS_HI = {
    "electrician":    "बिजली मिस्त्री",
    "plumber":        "प्लंबर",
    "loader":         "लोडर",
    "driver":         "ड्राइवर",
    "mason":          "राजमिस्त्री",
    "helper":         "हेल्पर",
    "welder":         "वेल्डर",
    "carpenter":      "बढ़ई",
    "painter":        "पेंटर",
    "security_guard": "सिक्योरिटी गार्ड",
}
