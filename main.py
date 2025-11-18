import os
from datetime import date, datetime
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Astrology Insights API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Utility data -----
ZODIAC_RANGES = [
    ("Capricorn", (12, 22), (1, 19)),
    ("Aquarius", (1, 20), (2, 18)),
    ("Pisces", (2, 19), (3, 20)),
    ("Aries", (3, 21), (4, 19)),
    ("Taurus", (4, 20), (5, 20)),
    ("Gemini", (5, 21), (6, 20)),
    ("Cancer", (6, 21), (7, 22)),
    ("Leo", (7, 23), (8, 22)),
    ("Virgo", (8, 23), (9, 22)),
    ("Libra", (9, 23), (10, 22)),
    ("Scorpio", (10, 23), (11, 21)),
    ("Sagittarius", (11, 22), (12, 21)),
]

SIGN_EMOJI = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}

TRAITS: Dict[str, Dict[str, List[str]]] = {
    "Aries": {
        "strengths": ["Bold self-starter", "Direct communication", "Thrives under pressure"],
        "growth": ["Pacing impulsivity", "Active listening", "Finishing what you start"],
        "likes": ["Healthy competition", "Quick decisions", "Fresh starts and challenges"],
        "watchouts": ["Impatience", "Starting too many things", "Speaking before thinking"],
    },
    "Taurus": {
        "strengths": ["Steadfast and reliable", "Sensory appreciation", "Financial savvy"],
        "growth": ["Flexibility in change", "Letting go of stubborn stances", "Balancing comfort with growth"],
        "likes": ["Good food and music", "Consistency", "Tactile experiences"],
        "watchouts": ["Resistance to change", "Over-attachment", "Comfort-zone inertia"],
    },
    "Gemini": {
        "strengths": ["Curious communicator", "Quick learner", "Social connector"],
        "growth": ["Depth over breadth", "Grounding routines", "Follow-through"],
        "likes": ["Conversation", "Variety", "Writing and media"],
        "watchouts": ["Scattered focus", "Restlessness", "Overthinking"],
    },
    "Cancer": {
        "strengths": ["Empathetic and protective", "Deep intuition", "Nurturing home-maker"],
        "growth": ["Boundaries", "Sharing needs openly", "Balancing care with self-care"],
        "likes": ["Family traditions", "Cooking", "Meaningful one-on-ones"],
        "watchouts": ["Moodiness", "Retreating into shell", "Taking things personally"],
    },
    "Leo": {
        "strengths": ["Warm leadership", "Creative flair", "Loyal heart"],
        "growth": ["Listening for understanding", "Sharing spotlight", "Humility in wins"],
        "likes": ["Celebrations", "Art and performance", "Romantic gestures"],
        "watchouts": ["Needing external validation", "Dramatics", "Pride blocking apologies"],
    },
    "Virgo": {
        "strengths": ["Practical problem-solver", "Attention to detail", "Service-oriented"],
        "growth": ["Self-compassion", "Big-picture thinking", "Delegating"],
        "likes": ["Order and craft", "Healthy habits", "Skill-building"],
        "watchouts": ["Perfectionism", "Over-critique", "Analysis paralysis"],
    },
    "Libra": {
        "strengths": ["Diplomatic", "Stylistic sense", "Partnership focus"],
        "growth": ["Decision confidence", "Stating preferences", "Conflict tolerance"],
        "likes": ["Aesthetics", "Harmony", "Collaborative projects"],
        "watchouts": ["People-pleasing", "Indecision", "Avoiding necessary conflict"],
    },
    "Scorpio": {
        "strengths": ["Deep loyalty", "Psychological insight", "Transformational power"],
        "growth": ["Trusting gradually", "Letting lightness in", "Releasing control"],
        "likes": ["Honesty", "Intensity", "Research and mysteries"],
        "watchouts": ["All-or-nothing thinking", "Jealousy", "Holding grudges"],
    },
    "Sagittarius": {
        "strengths": ["Optimistic explorer", "Big-picture vision", "Humor under stress"],
        "growth": ["Detail discipline", "Commitment", "Realistic timelines"],
        "likes": ["Travel", "Learning", "Philosophy and sports"],
        "watchouts": ["Over-promising", "Bluntness", "Restlessness"],
    },
    "Capricorn": {
        "strengths": ["Strategic and steady", "Long-term planner", "Resilient under responsibility"],
        "growth": ["Softening self-critique", "Work-life balance", "Celebrating progress"],
        "likes": ["Structure", "Traditions", "Practical wins"],
        "watchouts": ["Rigid routines", "Overworking", "Guarded emotions"],
    },
    "Aquarius": {
        "strengths": ["Innovative thinker", "Community-minded", "Independent"],
        "growth": ["Emotional presence", "Consistency", "Translating ideas into action"],
        "likes": ["Technology", "Causes", "Originality"],
        "watchouts": ["Detachment", "Rebellion for its own sake", "Stubborn ideals"],
    },
    "Pisces": {
        "strengths": ["Compassionate dreamer", "Creative empathy", "Spiritual sensitivity"],
        "growth": ["Grounded boundaries", "Clear communication", "Practical steps"],
        "likes": ["Music", "Poetry", "Quiet reflective spaces"],
        "watchouts": ["Escapism", "Over-giving", "Foggy priorities"],
    },
}

