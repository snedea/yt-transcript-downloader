"""
Web Search Service for Quote and Claim Verification

Uses self-hosted SearXNG instance at s.llam.ai (Tailscale network)
for private, secure quote and claim verification searches.

Supports:
- Quote attribution verification (existing)
- Factual claim verification (new for manipulation analysis)
"""

import logging
import re
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ClaimVerificationResult:
    """Result of a factual claim verification."""

    claim_text: str
    is_verified: bool
    verification_status: str  # verified, disputed, unverified, unverifiable
    confidence: float  # 0-1
    supporting_sources: List[str]
    contradicting_sources: List[str]
    verification_details: Optional[str]
    search_url: Optional[str]


@dataclass
class SourceAttribution:
    """Result of a quote source verification."""

    quote: str
    source: Optional[str]
    source_type: Optional[str]  # religious, political, literary, philosophical, scientific
    confidence: float  # 0-1
    verified: bool
    verification_details: Optional[str]
    search_url: Optional[str]


class WebSearchService:
    """
    Service for verifying quote attributions using self-hosted SearXNG.

    SearXNG is accessible via Tailscale at s.llam.ai, providing
    private, secure searches with no tracking.
    """

    SEARXNG_URL = "https://s.llam.ai"
    SEARCH_TIMEOUT = 15.0  # seconds

    # Known source patterns for quick matching
    KNOWN_SOURCES = {
        "religious": [
            r"bible", r"quran", r"torah", r"bhagavad.?gita", r"vedas?",
            r"proverbs?\s+\d+", r"psalm\s+\d+", r"matthew\s+\d+", r"john\s+\d+",
            r"romans\s+\d+", r"corinthians\s+\d+", r"genesis\s+\d+", r"exodus\s+\d+"
        ],
        "political": [
            r"declaration\s+of\s+independence", r"constitution", r"gettysburg",
            r"inaugural\s+address", r"state\s+of\s+the\s+union",
            r"i\s+have\s+a\s+dream", r"ask\s+not\s+what\s+your\s+country"
        ],
        "literary": [
            r"shakespeare", r"hamlet", r"macbeth", r"romeo\s+and\s+juliet",
            r"dickens", r"tale\s+of\s+two\s+cities", r"homer", r"odyssey", r"iliad",
            r"to\s+be\s+or\s+not\s+to\s+be", r"all\s+the\s+world'?s\s+a\s+stage"
        ],
        "philosophical": [
            r"plato", r"aristotle", r"socrates", r"nietzsche", r"kant",
            r"descartes", r"i\s+think,?\s+therefore", r"allegory\s+of\s+the\s+cave"
        ]
    }

    def __init__(self, searxng_url: Optional[str] = None):
        """Initialize the web search service."""
        self.searxng_url = searxng_url or self.SEARXNG_URL

    async def verify_quote(self, quote: str) -> SourceAttribution:
        """
        Verify a potential quote by searching for its source.

        Args:
            quote: The phrase to verify as a quote

        Returns:
            SourceAttribution with source details if found
        """
        # First check against known patterns
        quick_match = self._quick_pattern_match(quote)
        if quick_match:
            return quick_match

        # Search using SearXNG
        try:
            search_results = await self._search_searxng(quote)
            return self._parse_search_results(quote, search_results)
        except Exception as e:
            logger.error(f"Quote verification failed for '{quote[:50]}...': {e}")
            return SourceAttribution(
                quote=quote,
                source=None,
                source_type=None,
                confidence=0.0,
                verified=False,
                verification_details=f"Search failed: {str(e)}",
                search_url=None
            )

    async def verify_quotes_batch(self, quotes: List[str]) -> List[SourceAttribution]:
        """
        Verify multiple quotes in batch.

        Args:
            quotes: List of phrases to verify

        Returns:
            List of SourceAttribution results
        """
        results = []
        for quote in quotes:
            result = await self.verify_quote(quote)
            results.append(result)
        return results

    def _quick_pattern_match(self, quote: str) -> Optional[SourceAttribution]:
        """
        Quick pattern matching against known famous quotes.

        Returns SourceAttribution if a known pattern is matched.
        """
        quote_lower = quote.lower()

        for source_type, patterns in self.KNOWN_SOURCES.items():
            for pattern in patterns:
                if re.search(pattern, quote_lower):
                    return SourceAttribution(
                        quote=quote,
                        source=f"Likely {source_type} source (pattern match)",
                        source_type=source_type,
                        confidence=0.7,
                        verified=False,
                        verification_details="Matched known pattern, not web-verified",
                        search_url=None
                    )

        return None

    async def _search_searxng(self, quote: str) -> Dict[str, Any]:
        """
        Perform a search using SearXNG.

        Args:
            quote: The phrase to search for

        Returns:
            Raw search results from SearXNG
        """
        # Clean up the quote for searching
        clean_quote = quote.strip()
        if len(clean_quote) > 150:
            # Truncate very long quotes
            clean_quote = clean_quote[:150] + "..."

        search_query = f'"{clean_quote}" source OR origin OR attributed OR quote'

        async with httpx.AsyncClient(timeout=self.SEARCH_TIMEOUT) as client:
            response = await client.get(
                f"{self.searxng_url}/search",
                params={
                    "q": search_query,
                    "format": "json",
                    "categories": "general",
                    "language": "en",
                    "safesearch": 0,
                    "pageno": 1
                },
                headers={
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()

    def _parse_search_results(self, quote: str, results: Dict[str, Any]) -> SourceAttribution:
        """
        Parse SearXNG results to extract source attribution.

        Args:
            quote: Original quote
            results: Raw SearXNG response

        Returns:
            SourceAttribution with parsed source info
        """
        if not results.get("results"):
            return SourceAttribution(
                quote=quote,
                source=None,
                source_type=None,
                confidence=0.0,
                verified=True,
                verification_details="No search results found - likely original content",
                search_url=f"{self.searxng_url}/search?q={quote[:50]}"
            )

        # Analyze top results
        top_results = results["results"][:5]
        source_candidates = []

        for result in top_results:
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()
            url = result.get("url", "")

            # Look for attribution patterns in results
            source_info = self._extract_source_from_result(title, content, url)
            if source_info:
                source_candidates.append(source_info)

        if source_candidates:
            # Return the most confident source
            best_source = max(source_candidates, key=lambda x: x["confidence"])
            return SourceAttribution(
                quote=quote,
                source=best_source["source"],
                source_type=best_source["type"],
                confidence=best_source["confidence"],
                verified=True,
                verification_details=f"Found in web search: {best_source['details']}",
                search_url=top_results[0].get("url")
            )

        # Results found but no clear attribution
        return SourceAttribution(
            quote=quote,
            source=None,
            source_type="unknown",
            confidence=0.3,
            verified=True,
            verification_details="Search results found but no clear attribution identified",
            search_url=top_results[0].get("url") if top_results else None
        )

    def _extract_source_from_result(
        self,
        title: str,
        content: str,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract source information from a search result.

        Returns dict with source, type, confidence, and details.
        """
        combined_text = f"{title} {content}"

        # Check for biblical references
        bible_patterns = [
            r"(genesis|exodus|leviticus|numbers|deuteronomy|joshua|judges|ruth|"
            r"samuel|kings|chronicles|ezra|nehemiah|esther|job|psalms?|proverbs?|"
            r"ecclesiastes|song\s+of\s+songs?|isaiah|jeremiah|lamentations|ezekiel|"
            r"daniel|hosea|joel|amos|obadiah|jonah|micah|nahum|habakkuk|zephaniah|"
            r"haggai|zechariah|malachi|matthew|mark|luke|john|acts|romans|"
            r"corinthians|galatians|ephesians|philippians|colossians|thessalonians|"
            r"timothy|titus|philemon|hebrews|james|peter|jude|revelation)"
            r"\s*\d+[:\d]*"
        ]

        for pattern in bible_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                return {
                    "source": f"Bible - {match.group(0).title()}",
                    "type": "religious",
                    "confidence": 0.85,
                    "details": f"Biblical reference found: {match.group(0)}"
                }

        # Check for famous speakers/authors
        famous_sources = {
            r"martin\s+luther\s+king": ("Martin Luther King Jr.", "political", 0.9),
            r"abraham\s+lincoln": ("Abraham Lincoln", "political", 0.9),
            r"winston\s+churchill": ("Winston Churchill", "political", 0.9),
            r"john\s+f\.?\s*kennedy|jfk": ("John F. Kennedy", "political", 0.9),
            r"shakespeare": ("William Shakespeare", "literary", 0.9),
            r"plato": ("Plato", "philosophical", 0.85),
            r"aristotle": ("Aristotle", "philosophical", 0.85),
            r"socrates": ("Socrates", "philosophical", 0.85),
            r"confucius": ("Confucius", "philosophical", 0.85),
            r"mark\s+twain": ("Mark Twain", "literary", 0.85),
            r"oscar\s+wilde": ("Oscar Wilde", "literary", 0.85),
            r"einstein": ("Albert Einstein", "scientific", 0.85),
            r"gandhi": ("Mahatma Gandhi", "political", 0.85),
            r"nelson\s+mandela": ("Nelson Mandela", "political", 0.9),
        }

        for pattern, (source, source_type, confidence) in famous_sources.items():
            if re.search(pattern, combined_text, re.IGNORECASE):
                return {
                    "source": source,
                    "type": source_type,
                    "confidence": confidence,
                    "details": f"Attributed to {source}"
                }

        # Check URL for quote databases
        quote_sites = ["brainyquote", "goodreads", "quoteinvestigator", "wikiquote"]
        for site in quote_sites:
            if site in url.lower():
                # Extract author from title if possible
                author_match = re.search(r"by\s+([^|,\-]+)", title, re.IGNORECASE)
                if author_match:
                    return {
                        "source": author_match.group(1).strip().title(),
                        "type": "unknown",
                        "confidence": 0.75,
                        "details": f"Found on {site}"
                    }

        return None

    async def check_connection(self) -> bool:
        """
        Check if SearXNG is reachable.

        Returns:
            True if SearXNG is accessible, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.searxng_url}/healthz")
                return response.status_code == 200
        except Exception:
            # Try a simple search as fallback health check
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        f"{self.searxng_url}/search",
                        params={"q": "test", "format": "json"}
                    )
                    return response.status_code == 200
            except Exception:
                return False

    # =========================================================================
    # CLAIM VERIFICATION METHODS (for Manipulation Analysis)
    # =========================================================================

    async def verify_claim(self, claim_text: str) -> ClaimVerificationResult:
        """
        Verify a factual claim by searching for evidence.

        Args:
            claim_text: The claim to verify

        Returns:
            ClaimVerificationResult with verification status
        """
        # Skip very short or vague claims
        if len(claim_text.strip()) < 20:
            return ClaimVerificationResult(
                claim_text=claim_text,
                is_verified=False,
                verification_status="unverifiable",
                confidence=0.0,
                supporting_sources=[],
                contradicting_sources=[],
                verification_details="Claim too short or vague to verify",
                search_url=None
            )

        try:
            # Search for the claim with fact-check context
            search_results = await self._search_claim(claim_text)
            return self._parse_claim_results(claim_text, search_results)
        except Exception as e:
            logger.error(f"Claim verification failed for '{claim_text[:50]}...': {e}")
            return ClaimVerificationResult(
                claim_text=claim_text,
                is_verified=False,
                verification_status="unverified",
                confidence=0.0,
                supporting_sources=[],
                contradicting_sources=[],
                verification_details=f"Search failed: {str(e)}",
                search_url=None
            )

    async def verify_claims_batch(
        self,
        claims: List[str],
        rate_limit_delay: float = 0.5
    ) -> List[ClaimVerificationResult]:
        """
        Verify multiple claims with rate limiting.

        Args:
            claims: List of claim texts to verify
            rate_limit_delay: Seconds to wait between searches

        Returns:
            List of ClaimVerificationResult
        """
        results = []

        for i, claim in enumerate(claims):
            result = await self.verify_claim(claim)
            results.append(result)

            # Rate limiting - don't hammer the search server
            if i < len(claims) - 1:
                await asyncio.sleep(rate_limit_delay)

        return results

    async def _search_claim(self, claim_text: str) -> Dict[str, Any]:
        """
        Search for evidence about a claim.

        Args:
            claim_text: The claim to search for

        Returns:
            Raw search results from SearXNG
        """
        # Clean and truncate
        clean_claim = claim_text.strip()
        if len(clean_claim) > 200:
            clean_claim = clean_claim[:200]

        # Build search query for fact-checking
        search_query = f'"{clean_claim}" fact check OR true OR false OR evidence'

        async with httpx.AsyncClient(timeout=self.SEARCH_TIMEOUT) as client:
            response = await client.get(
                f"{self.searxng_url}/search",
                params={
                    "q": search_query,
                    "format": "json",
                    "categories": "general",
                    "language": "en",
                    "safesearch": 0,
                    "pageno": 1
                },
                headers={
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()

    def _parse_claim_results(
        self,
        claim_text: str,
        results: Dict[str, Any]
    ) -> ClaimVerificationResult:
        """
        Parse search results to determine claim verification status.

        Args:
            claim_text: Original claim
            results: Raw SearXNG response

        Returns:
            ClaimVerificationResult
        """
        if not results.get("results"):
            return ClaimVerificationResult(
                claim_text=claim_text,
                is_verified=False,
                verification_status="unverified",
                confidence=0.3,
                supporting_sources=[],
                contradicting_sources=[],
                verification_details="No search results found",
                search_url=f"{self.searxng_url}/search?q={claim_text[:50]}"
            )

        top_results = results["results"][:8]
        supporting = []
        contradicting = []
        neutral = []

        # Patterns for fact-checking sites
        fact_check_sites = [
            "snopes.com", "politifact.com", "factcheck.org",
            "reuters.com/fact-check", "apnews.com/ap-fact-check"
        ]

        for result in top_results:
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()
            url = result.get("url", "")
            combined = f"{title} {content}"

            source_info = {
                "url": url,
                "title": result.get("title", ""),
                "snippet": result.get("content", "")[:200]
            }

            # Check for explicit verdicts
            if any(word in combined for word in ["true", "correct", "verified", "confirmed", "accurate"]):
                if not any(word in combined for word in ["false", "incorrect", "misleading", "debunked"]):
                    supporting.append(source_info)
            elif any(word in combined for word in ["false", "incorrect", "misleading", "debunked", "myth", "hoax"]):
                contradicting.append(source_info)
            else:
                neutral.append(source_info)

            # Weight fact-checking sites higher
            for site in fact_check_sites:
                if site in url.lower():
                    if source_info in supporting:
                        supporting.append(source_info)  # Double weight
                    elif source_info in contradicting:
                        contradicting.append(source_info)  # Double weight

        # Determine overall status
        supporting_count = len(supporting)
        contradicting_count = len(contradicting)
        total = supporting_count + contradicting_count

        if total == 0:
            verification_status = "unverified"
            confidence = 0.3
            details = "No clear evidence found for or against the claim"
        elif contradicting_count > supporting_count * 2:
            verification_status = "disputed"
            confidence = min(0.9, 0.5 + (contradicting_count - supporting_count) * 0.1)
            details = f"Found {contradicting_count} contradicting sources vs {supporting_count} supporting"
        elif supporting_count > contradicting_count * 2:
            verification_status = "verified"
            confidence = min(0.9, 0.5 + (supporting_count - contradicting_count) * 0.1)
            details = f"Found {supporting_count} supporting sources vs {contradicting_count} contradicting"
        else:
            verification_status = "unverified"
            confidence = 0.4
            details = f"Mixed results: {supporting_count} supporting, {contradicting_count} contradicting"

        return ClaimVerificationResult(
            claim_text=claim_text,
            is_verified=verification_status == "verified",
            verification_status=verification_status,
            confidence=confidence,
            supporting_sources=[s["url"] for s in supporting[:3]],
            contradicting_sources=[s["url"] for s in contradicting[:3]],
            verification_details=details,
            search_url=top_results[0].get("url") if top_results else None
        )


# Singleton instance
_web_search_service: Optional[WebSearchService] = None


def get_web_search_service() -> WebSearchService:
    """Get or create the web search service singleton."""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
