"""
Manipulation Detection Toolkit

Comprehensive definitions for the 5-dimension analysis framework:
1. Epistemic Integrity - Scholarly vs sloppy reasoning
2. Argument Quality - Logic and coherence
3. Manipulation Risk - Coercive persuasion markers
4. Rhetorical Craft - Style and devices (neutral)
5. Fairness/Balance - One-sidedness detection

Based on:
- Argumentation theory (Toulmin, pragma-dialectics)
- Propaganda studies (IPA, modern research)
- Social psychology (Cialdini, ELM model)
- Critical discourse analysis
- Classical rhetoric
"""

from typing import Dict, List, Any


# ============================================================================
# THE 5 ANALYSIS DIMENSIONS
# ============================================================================

DIMENSION_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "epistemic_integrity": {
        "name": "Epistemic Integrity",
        "description": "Measures how scholarly, careful, and intellectually honest the reasoning is",
        "weight": 0.25,
        "high_score_meaning": "Clear definitions, acknowledges uncertainty, cites sources, distinguishes fact from opinion",
        "low_score_meaning": "Absolutist claims, vague assertions, cherry-picked evidence, conflates fact with opinion",
        "red_flags": [
            "absolutist_certainty",
            "vague_quantifiers",
            "cherry_picking",
            "anecdote_as_proof",
            "trust_me_authority",
            "no_base_rates",
            "no_limitations",
            "shifting_definitions"
        ],
        "green_flags": [
            "uncertainty_acknowledgment",
            "source_citation",
            "base_rate_inclusion",
            "limitation_acknowledgment",
            "clear_definitions",
            "fact_opinion_distinction",
            "steelman_opponents",
            "updates_claims"
        ],
        "detection_hints": [
            "Look for 'always', 'never', 'everyone knows', 'obviously'",
            "Check for 'many people say', 'experts agree' without specifics",
            "Look for single anecdotes replacing data",
            "Check if definitions are clear and consistent"
        ]
    },

    "argument_quality": {
        "name": "Argument Quality",
        "description": "Measures logical coherence, evidence quality, and reasoning soundness",
        "weight": 0.25,
        "high_score_meaning": "Claims supported by relevant evidence, valid reasoning, addresses counterarguments",
        "low_score_meaning": "Unsupported claims, logical fallacies, hidden assumptions, ignores objections",
        "red_flags": [
            "non_sequitur",
            "hidden_premise",
            "false_dilemma",
            "strawman",
            "ad_hominem",
            "post_hoc",
            "slippery_slope",
            "burden_shift",
            "moving_goalposts",
            "correlation_causation"
        ],
        "green_flags": [
            "clear_evidence",
            "valid_inference",
            "addresses_counterarguments",
            "explicit_assumptions",
            "qualified_claims",
            "relevant_expertise_cited"
        ],
        "detection_hints": [
            "Map claims to their supporting evidence",
            "Check if 'therefore' is warranted by premises",
            "Look for hidden assumptions required for conclusion",
            "Check if counterarguments are addressed fairly"
        ]
    },

    "manipulation_risk": {
        "name": "Manipulation Risk",
        "description": "Detects patterns associated with manipulative persuasion attempts",
        "weight": 0.20,
        "high_score_meaning": "Many coercive tactics, fear/urgency, identity manipulation, loaded language",
        "low_score_meaning": "Respectful persuasion, evidence-based, allows audience autonomy",
        "note": "Score is INVERTED for overall calculation - high manipulation = lower overall score",
        "red_flags": [
            "fear_appeal",
            "urgency_pressure",
            "moral_outrage_harvesting",
            "identity_capture",
            "outgroup_demonization",
            "loaded_language",
            "scapegoating",
            "conspiracy_rhetoric",
            "pre_bunking_critics",
            "us_vs_them",
            "purity_tests"
        ],
        "green_flags": [
            "respectful_tone",
            "audience_autonomy",
            "balanced_emotion",
            "evidence_over_appeal"
        ],
        "detection_hints": [
            "Look for 'act now', 'last chance', catastrophe language",
            "Check for 'real patriots/believers do X'",
            "Look for dehumanizing metaphors about opponents",
            "Check for 'they don't want you to know' patterns"
        ]
    },

    "rhetorical_craft": {
        "name": "Rhetorical Craft",
        "description": "Neutral assessment of persuasive technique and style quality",
        "weight": 0.15,
        "high_score_meaning": "Skillful use of rhetorical devices, effective structure, compelling delivery",
        "low_score_meaning": "Weak structure, unclear messaging, ineffective persuasion technique",
        "note": "This is a NEUTRAL dimension - high craft is not good or bad, just effective",
        "components": [
            "ethos_effectiveness",
            "pathos_effectiveness",
            "logos_effectiveness",
            "kairos_awareness",
            "device_sophistication",
            "narrative_structure"
        ],
        "detection_hints": [
            "Evaluate credibility-building techniques",
            "Assess emotional appeal quality",
            "Check logical structure of arguments",
            "Look for timing/relevance awareness"
        ]
    },

    "fairness_balance": {
        "name": "Fairness & Balance",
        "description": "Measures even-handedness, fair representation of opposing views",
        "weight": 0.15,
        "high_score_meaning": "Presents counterarguments fairly, consistent standards, separates people from ideas",
        "low_score_meaning": "One-sided, strawmans opponents, double standards, ad hominem attacks",
        "red_flags": [
            "strawman_opponents",
            "double_standard",
            "card_stacking",
            "no_counterarguments",
            "weakest_example_attack",
            "person_vs_idea_conflation"
        ],
        "green_flags": [
            "steelman_opponents",
            "consistent_standards",
            "counterargument_addressed",
            "separates_person_idea",
            "acknowledges_tradeoffs"
        ],
        "detection_hints": [
            "Check if opposing view is presented in strongest form",
            "Look for consistent application of standards",
            "Check if any counterarguments are mentioned",
            "Look for attacks on people vs their ideas"
        ]
    }
}