COMPATIBILITY: Dict[str, List[Dict[str, str]]] = {
    "Aries": [
        {"sign": "Leo", "reason": "Shared fire brings passion and mutual encouragement."},
        {"sign": "Sagittarius", "reason": "Adventure, humor, and forward momentum."},
        {"sign": "Gemini", "reason": "Fast-paced ideas keep energy lively."},
    ],
    "Taurus": [
        {"sign": "Virgo", "reason": "Practical rhythms and mutual reliability."},
        {"sign": "Capricorn", "reason": "Long-term planning and loyalty."},
        {"sign": "Cancer", "reason": "Comfort, home, and heartfelt steadiness."},
    ],
    "Gemini": [
        {"sign": "Libra", "reason": "Dialogue, style, and mental harmony."},
        {"sign": "Aquarius", "reason": "Ideas, innovation, and intellectual play."},
        {"sign": "Aries", "reason": "Spontaneity and shared curiosity."},
    ],
    "Cancer": [
        {"sign": "Scorpio", "reason": "Depth, loyalty, and emotional safety."},
        {"sign": "Pisces", "reason": "Intuition and creative comfort."},
        {"sign": "Taurus", "reason": "Nurturing routines and stability."},
    ],
    "Leo": [
        {"sign": "Aries", "reason": "Spark, courage, and celebration."},
        {"sign": "Sagittarius", "reason": "Adventure and optimism."},
        {"sign": "Libra", "reason": "Charm and social warmth."},
    ],
    "Virgo": [
        {"sign": "Taurus", "reason": "Reliable routines and craftsmanship."},
        {"sign": "Capricorn", "reason": "Long-term goals and maturity."},
        {"sign": "Cancer", "reason": "Care with practicality."},
    ],
    "Libra": [
        {"sign": "Gemini", "reason": "Conversation and balance."},
        {"sign": "Aquarius", "reason": "Shared ideals and community."},
        {"sign": "Leo", "reason": "Romance and aesthetic flair."},
    ],
    "Scorpio": [
        {"sign": "Cancer", "reason": "Deep emotional trust."},
        {"sign": "Pisces", "reason": "Spiritual intimacy."},
        {"sign": "Capricorn", "reason": "Power with purpose."},
    ],
    "Sagittarius": [
        {"sign": "Aries", "reason": "Momentum and optimism."},
        {"sign": "Leo", "reason": "Courage and fun."},
        {"sign": "Aquarius", "reason": "Ideas and freedom."},
    ],
    "Capricorn": [
        {"sign": "Taurus", "reason": "Security and patience."},
        {"sign": "Virgo", "reason": "Efficiency and care."},
        {"sign": "Scorpio", "reason": "Focus and depth."},
    ],
    "Aquarius": [
        {"sign": "Gemini", "reason": "Thought partners and wit."},
        {"sign": "Libra", "reason": "Harmony in ideas and society."},
        {"sign": "Sagittarius", "reason": "Exploration and vision."},
    ],
    "Pisces": [
        {"sign": "Cancer", "reason": "Emotional resonance."},
        {"sign": "Scorpio", "reason": "Transformative intimacy."},
        {"sign": "Capricorn", "reason": "Grounding support for dreams."},
    ],
}


