"""
Rhetorical Toolkit Data Model

Based on "A Rhetorician's Toolkit for Effective Persuasion" by The Modern Hermeticist.
This module contains structured definitions of rhetorical techniques and the four
pillars of rhetoric (Logos, Pathos, Ethos, Kairos) for use in transcript analysis.

Source: Anton D. Leeman's "Orationis Ratio" and the "Rhetorica ad Herennium" (1st century BC)
"""

from typing import Dict, List, Any


# The Four Pillars of Rhetoric
RHETORICAL_PILLARS: Dict[str, Dict[str, Any]] = {
    "logos": {
        "name": "Logos",
        "greek_meaning": "Reason/Logic",
        "description": "Appeal to an audience's reason through logical ideas and arguments",
        "characteristics": [
            "Logical structure and reasoning",
            "Evidence-based arguments",
            "Clear cause-and-effect relationships",
            "Statistical or factual support",
            "Rational progression of ideas"
        ],
        "detection_hints": [
            "therefore", "because", "consequently", "as a result",
            "evidence shows", "studies indicate", "logically",
            "if...then", "it follows that", "reason suggests"
        ]
    },
    "pathos": {
        "name": "Pathos",
        "greek_meaning": "Emotion/Feeling",
        "description": "Appeal to an audience's emotions through tone, expression, and dramatic elements",
        "characteristics": [
            "Emotional language and imagery",
            "Personal stories and anecdotes",
            "Appeals to fear, hope, anger, or compassion",
            "Vivid descriptions",
            "Dramatic pauses and emphasis"
        ],
        "detection_hints": [
            "imagine", "feel", "heart", "soul", "dream",
            "fear", "hope", "love", "tragedy", "triumph",
            "suffering", "joy", "pain", "desperate"
        ]
    },
    "ethos": {
        "name": "Ethos",
        "greek_meaning": "Character/Credibility",
        "description": "Appeal grounded in the credibility and moral character of the speaker",
        "characteristics": [
            "Establishing authority and expertise",
            "Demonstrating moral integrity",
            "Referencing shared values",
            "Building trust through reputation",
            "Aligning with audience beliefs"
        ],
        "detection_hints": [
            "as an expert", "in my experience", "we believe",
            "our values", "integrity", "trust", "credibility",
            "tradition", "heritage", "our community"
        ]
    },
    "kairos": {
        "name": "Kairos",
        "greek_meaning": "Right Time/Opportunity",
        "description": "Appeal to the timeliness and opportune moment of the argument",
        "characteristics": [
            "Seizing the opportune moment",
            "Relevance to current events",
            "Striking when the iron is hot",
            "Contextual awareness",
            "Timely delivery of key points"
        ],
        "detection_hints": [
            "now is the time", "this moment", "today",
            "never before", "unprecedented", "critical juncture",
            "at this hour", "the time has come", "urgent"
        ]
    }
}