# ============================================================================
# MANIPULATION TECHNIQUES - LANGUAGE LEVEL
# ============================================================================

LANGUAGE_TECHNIQUES: Dict[str, Dict[str, Any]] = {
    "vagueness_shield": {
        "name": "Vagueness Shield",
        "category": "language",
        "severity": "medium",
        "description": "Using vague terms to make claims unfalsifiable or deniable",
        "examples": [
            "many people are saying",
            "experts agree",
            "studies show",
            "some say",
            "people are concerned"
        ],
        "detection_patterns": [
            r"many (people|experts|scientists)",
            r"some (say|believe|think)",
            r"studies (show|suggest|indicate)",
            r"it('s| is) (well )?known"
        ],
        "why_concerning": "Shields claims from verification by avoiding specifics"
    },

    "certainty_inflation": {
        "name": "Certainty Inflation",
        "category": "language",
        "severity": "medium",
        "description": "Expressing more certainty than evidence warrants",
        "examples": [
            "obviously",
            "everyone knows",
            "it's proven",
            "undeniably",
            "without question",
            "always",
            "never"
        ],
        "detection_patterns": [
            r"obviously|clearly|undeniably",
            r"everyone knows",
            r"it('s| is) (proven|certain|undeniable)",
            r"without (a )?doubt",
            r"always|never|impossible"
        ],
        "why_concerning": "Discourages questioning by presenting uncertain claims as settled"
    },

    "passive_voice_hiding": {
        "name": "Passive Voice Agency Hiding",
        "category": "language",
        "severity": "low",
        "description": "Using passive voice to obscure who is responsible for actions",
        "examples": [
            "mistakes were made",
            "it was decided",
            "the policy was implemented",
            "people were affected"
        ],
        "detection_patterns": [
            r"(was|were|been) (made|done|decided|implemented)",
            r"it (was|is) (said|believed|thought)"
        ],
        "why_concerning": "Hides accountability and agency"
    },

    "presupposition": {
        "name": "Presupposition Smuggling",
        "category": "language",
        "severity": "medium",
        "description": "Sneaking unproven assumptions into statements as if established",
        "examples": [
            "When did you stop...",
            "Even you agree that...",
            "Given the obvious failure...",
            "Since we all know..."
        ],
        "detection_patterns": [
            r"when did (you|they) stop",
            r"even you (agree|admit|know)",
            r"given (the|that|how)",
            r"since we (all )?(know|agree)"
        ],
        "why_concerning": "Forces acceptance of unproven premises"
    },

    "category_smuggling": {
        "name": "Category/Definition Smuggling",
        "category": "language",
        "severity": "high",
        "description": "Redefining terms mid-argument or using terms tendentiously",
        "examples": [
            "That's not real freedom",
            "True patriots would...",
            "By definition, X is Y"
        ],
        "why_concerning": "Wins arguments by definition rather than substance"
    },

    "motte_and_bailey": {
        "name": "Motte and Bailey",
        "category": "language",
        "severity": "high",
        "description": "Making bold claim (bailey), retreating to defensible claim (motte) when challenged",
        "examples": [
            "Saying 'All X are bad' then 'I just meant some X have problems'",
            "Strong claim followed by 'I'm just asking questions'"
        ],
        "why_concerning": "Allows plausible deniability while spreading bold claims"
    },

    "loaded_language": {
        "name": "Loaded Language",
        "category": "language",
        "severity": "medium",
        "description": "Using emotionally charged words that smuggle in judgments",
        "examples": [
            "regime vs government",
            "freedom fighter vs terrorist",
            "pro-life vs anti-choice",
            "radical vs passionate"
        ],
        "why_concerning": "Embeds conclusions in word choice rather than argument"
    },

    "nominalization": {
        "name": "Nominalization",
        "category": "language",
        "severity": "low",
        "description": "Turning verbs into nouns to hide actors and agency",
        "examples": [
            "'The destruction of X' vs 'Y destroyed X'",
            "'The implementation of policy' vs 'They implemented policy'"
        ],
        "why_concerning": "Obscures who did what to whom"
    }
}


