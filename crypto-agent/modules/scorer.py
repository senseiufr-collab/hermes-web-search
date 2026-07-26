#!/usr/bin/env python3
"""Signal scorer for crypto-agent."""
from __future__ import annotations

from typing import List, Dict, Any


def _contains_any(text: str, keywords: List[str]) -> bool:
    t = text.lower()
    return any(k in t for k in keywords)


def score_item(text: str, horizon: str = "short") -> Dict[str, Any]:
    long_kw = [
        "vc", "fundraising", "funding round", "raised", "valuation",
        "institutional", "treasury", "tokenization", "rwa", "infrastructure",
        "layer 2", "l2", "ethereum", "btc", "solana", "avalanche", "chainlink"
    ]
    short_kw = [
        "listing", "exchange", "pump", "spike", "volume", "fomo", "trending",
        "announcement", "partnership", "airdrop", "nft", "meme", "etf", "flow"
    ]
    neg_kw = ["hack", "exploit", "scam", "downgrade", "ban", "investigation"]

    horizon = (horizon or "short").lower()
    primary = long_kw if horizon == "long" else short_kw
    score = 0.0
    reasons: List[str] = []

    if _contains_any(text, primary):
        score += 0.6
        reasons.append("matches_" + horizon + "_keywords")

    if _contains_any(text, ["$", "billion", "млрд", "million", "млн"]):
        score += 0.2
        reasons.append("mentions_funding_size")

    if _contains_any(text, neg_kw):
        score -= 0.5
        reasons.append("negative_signal")

    score = max(0.0, min(1.0, score + 0.1 * len(reasons)))
    confidence = "high" if score >= 0.75 else ("medium" if score >= 0.45 else "low")
    return {"score": round(score, 2), "confidence": confidence, "reasons": reasons}


def rank_signals(items: List[Dict[str, Any]], horizon: str = "short") -> List[Dict[str, Any]]:
    ranked = []
    for it in items:
        text = " ".join(str(it.get(k, "")) for k in ("title", "body", "text", "name", "title"))
        s = score_item(text, horizon=horizon)
        ranked.append({**it, "score": s["score"], "confidence": s["confidence"], "reasons": s["reasons"]})
    ranked.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return ranked