# Rhetorical Techniques/Figures of Speech
RHETORICAL_TECHNIQUES: Dict[str, Dict[str, Any]] = {
    "anaphora": {
        "name": "Anaphora",
        "category": "repetition",
        "etymology": "Greek 'ana' (up) + 'phero' (to carry)",
        "description": "Repetition of a word or phrase at the beginning of successive clauses or sentences",
        "effect": "Creates rhythm, parallelism, and amplifies the impact of the message; aids memory and stirs emotions",
        "examples": [
            "I have a dream... I have a dream... I have a dream...",
            "In every cry of every man, in every infant's cry of fear, in every voice, in every ban",
            "It was the best of times, it was the worst of times, it was the age of wisdom...",
            "Mad world! Mad kings! Mad composition!"
        ],
        "detection_hints": ["repeated phrase at start of sentences", "parallel beginnings", "rhythmic repetition"]
    },
    "climax": {
        "name": "Climax",
        "category": "structure",
        "etymology": "Greek 'klimax' (ladder)",
        "description": "Repetition of words that works like climbing steps, with each word/phrase taking one step higher in intensity",
        "effect": "Builds intensity and focus; often used to create false dichotomies and guide value judgments",
        "examples": [
            "Faith, hope, and love. But the greatest of these is love.",
            "Life, liberty, and the pursuit of happiness",
            "X is good, Y is better, Z is best"
        ],
        "detection_hints": ["ascending importance", "ladder of ideas", "building intensity", "comparative progression"]
    },
    "anticlimax": {
        "name": "Anticlimax",
        "category": "structure",
        "etymology": "Greek 'anti' (against) + 'klimax' (ladder)",
        "description": "The reverse of climax - a descending ladder where an initial term seems better by comparison",
        "effect": "Makes initial options appear superior through descending comparison",
        "examples": [
            "A isn't perfect, but B is worse, and C is worst"
        ],
        "detection_hints": ["descending importance", "downward comparison", "diminishing value"]
    },
    "antithesis": {
        "name": "Antithesis",
        "category": "contrast",
        "etymology": "Greek 'anti' (against) + 'thesis' (position)",
        "description": "Juxtaposing opposing ideas to paint a vivid picture through contrast",
        "effect": "Creates memorable contrasts and can lead to value judgments; beware of false dichotomies",
        "examples": [
            "One small step for man, one giant leap for mankind",
            "Speech is silver, but silence is gold",
            "It was the best of times, it was the worst of times",
            "We are caught in war, wanting peace. We're torn by division, wanting unity."
        ],
        "detection_hints": ["contrasting pairs", "opposing ideas", "but/yet connectors", "juxtaposition"]
    },
    "parison": {
        "name": "Parison",
        "category": "structure",
        "etymology": "Greek 'parisos' (almost equal)",
        "description": "Two clauses structured to mirror each other, creating aesthetic balance",
        "effect": "Creates memorable, balanced sentences; particularly effective for slogans and headlines",
        "examples": [
            "If only the youth knew, if only the elderly could",
            "What you see is what you get",
            "The bigger they are, the harder they fall",
            "Melts in your mouth, not in your hand"
        ],
        "detection_hints": ["mirrored structure", "parallel clauses", "balanced phrasing"]
    },
    "chiasmus": {
        "name": "Chiasmus",
        "category": "structure",
        "etymology": "Greek letter Chi (X) - reflects the criss-cross pattern",
        "description": "Structure of two or more clauses is mirrored and inverted, like the lines of an X",
        "effect": "Creates memorable, profound statements through reversal",
        "examples": [
            "Ask not what your country can do for you – ask what you can do for your country",
            "When the going gets tough, the tough get going",
            "Fair is foul, and foul is fair",
            "Pleasure's a sin, and sometimes sin's a pleasure"
        ],
        "detection_hints": ["ABBA pattern", "inverted repetition", "criss-cross structure", "reversed phrase"]
    },
    "isocolon": {
        "name": "Isocolon",
        "category": "structure",
        "etymology": "Greek 'isos' (equal) + 'kolon' (member/clause)",
        "description": "Parallel clauses that match not only in structure but also in syllable count",
        "effect": "Creates tight rhythmic balance, like a dance of words",
        "examples": [
            "To err is human, to forgive divine",
            "Veni, vidi, vici (I came, I saw, I conquered)"
        ],
        "detection_hints": ["equal syllable count", "rhythmic matching", "precise parallelism"]
    },
    "alliteration": {
        "name": "Alliteration",
        "category": "sound",
        "etymology": "Latin 'ad' (to) + 'littera' (letter)",
        "description": "A series of words with the same first consonant sound occurring close together",
        "effect": "Creates memorable, catchy phrases; heavily used in branding and marketing",
        "examples": [
            "TikTok, Dunkin' Donuts, PayPal, Best Buy, Coca-Cola",
            "Peter Piper picked a peck of pickled peppers",
            "Krispy Kreme, Lulu Lemon, Weight Watchers"
        ],
        "detection_hints": ["repeated initial consonant", "same starting sound", "consonant patterns"]
    },
    "paranomasia": {
        "name": "Paranomasia",
        "category": "wordplay",
        "etymology": "Greek 'para' (beside) + 'onoma' (name)",
        "description": "Wordplay or puns that exploit multiple meanings of a term or similar-sounding words",
        "effect": "Creates humor, reveals wit, and can add layers of meaning; requires cognitive flexibility to appreciate",
        "examples": [
            "A little more than kin, and less than kind",
            "Atheism is a non-prophet institution",
            "Outis (Nobody) is attacking me - from Homer's Odyssey"
        ],
        "detection_hints": ["double meaning", "word play", "homophone usage", "punning"]
    },
    "figura_etymologica": {
        "name": "Figura Etymologica",
        "category": "wordplay",
        "etymology": "Latin 'figura' (form) + Greek 'etymologia' (true sense of a word)",
        "description": "A subtle pun based on etymology, using words that share common etymological roots",
        "effect": "Adds hidden depth appreciated by those with keen interest in language",
        "examples": [
            "Worshipped the creature more than the Creator (creature/creator share Latin root)",
            "There hath he lain for ages, and will lie (lain/lie share root)",
            "Nature is born in heaven (natura/nascitur share root)"
        ],
        "detection_hints": ["etymological connection", "root word play", "hidden linguistic link"]
    },
    "polyptoton": {
        "name": "Polyptoton",
        "category": "wordplay",
        "etymology": "Greek 'polys' (many) + 'ptosis' (case/falling)",
        "description": "Repeating a word in different grammatical forms or cases",
        "effect": "Creates catchy, memorable phrases through variation",
        "examples": [
            "A man's man",
            "In the morning when the morning bird sings",
            "Love is not love which alters when it alteration finds"
        ],
        "detection_hints": ["same word different form", "grammatical variation", "case changes"]
    },
    "zeugma": {
        "name": "Zeugma",
        "category": "structure",
        "etymology": "Greek 'zeugma' (yoke) - related to Sanskrit 'yoga' and Latin 'iungo' (to join)",
        "description": "Using one verb to govern many different ideas in a sentence",
        "effect": "Achieves brevity and conciseness; perfection through subtraction",
        "examples": [
            "He works his work, I mine",
            "She lowered her standards and her neckline"
        ],
        "detection_hints": ["single verb multiple objects", "yoking ideas", "grammatical compression"]
    },
    "syllepsis": {
        "name": "Syllepsis",
        "category": "structure",
        "etymology": "Greek 'syllepsis' (taking together)",
        "description": "A variant of zeugma introducing irony or humor by using a word in two different contexts",
        "effect": "Creates wit through ambiguity",
        "examples": [
            "Would the maiden stain her honour, or her dress?",
            "You are free to execute your laws and your citizens as you see fit"
        ],
        "detection_hints": ["dual meaning verb", "ironic double application", "humorous ambiguity"]
    },
    "anadiplosis": {
        "name": "Anadiplosis",
        "category": "repetition",
        "etymology": "Greek 'ana' (again) + 'diploos' (double)",
        "description": "Repeating a word twice for emphasis, or ending a clause with a word that begins the next",
        "effect": "Evokes feelings of grief or seriousness; creates a chain of thought linking ideas",
        "examples": [
            "Lies, lies! I can't believe a word you say!",
            "Rage, rage against the dying of the light!",
            "Fear leads to anger. Anger leads to hate. Hate leads to suffering.",
            "Suffering produces perseverance; perseverance, character; and character, hope"
        ],
        "detection_hints": ["word repetition", "chain linking", "emphatic doubling", "grief expression"]
    },
    "synonymia": {
        "name": "Synonymia",
        "category": "repetition",
        "etymology": "Greek 'syn' (together) + 'onoma' (name)",
        "description": "Repetition of one idea with different words; a stylized tautology",
        "effect": "Adds emotional force or intellectual clarity through varied expression",
        "examples": [
            "You blocks, you stones, you worse than senseless things!",
            "That's worthless, useless, and of no value"
        ],
        "detection_hints": ["synonym chains", "repeated concept different words", "emphatic tautology"]
    },
    "antimetabole": {
        "name": "Antimetabole",
        "category": "structure",
        "etymology": "Greek 'anti' (against) + 'metabole' (turning about)",
        "description": "A phrase repeated in reverse order, offering a mirror-like reflection of ideas",
        "effect": "Reveals deeper truth or perspective through reversal",
        "examples": [
            "Everything is in your head, your head is in everything",
            "That which is above is as that which is below, and that which is below is as that which is above",
            "You should eat to live, not live to eat"
        ],
        "detection_hints": ["reversed phrase", "mirror structure", "AB-BA word pattern"]
    },
    "tmesis": {
        "name": "Tmesis",
        "category": "structure",
        "etymology": "Greek 'tmesis' (to cut)",
        "description": "Splitting a word and inserting another word or phrase in the middle for emphasis",
        "effect": "Adds dramatic flair and forcefulness",
        "examples": [
            "Un-freaking-believable",
            "A whole nother thing",
            "Abso-bloody-lutely"
        ],
        "detection_hints": ["split word", "inserted emphasis", "word interruption"]
    },
    "praeteritio": {
        "name": "Praeteritio (Paralipsis)",
        "category": "irony",
        "etymology": "Latin 'praeterire' (to pass over)",
        "description": "Emphasizing a point by conspicuously choosing not to mention it",
        "effect": "Draws attention to something while claiming to avoid it; can seem weaselly if poorly executed",
        "examples": [
            "I'm not going to mention his scandals, but his policy is terrible",
            "Far be it from me to tell you how foolish you were",
            "I'm not one for gossip, but did you see what she was wearing?"
        ],
        "detection_hints": ["I won't mention", "not to say", "far be it from me", "needless to say"]
    },
    "metaphor": {
        "name": "Metaphor",
        "category": "comparison",
        "etymology": "Greek 'metaphora' (transfer)",
        "description": "Direct comparison stating one thing IS another, transferring qualities between concepts",
        "effect": "Creates vivid imagery and new understanding through comparison",
        "examples": [
            "Life is a journey",
            "The world is a stage",
            "Time is money"
        ],
        "detection_hints": ["direct comparison", "is/are equivalence", "transferred meaning"]
    },
    "allegory": {
        "name": "Allegory",
        "category": "comparison",
        "etymology": "Greek 'allos' (other) + 'agoreuo' (speak)",
        "description": "Extended metaphor where characters, events, or settings represent abstract ideas",
        "effect": "Conveys complex moral or political messages through narrative",
        "examples": [
            "Animal Farm as political allegory",
            "Plato's Cave as allegory for enlightenment"
        ],
        "detection_hints": ["extended symbolic narrative", "hidden meaning", "representative characters"]
    },
    "irony": {
        "name": "Irony",
        "category": "irony",
        "etymology": "Greek 'eironeia' (dissimulation)",
        "description": "Expressing meaning through language that signifies the opposite",
        "effect": "Creates humor, criticism, or emphasis through contradiction",
        "examples": [
            "Oh, what a beautiful day (said during a storm)",
            "How nice of you to arrive on time (to someone late)"
        ],
        "detection_hints": ["opposite meaning", "sarcasm", "contradiction between words and context"]
    },
    "onomatopoeia": {
        "name": "Onomatopoeia",
        "category": "sound",
        "etymology": "Greek 'onoma' (name) + 'poiein' (to make)",
        "description": "Words that imitate sounds, or more broadly, any invented/made-up word",
        "effect": "Creates vivid sensory experience; when novel words are used, question the intent",
        "examples": [
            "Boom, kablam, pow",
            "Supercalifragilisticexpialidocious",
            "Buzz, hiss, splash"
        ],
        "detection_hints": ["sound imitation", "invented words", "sensory language"]
    },
    "metonymy": {
        "name": "Metonymy",
        "category": "substitution",
        "etymology": "Greek 'meta' (change) + 'onoma' (name)",
        "description": "Calling a thing by a word associated with it",
        "effect": "Creates efficient, evocative reference through association",
        "examples": [
            "The Crown announced... (meaning the monarchy)",
            "My ride is outside (meaning car)",
            "The pen is mightier than the sword"
        ],
        "detection_hints": ["associated term substitution", "symbolic reference", "related concept"]
    },
    "synecdoche": {
        "name": "Synecdoche",
        "category": "substitution",
        "etymology": "Greek 'synekdoche' (understanding one thing with another)",
        "description": "A type of metonymy where a part stands in for the whole, or vice versa",
        "effect": "Creates compact, vivid expression through partial reference",
        "examples": [
            "All hands on deck (hands = sailors)",
            "Nice wheels (wheels = car)",
            "Got a new set of threads (threads = clothes)"
        ],
        "detection_hints": ["part for whole", "whole for part", "representative portion"]
    },
    "antonomasia": {
        "name": "Antonomasia",
        "category": "substitution",
        "etymology": "Greek 'anti' (instead) + 'onoma' (name)",
        "description": "Calling a person by a descriptive phrase that says something about them",
        "effect": "Encapsulates key aspects of identity or reputation in a title",
        "examples": [
            "The Blind Bard (Homer)",
            "The Man of Many Turns (Odysseus)",
            "The Philosopher (Aristotle)",
            "Der Fuhrer (Hitler)"
        ],
        "detection_hints": ["descriptive title", "epithet", "characteristic phrase for person"]
    },
    "hyperbole": {
        "name": "Hyperbole",
        "category": "exaggeration",
        "etymology": "Greek 'hyperbole' (throwing above and beyond)",
        "description": "Deliberate exaggeration for effect, not meant to be taken literally",
        "effect": "Creates emphasis or humor; dangerous when it distorts reality in serious contexts",
        "examples": [
            "I've told you a million times",
            "This bag weighs a ton",
            "I'm so hungry I could eat a horse"
        ],
        "detection_hints": ["obvious exaggeration", "impossible claims", "emphatic overstatement"]
    },
    "litotes": {
        "name": "Litotes",
        "category": "exaggeration",
        "etymology": "Greek 'litos' (plain/simple)",
        "description": "Deliberate understatement, often through negating the opposite",
        "effect": "Creates subtle emphasis through restraint",
        "examples": [
            "Not bad (meaning good)",
            "He's no fool (meaning clever)",
            "That's not a small problem"
        ],
        "detection_hints": ["double negative", "understated positive", "negated opposite"]
    }
}


