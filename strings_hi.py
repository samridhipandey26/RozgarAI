"""
strings_hi.py — RozgarAI Hindi Language Constants
===================================================
ALL user-facing Hindi strings must be defined here.
Never hardcode Hindi strings inline in other modules.
This file enables future localization to other Indian languages.

Convention:
  - Constants are UPPER_SNAKE_CASE
  - Comments explain the English meaning
  - Group by agent/feature section
"""

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM / GENERAL
# ─────────────────────────────────────────────────────────────────────────────

APP_NAME = "RozgarAI"
APP_TAGLINE = "Aapki Naukri, Aapki Awaz"  # Your job, your voice

GREETING = "Namaste! Main RozgarAI hoon. Aap kya kaam karte ho, bataiye."
# Hello! I am RozgarAI. Tell me, what work do you do?

ERROR_GENERIC = "Kuch gadbad ho gayi. Dobara koshish karo."
# Something went wrong. Please try again.

PROCESSING = "Ek minute... main dekh raha hoon..."
# One moment... I'm looking...

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1 — VOICE INTAKE
# ─────────────────────────────────────────────────────────────────────────────

VOICE_PROMPT = "Boliye — aap kya kaam karte ho aur kahan rehte ho?"
# Speak — what work do you do and where do you live?

VOICE_RECEIVED = "Shukriya! Aapki baat sun li. Ab main samajh raha hoon..."
# Thank you! I've heard you. Now I'm understanding...

VOICE_TRANSCRIBED = "Yeh mujhe samajh aaya:"
# This is what I understood:

VOICE_ERROR = "Maafi karo, awaaz sahi se nahi aayi. Dobara boliye?"
# Sorry, voice didn't come through properly. Can you speak again?

VOICE_FALLBACK_PROMPT = "Ya yahan type karo — kya kaam karte ho?"
# Or type here — what work do you do?

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2 — SKILL EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

PROFILE_BUILDING = "Aapki jankari bana raha hoon..."
# Building your profile...

PROFILE_DONE = "Bahut achha! Aapki profile tayyar ho gayi."
# Very good! Your profile is ready.

PROFILE_ROLE_LABEL = "Kaam"          # Work/Role
PROFILE_EXP_LABEL = "Anubhav"       # Experience
PROFILE_LOCATION_LABEL = "Shahar"   # City
PROFILE_SKILLS_LABEL = "Hunar"      # Skills
PROFILE_CERT_LABEL = "Certificate"

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3 — RESUME BUILDER
# ─────────────────────────────────────────────────────────────────────────────

RESUME_BUILDING = "Aapka resume bana raha hoon..."
# Building your resume...

RESUME_BUILT = "Resume tayyar ho gaya! Suniye — yeh aapka resume hai:"
# Resume is ready! Listen — this is your resume:

RESUME_CONFIRM_PROMPT = "Kya sab sahi hai? HAAN ya NAHI boliye."
# Is everything correct? Say YES or NO.

RESUME_CONFIRMED = "Shukriya! Ab aapke liye naukri dhundh raha hoon..."
# Thank you! Now finding jobs for you...

RESUME_REJECTED = "Theek hai. Dobara bataiye — aap kya kaam karte ho?"
# Okay. Please tell me again — what work do you do?

RESUME_TTS_INTRO = "Aapka naam hai {name}. Aap {role_hindi} hain. {experience_years} saal ka anubhav hai. Aap {location} mein rehte hain."
# Your name is {name}. You are a {role}. You have {experience_years} years of experience. You live in {location}.

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 4 — JOB MATCHER
# ─────────────────────────────────────────────────────────────────────────────

JOB_SEARCHING = "Aapke liye sahi naukri dhundh raha hoon..."
# Searching for the right job for you...

JOB_MATCH_INTRO = "Aapke liye {count} achchi naukri mili hai:"
# {count} good jobs found for you:

JOB_CARD_FORMAT = "{num}. {employer} — {role_hindi} — ₹{salary}/maah — {match_score}% match"
# {num}. {employer} — {role} — ₹{salary}/month — {match_score}% match