# ============================================================================
# MANIPULATION TECHNIQUES - REASONING LEVEL
# ============================================================================

REASONING_TECHNIQUES: Dict[str, Dict[str, Any]] = {
    "false_dilemma": {
        "name": "False Dilemma",
        "category": "reasoning",
        "severity": "high",
        "description": "Presenting only two options when more exist",
        "examples": [
            "You're either with us or against us",
            "We can have security or freedom, not both",
            "Either accept this or face disaster"
        ],
        "why_concerning": "Artificially constrains choices, often to favor speaker's position"
    },

    "strawman": {
        "name": "Strawman",
        "category": "reasoning",
        "severity": "high",
        "description": "Misrepresenting opponent's position to make it easier to attack",
        "examples": [
            "So you're saying we should just do nothing?",
            "They want to destroy everything we believe in",
            "Critics think X (weak version of their actual view)"
        ],
        "why_concerning": "Avoids engaging with actual opposing arguments"
    },

    "ad_hominem": {
        "name": "Ad Hominem",
        "category": "reasoning",
        "severity": "medium",
        "description": "Attacking the person rather than their argument",
        "examples": [
            "Of course they'd say that, they're a...",
            "You can't trust them because they're...",
            "Consider the source"
        ],
        "why_concerning": "Distracts from evaluating argument on its merits"
    },

    "post_hoc": {
        "name": "Post Hoc Ergo Propter Hoc",
        "category": "reasoning",
        "severity": "medium",
        "description": "Assuming causation from sequence (after this, therefore because of this)",
        "examples": [
            "I prayed and then recovered, so prayer healed me",
            "The policy was enacted, then things improved, so the policy worked"
        ],
        "why_concerning": "Ignores alternative explanations and confuses correlation with causation"
    },

    "slippery_slope": {
        "name": "Slippery Slope",
        "category": "reasoning",
        "severity": "medium",
        "description": "Claiming one step inevitably leads to extreme consequences without justification",
        "examples": [
            "If we allow X, next they'll demand Y, then Z",
            "This is just the beginning, soon they'll..."
        ],
        "why_concerning": "Asserts causal chain without demonstrating each link"
    },

    "whataboutism": {
        "name": "Whataboutism",
        "category": "reasoning",
        "severity": "medium",
        "description": "Deflecting criticism by pointing to others' faults",
        "examples": [
            "What about when they did...",
            "But the other side also...",
            "You're criticizing us, but what about..."
        ],
        "why_concerning": "Avoids addressing the actual criticism"
    },

    "appeal_to_authority": {
        "name": "Inappropriate Appeal to Authority",
        "category": "reasoning",
        "severity": "medium",
        "description": "Citing authority without relevant expertise or verifiability",
        "examples": [
            "A famous actor says this product works",
            "My friend who's a doctor says...",
            "Ancient wisdom tells us..."
        ],
        "why_concerning": "Authority doesn't equal correctness, especially outside expertise"
    },

    "base_rate_neglect": {
        "name": "Base Rate Neglect",
        "category": "reasoning",
        "severity": "high",
        "description": "Ignoring background probabilities when presenting statistics",
        "examples": [
            "100 cases of X! (without mentioning out of millions)",
            "Doubled the risk! (from 0.001% to 0.002%)"
        ],
        "why_concerning": "Makes risks or benefits seem larger than they are"
    },

    "anecdote_laundering": {
        "name": "Anecdote as Proof",
        "category": "reasoning",
        "severity": "medium",
        "description": "Using individual stories to prove general claims",
        "examples": [
            "I know someone who...",
            "There was this one case where...",
            "My experience proves that..."
        ],
        "why_concerning": "Single cases don't establish patterns or causation"
    },

    "moving_goalposts": {
        "name": "Moving Goalposts",
        "category": "reasoning",
        "severity": "high",
        "description": "Changing criteria for proof when original criteria are met",
        "examples": [
            "That's not enough evidence, now you need to show...",
            "But can you prove it was intentional?"
        ],
        "why_concerning": "Makes claims unfalsifiable by always demanding more"
    },

    "burden_shift": {
        "name": "Burden of Proof Shift",
        "category": "reasoning",
        "severity": "medium",
        "description": "Demanding others disprove your claim rather than proving it",
        "examples": [
            "You can't prove it's NOT true",
            "Until you disprove X, I'll believe X",
            "Absence of evidence isn't evidence of absence"
        ],
        "why_concerning": "Inverts proper reasoning; claimant bears burden"
    },

    "non_sequitur": {
        "name": "Non Sequitur",
        "category": "reasoning",
        "severity": "medium",
        "description": "Conclusion doesn't follow from premises",
        "examples": [
            "They're experienced, therefore they're correct",
            "It's natural, therefore it's good"
        ],
        "why_concerning": "Missing logical link between premise and conclusion"
    }
}