# Categories for organizing techniques
TECHNIQUE_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "repetition": {
        "name": "Repetition Techniques",
        "description": "Techniques that use repetition of words, sounds, or structures for emphasis",
        "techniques": ["anaphora", "anadiplosis", "synonymia"]
    },
    "structure": {
        "name": "Structural Techniques",
        "description": "Techniques that manipulate sentence or clause structure for effect",
        "techniques": ["climax", "anticlimax", "parison", "chiasmus", "isocolon", "zeugma", "syllepsis", "antimetabole", "tmesis"]
    },
    "contrast": {
        "name": "Contrast Techniques",
        "description": "Techniques that juxtapose opposing ideas",
        "techniques": ["antithesis"]
    },
    "sound": {
        "name": "Sound Techniques",
        "description": "Techniques that use sound patterns for effect",
        "techniques": ["alliteration", "onomatopoeia"]
    },
    "wordplay": {
        "name": "Wordplay Techniques",
        "description": "Techniques involving clever use of words and their meanings",
        "techniques": ["paranomasia", "figura_etymologica", "polyptoton"]
    },
    "comparison": {
        "name": "Comparison Techniques",
        "description": "Techniques that create meaning through comparison",
        "techniques": ["metaphor", "allegory"]
    },
    "substitution": {
        "name": "Substitution Techniques",
        "description": "Techniques that replace one term with another",
        "techniques": ["metonymy", "synecdoche", "antonomasia"]
    },
    "irony": {
        "name": "Irony Techniques",
        "description": "Techniques that express meaning through opposition or misdirection",
        "techniques": ["irony", "praeteritio"]
    },
    "exaggeration": {
        "name": "Exaggeration Techniques",
        "description": "Techniques that use over- or understatement",
        "techniques": ["hyperbole", "litotes"]
    }
}