JOB_DISTANCE = "{distance_km} km door"
# {distance_km} km away

JOB_SELECT_PROMPT = "Konsi naukri chahiye? 1, 2, ya 3 boliye."
# Which job do you want? Say 1, 2, or 3.

JOB_SELECTED = "Achha! {employer} ki naukri choose ki."
# Good! You chose the {employer} job.

JOB_NO_MATCH = "Abhi aapke liye sahi naukri nahi mili. Kal dobara try karein."
# No suitable job found right now. Try again tomorrow.

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 5 — INTERVIEW COACH
# ─────────────────────────────────────────────────────────────────────────────

COACH_INTRO = "Interview ki taiyari karein! Main aapko 3 sawaal poochhonga."
# Let's prepare for the interview! I will ask you 3 questions.

COACH_QUESTION_PREFIX = "Sawaal {num}: {question}"
# Question {num}: {question}

COACH_LISTENING = "Shukriya! Aapka jawab sun raha hoon..."
# Thank you! Listening to your answer...

COACH_FEEDBACK_GOOD = "Bahut achha jawab! {feedback}"
# Very good answer! {feedback}

COACH_FEEDBACK_TRY = "Achha koshish! Ek baat yaad rakho: {feedback}"
# Good try! Remember one thing: {feedback}

COACH_COMPLETE = "Shandaar! Interview taiyari ho gayi. Aap tayaar hain!"
# Excellent! Interview preparation is done. You are ready!

COACH_READINESS = "Aapka score: {score}/5"
# Your score: {score}/5

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 6 — APPLY AGENT
# ─────────────────────────────────────────────────────────────────────────────

APPLY_CONFIRM_PROMPT = "{employer} mein {role_hindi} ke liye apply karna chahte ho? HAAN boliye."
# Do you want to apply for {role} at {employer}? Say YES.

APPLY_SUBMITTING = "Application bhej raha hoon..."
# Submitting application...

APPLY_SUCCESS = "Ho gaya! Aapki application {employer} ko bhej di gayi. 🎉"
# Done! Your application has been sent to {employer}.

APPLY_RECEIPT = "Application number: {app_id}"
# Application number: {app_id}

APPLY_NEXT_STEPS = "Jab employer jawab dega, main aapko bataunga."
# When the employer responds, I will let you know.

APPLY_CANCELLED = "Theek hai, apply nahi kiya. Koi aur naukri dekhni hai?"
# Okay, not applied. Want to see another job?

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 7 — STATUS TRACKER
# ─────────────────────────────────────────────────────────────────────────────

STATUS_APPLIED = "Aapki application bhej di gayi. Wait karo..."
# Your application has been sent. Please wait...

STATUS_VIEWED = "Achhi khabar! {employer} ne aapki application dekhi. 👀"
# Good news! {employer} has viewed your application.

STATUS_SHORTLISTED = "Waah! Aap shortlist ho gaye! {employer} ne choose kiya. 🌟"
# Wow! You have been shortlisted! {employer} has chosen you.

STATUS_INTERVIEW_SCHEDULED = "Interview pakka ho gaya! 🎉\n{employer}\n{date} ko {time} baje\n{location}\n\nTime pe pahuncho!"
# Interview confirmed! {employer} on {date} at {time} at {location}. Be on time!

STATUS_REJECTED = "Is baar nahi hua. Himmat mat haro!\n\nAapke liye ek free course hai jo madad karega:\n{course_name}\nLink: {course_link}"
# This time it didn't work out. Don't lose heart! Here's a free course that will help.

STATUS_CHECKING = "Aapki application ka status check kar raha hoon..."
# Checking your application status...

# ─────────────────────────────────────────────────────────────────────────────
# RESUME PDF LABELS
# ─────────────────────────────────────────────────────────────────────────────