# ============================================================================
# MANIPULATION TECHNIQUES - PROPAGANDA/SOCIAL PSYCHOLOGY
# ============================================================================

PROPAGANDA_TECHNIQUES: Dict[str, Dict[str, Any]] = {
    "bandwagon": {
        "name": "Bandwagon",
        "category": "propaganda",
        "severity": "medium",
        "description": "Appealing to popularity or the crowd",
        "examples": [
            "Everyone is waking up to...",
            "More and more people are realizing...",
            "Join millions who already..."
        ],
        "psychology": "Social proof principle (Cialdini)",
        "why_concerning": "Popular belief doesn't equal truth"
    },

    "scapegoating": {
        "name": "Scapegoating",
        "category": "propaganda",
        "severity": "high",
        "description": "Blaming a single group/person for complex problems",
        "examples": [
            "They are the reason for all our problems",
            "If only they weren't here, things would be better",
            "Everything was fine until they..."
        ],
        "psychology": "Outgroup blame, simplification of complexity",
        "why_concerning": "Oversimplifies, promotes division, avoids systemic analysis"
    },

    "fear_salvation": {
        "name": "Fear + Salvation",
        "category": "propaganda",
        "severity": "high",
        "description": "Escalating threat + 'only we can fix it' pattern",
        "examples": [
            "The threat is worse than ever, but together we can...",
            "Our way of life is under attack, only X can save us",
            "Time is running out, act now or..."
        ],
        "psychology": "Fear appeal + scarcity + authority",
        "why_concerning": "Exploits fear to bypass rational evaluation"
    },

    "identity_capture": {
        "name": "Identity Capture",
        "category": "propaganda",
        "severity": "high",
        "description": "Tying beliefs to group identity",
        "examples": [
            "Real patriots believe...",
            "True Christians would never...",
            "Any decent person knows..."
        ],
        "psychology": "Unity principle, identity fusion",
        "why_concerning": "Makes changing mind feel like betraying identity"
    },

    "outgroup_demonization": {
        "name": "Outgroup Demonization",
        "category": "propaganda",
        "severity": "high",
        "description": "Dehumanizing or demonizing the opposition",
        "examples": [
            "They are animals/vermin/cancer",
            "They want to destroy everything",
            "They're evil/satanic/subhuman"
        ],
        "psychology": "Dehumanization, moral disengagement",
        "why_concerning": "Precursor to justifying harm, prevents understanding"
    },

    "glittering_generalities": {
        "name": "Glittering Generalities",
        "category": "propaganda",
        "severity": "medium",
        "description": "Using vague positive words without specifics",
        "examples": [
            "Freedom, justice, and the American way",
            "For the people, by the people",
            "Hope, change, progress"
        ],
        "psychology": "Transfer of positive affect to speaker/cause",
        "why_concerning": "Emotional appeal without substantive claims"
    },

    "transfer": {
        "name": "Transfer",
        "category": "propaganda",
        "severity": "medium",
        "description": "Associating with revered symbols/concepts to gain legitimacy",
        "examples": [
            "Wrapping in the flag",
            "Invoking religious symbols",
            "Connecting to founding fathers/national heroes"
        ],
        "psychology": "Association, halo effect",
        "why_concerning": "Borrows credibility without earning it"
    },

    "testimonial": {
        "name": "Testimonial",
        "category": "propaganda",
        "severity": "low",
        "description": "Using endorsements from admired figures",
        "examples": [
            "Celebrity X supports this",
            "Famous person Y uses this product",
            "Expert Z recommends..."
        ],
        "psychology": "Authority, liking principle",
        "why_concerning": "Admiration doesn't equal expertise or truth"
    },

    "plain_folks": {
        "name": "Plain Folks",
        "category": "propaganda",
        "severity": "low",
        "description": "Pretending to be ordinary to gain trust",
        "examples": [
            "I'm just a regular person like you",
            "I understand your struggles",
            "I'm not like those elites"
        ],
        "psychology": "Liking, similarity principle",
        "why_concerning": "May hide actual power/privilege/agenda"
    },

    "pre_bunking": {
        "name": "Pre-bunking Critics",
        "category": "propaganda",
        "severity": "high",
        "description": "Inoculating audience against future criticism",
        "examples": [
            "They'll call me crazy for saying this, but...",
            "The media will lie about what I just said",
            "The establishment doesn't want you to know..."
        ],
        "psychology": "Inoculation theory, us vs them",
        "why_concerning": "Makes audience dismiss any contrary evidence"
    },

    "conspiracy_rhetoric": {
        "name": "Conspiracy Rhetoric",
        "category": "propaganda",
        "severity": "high",
        "description": "Unfalsifiable claims about hidden plots",
        "examples": [
            "They don't want you to know...",
            "The hidden truth is...",
            "Wake up and see the real agenda...",
            "It's all connected if you look deeper..."
        ],
        "markers": [
            "unfalsifiable_claims",
            "hidden_truth",
            "connecting_unrelated",
            "shifting_evidence_requirements"
        ],
        "why_concerning": "Unfalsifiable, promotes distrust of all sources"
    },

    "urgency_scarcity": {
        "name": "Urgency/Scarcity",
        "category": "propaganda",
        "severity": "medium",
        "description": "Creating artificial time pressure or scarcity",
        "examples": [
            "Act now before it's too late",
            "Limited time only",
            "This is your last chance"
        ],
        "psychology": "Scarcity principle (Cialdini)",
        "why_concerning": "Pressures decisions before careful evaluation"
    },

    "us_vs_them": {
        "name": "Us vs Them Framing",
        "category": "propaganda",
        "severity": "high",
        "description": "Dividing world into ingroup and enemy outgroup",
        "examples": [
            "We are the good ones, they are the bad ones",
            "You're either with us or against us",
            "Our side vs their side"
        ],
        "psychology": "Ingroup/outgroup bias, tribal psychology",
        "why_concerning": "Prevents nuance, promotes tribalism"
    },

    "moral_outrage": {
        "name": "Moral Outrage Harvesting",
        "category": "propaganda",
        "severity": "high",
        "description": "Repeatedly triggering disgust/anger for engagement",
        "examples": [
            "Can you BELIEVE they did this?!",
            "This is absolutely DISGUSTING",
            "Share if you're OUTRAGED"
        ],
        "psychology": "Emotional contagion, engagement optimization",
        "why_concerning": "Outrage is addictive and impairs reasoning"
    }
}