def get_all_techniques() -> List[str]:
    """Return list of all technique IDs."""
    return list(RHETORICAL_TECHNIQUES.keys())


def get_technique_by_id(technique_id: str) -> Dict[str, Any] | None:
    """Get technique details by ID."""
    return RHETORICAL_TECHNIQUES.get(technique_id)


def get_techniques_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all techniques in a category."""
    if category not in TECHNIQUE_CATEGORIES:
        return []

    technique_ids = TECHNIQUE_CATEGORIES[category]["techniques"]
    return [RHETORICAL_TECHNIQUES[tid] for tid in technique_ids if tid in RHETORICAL_TECHNIQUES]


def get_pillar_by_id(pillar_id: str) -> Dict[str, Any] | None:
    """Get pillar details by ID."""
    return RHETORICAL_PILLARS.get(pillar_id)


def get_toolkit_summary(include_examples: bool = False) -> str:
    """
    Get a summary of the toolkit for use in AI prompts.

    Args:
        include_examples: If False (default), excludes examples to prevent GPT
                         from returning toolkit examples instead of actual transcript quotes.
                         Set to True for documentation purposes only.
    """
    summary = "# Rhetorical Toolkit Reference\n\n"

    summary += "## The Four Pillars of Rhetoric\n"
    for pid, pillar in RHETORICAL_PILLARS.items():
        summary += f"- **{pillar['name']}** ({pillar['greek_meaning']}): {pillar['description']}\n"

    summary += "\n## Rhetorical Techniques\n"
    for category, cat_info in TECHNIQUE_CATEGORIES.items():
        summary += f"\n### {cat_info['name']}\n"
        for tid in cat_info["techniques"]:
            if tid in RHETORICAL_TECHNIQUES:
                tech = RHETORICAL_TECHNIQUES[tid]
                summary += f"- **{tech['name']}** (id: {tid}): {tech['description']}\n"
                # Only include examples for documentation, NOT for analysis prompts
                # Including examples causes GPT to return them instead of actual quotes
                if include_examples:
                    summary += f"  - Examples: {'; '.join(tech['examples'][:2])}\n"

    return summary