def sign_for(d: date) -> str:
    m, day = d.month, d.day
    for sign, (start_m, start_d), (end_m, end_d) in ZODIAC_RANGES:
        if (m == start_m and day >= start_d) or (m == end_m and day <= end_d):
            return sign
    # If not matched above, it's Capricorn at year turn
    return "Capricorn"


def seeded_index(name: str, dob: date, modulo: int) -> int:
    seed = sum(ord(c) for c in (name.strip().lower() + dob.isoformat()))
    return seed % modulo


def month_span(seed: int) -> str:
    months = [
        "early January", "late January", "early February", "late February",
        "early March", "late March", "early April", "late April",
        "early May", "late May", "early June", "late June",
        "early July", "late July", "early August", "late August",
        "early September", "late September", "early October", "late October",
        "early November", "late November", "early December", "late December",
    ]
    a = months[seed % len(months)]
    b = months[(seed * 7 + 13) % len(months)]
    return f"from {a} to {b}"


class AstrologyRequest(BaseModel):
    name: str = Field(..., min_length=1)
    dob: date


class PredictionBlock(BaseModel):
    title: str
    bullets: List[str]


class AstrologyResponse(BaseModel):
    name: str
    dob: date
    sign: str
    symbol: str
    personality: List[PredictionBlock]
    future: Dict[str, PredictionBlock]
    matches: List[Dict[str, str]]
    disclaimer: str


@app.get("/")
def read_root():
    return {"message": "Astrology Insights API is running"}


@app.post("/api/astrology/predict", response_model=AstrologyResponse)
def predict(req: AstrologyRequest):
    try:
        user_sign = sign_for(req.dob)
        traits = TRAITS[user_sign]
        idx = seeded_index(req.name, req.dob, 1000)

        # Personality sections
        personality = [
            PredictionBlock(
                title="Core strengths",
                bullets=[
                    *traits["strengths"],
                    "Natural rhythm this year: maintain steady momentum rather than big bursts.",
                ],
            ),
            PredictionBlock(
                title="Growth edges",
                bullets=[
                    *traits["growth"],
                    "A small weekly ritual will compound into major progress.",
                ],
            ),
            PredictionBlock(
                title="What energizes you",
                bullets=[
                    *traits["likes"],
                    "Meaningful conversation that turns into action.",
                ],
            ),
            PredictionBlock(
                title="Watch-outs",
                bullets=[
                    *traits["watchouts"],
                    "Avoid comparing your timeline to others—yours is unfolding right on time.",
                ],
            ),
        ]

        # Future aspects with soft, time-bound guidance
        love_seed = (idx * 3 + 7) % 1000
        career_seed = (idx * 5 + 11) % 1000
        growth_seed = (idx * 7 + 23) % 1000

        future = {
            "love": PredictionBlock(
                title="Love & Relationships",
                bullets=[
                    f"A notable opening for connection appears {month_span(love_seed)}.",
                    "Someone with complementary strengths helps you feel seen and understood.",
                    "Clear, kind honesty accelerates closeness—say what you mean and mean what you say.",
                    "Prior relationships resurface with closure or a fresh perspective—take the learning, not the loop.",
                ],
            ),
            "career": PredictionBlock(
                title="Career & Purpose",
                bullets=[
                    f"Momentum builds {month_span(career_seed)}—expect recognition for consistent effort.",
                    "A stretch project highlights your leadership; document your wins.",
                    "Mentorship—either giving or receiving—unlocks the next step.",
                    "Focus on systems: small improvements to routines free up hours each week.",
                ],
            ),
            "growth": PredictionBlock(
                title="Personal Growth",
                bullets=[
                    f"Inner clarity crystallizes {month_span(growth_seed)} after you simplify commitments.",
                    "A daily 10–15 minute practice compounds into confidence.",
                    "Your intuition sharpens when you slow down before big choices.",
                    "Saying no to misaligned requests creates room for a resounding yes.",
                ],
            ),
        }

        matches = COMPATIBILITY[user_sign]

        resp = AstrologyResponse(
            name=req.name.strip(),
            dob=req.dob,
            sign=user_sign,
            symbol=SIGN_EMOJI.get(user_sign, ""),
            personality=personality,
            future=future,
            matches=matches,
            disclaimer=(
                "Astrology-based guidance intended for reflection and entertainment—"
                "use your judgment for life decisions. Timelines are indicative, not guarantees."
            ),
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db  # type: ignore

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # pragma: no cover
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:  # pragma: no cover
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