# ============================================================================
# COMBINED TECHNIQUES DICTIONARY
# ============================================================================

MANIPULATION_TECHNIQUES: Dict[str, Dict[str, Any]] = {
    **LANGUAGE_TECHNIQUES,
    **REASONING_TECHNIQUES,
    **PROPAGANDA_TECHNIQUES
}


# ============================================================================
# TECHNIQUE CATEGORIES
# ============================================================================

TECHNIQUE_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "language": {
        "name": "Language-Level Techniques",
        "description": "Manipulation through word choice, framing, and linguistic tricks",
        "techniques": list(LANGUAGE_TECHNIQUES.keys())
    },
    "reasoning": {
        "name": "Reasoning-Level Techniques",
        "description": "Logical fallacies and argumentative tricks",
        "techniques": list(REASONING_TECHNIQUES.keys())
    },
    "propaganda": {
        "name": "Propaganda & Social Psychology",
        "description": "Mass persuasion and psychological manipulation tactics",
        "techniques": list(PROPAGANDA_TECHNIQUES.keys())
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_techniques() -> List[str]:
    """Return list of all technique IDs."""
    return list(MANIPULATION_TECHNIQUES.keys())


def get_technique_by_id(technique_id: str) -> Dict[str, Any] | None:
    """Get technique details by ID."""
    return MANIPULATION_TECHNIQUES.get(technique_id)


def get_techniques_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all techniques in a category."""
    if category not in TECHNIQUE_CATEGORIES:
        return []
    technique_ids = TECHNIQUE_CATEGORIES[category]["techniques"]
    return [MANIPULATION_TECHNIQUES[tid] for tid in technique_ids if tid in MANIPULATION_TECHNIQUES]


def get_dimension_by_id(dimension_id: str) -> Dict[str, Any] | None:
    """Get dimension details by ID."""
    return DIMENSION_DEFINITIONS.get(dimension_id)


def get_manipulation_toolkit_summary() -> str:
    """
    Get a summary of the manipulation toolkit for use in AI prompts.
    Returns a formatted string suitable for GPT system prompts.
    """
    summary = "# Manipulation Analysis Toolkit Reference\n\n"

    # Dimensions
    summary += "## The 5 Analysis Dimensions\n\n"
    for dim_id, dim in DIMENSION_DEFINITIONS.items():
        summary += f"### {dim['name']}\n"
        summary += f"{dim['description']}\n"
        summary += f"- **High score**: {dim['high_score_meaning']}\n"
        summary += f"- **Low score**: {dim['low_score_meaning']}\n"
        if dim.get('red_flags'):
            summary += f"- **Red flags**: {', '.join(dim['red_flags'][:5])}...\n"
        summary += "\n"

    # Techniques by category
    summary += "## Manipulation Techniques\n\n"
    for cat_id, cat in TECHNIQUE_CATEGORIES.items():
        summary += f"### {cat['name']}\n"
        for tech_id in cat['techniques'][:8]:  # Limit for prompt size
            tech = MANIPULATION_TECHNIQUES.get(tech_id, {})
            summary += f"- **{tech.get('name', tech_id)}**: {tech.get('description', '')}\n"
        summary += "\n"

    return summary


def get_full_prompt_reference() -> str:
    """
    Get a comprehensive reference for the GPT analysis prompt.
    More detailed than get_manipulation_toolkit_summary().
    """
    lines = [
        "# MANIPULATION ANALYSIS REFERENCE",
        "",
        "## DIMENSIONS TO SCORE (each 0-100)",
        ""
    ]

    for dim_id, dim in DIMENSION_DEFINITIONS.items():
        lines.append(f"### {dim_id.upper()}: {dim['name']}")
        lines.append(dim['description'])
        lines.append(f"Red flags to detect: {', '.join(dim.get('red_flags', []))}")
        lines.append(f"Green flags to reward: {', '.join(dim.get('green_flags', []))}")
        lines.append("")

    lines.append("## MANIPULATION TECHNIQUES TO DETECT")
    lines.append("")

    for cat_id, cat in TECHNIQUE_CATEGORIES.items():
        lines.append(f"### {cat['name'].upper()}")
        for tech_id in cat['techniques']:
            tech = MANIPULATION_TECHNIQUES[tech_id]
            lines.append(f"- {tech['name']}: {tech['description']}")
            if tech.get('examples'):
                lines.append(f"  Examples: {'; '.join(tech['examples'][:2])}")
        lines.append("")

    return "\n".join(lines)