PDF_RESUME_TITLE = "Bio-Data / बायोडेटा"
PDF_PERSONAL_SECTION = "Personal Jankari / व्यक्तिगत जानकारी"
PDF_SKILLS_SECTION = "Hunar / कौशल"
PDF_EXPERIENCE_SECTION = "Anubhav / अनुभव"
PDF_CERT_SECTION = "Certificates / प्रमाण पत्र"
PDF_LANGUAGES_SECTION = "Boli / भाषा"
PDF_YEARS_EXP = "saal ka anubhav / वर्ष का अनुभव"
PDF_PREPARED_BY = "RozgarAI dwara tayyar / RozgarAI द्वारा तैयार"

# ─────────────────────────────────────────────────────────────────────────────
# SKILL / ROLE MAPPINGS (Hindi ↔ English)
# ─────────────────────────────────────────────────────────────────────────────

ROLE_MAP_HI_TO_EN = {
    # Electrician
    "bijli ka kaam": "Electrician",
    "bijli wala": "Electrician",
    "electrical": "Electrician",
    "light fitting": "Electrician",
    "wiring": "Electrician",
    # Driver
    "gaadi chalata hoon": "Driver",
    "truck driver": "Driver",
    "taxi chalata": "Driver",
    "driver": "Driver",
    "gaadi": "Driver",
    # Loading / Warehouse
    "truck loading": "Loading Worker",
    "maal uthana": "Loading Worker",
    "godam": "Warehouse Associate",
    "warehouse": "Warehouse Associate",
    "loading unloading": "Loading Worker",
    # Plumber
    "plumber": "Plumber",
    "pipe ka kaam": "Plumber",
    "nalkaa": "Plumber",
    # Construction
    "raj mistri": "Mason",
    "mistri": "Mason",
    "construction": "Construction Labour",
    "cement": "Construction Labour",
    # Security
    "security guard": "Security Guard",
    "chaukidar": "Security Guard",
    "guard": "Security Guard",
    # Cook
    "khana banana": "Cook",
    "cook": "Cook",
    "chef": "Cook",
    # Delivery
    "delivery": "Delivery Executive",
    "parcel": "Delivery Executive",
    # Carpenter
    "badhai": "Carpenter",
    "wood ka kaam": "Carpenter",
    "furniture": "Carpenter",
    # Welder
    "welding": "Welder",
    "gaas wala": "Welder",
}

ROLE_MAP_EN_TO_HI = {
    "Electrician": "Bijli Mistri / बिजली मिस्त्री",
    "Driver": "Driver / ड्राइवर",
    "Loading Worker": "Loading Worker / लोडिंग वर्कर",
    "Warehouse Associate": "Godam Karmchari / गोदाम कर्मचारी",
    "Plumber": "Plumber / प्लम्बर",
    "Mason": "Raj Mistri / राज मिस्त्री",
    "Construction Labour": "Nirman Mazdoor / निर्माण मजदूर",
    "Security Guard": "Security Guard / सुरक्षा गार्ड",
    "Cook": "Rasiya / रसोइया",
    "Delivery Executive": "Delivery Boy / डिलीवरी बॉय",
    "Carpenter": "Badhai / बढ़ई",
    "Welder": "Welder / वेल्डर",
    "Factory Worker": "Factory Mazdoor / फैक्ट्री मजदूर",
}

# ─────────────────────────────────────────────────────────────────────────────
# NSDC / SKILL GAP COURSES
# ─────────────────────────────────────────────────────────────────────────────

SKILL_GAP_COURSES = {
    "Electrician": {
        "name": "Electrician (NSDC) — Free Course",
        "link": "https://www.nsdcindia.org/skill-india",
        "hindi": "Bijli ka kaam sikhiye bilkul free mein",
    },
    "Driver": {
        "name": "Commercial Vehicle Driver (PMKVY)",
        "link": "https://pmkvyofficial.org/",
        "hindi": "Commercial gaadi chalane ka course — bilkul free",
    },
    "Warehouse Associate": {
        "name": "Warehouse & Logistics (NSDC)",
        "link": "https://www.nsdcindia.org/skill-india",
        "hindi": "Godam aur logistics ka kaam sikhiye",
    },
    "default": {
        "name": "Skill India Free Training (PMKVY)",
        "link": "https://pmkvyofficial.org/",
        "hindi": "Naya hunar sikhiye — bilkul free, government ki taraf se",
    },
}
