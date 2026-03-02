"""
cluster.py — group related keywords into macro trends

Two clustering strategies, applied in order:

1. Category clustering — keywords from the same email newsletter section
   (e.g. "Making Friends", "Third Places") are grouped together. Google
   already did the semantic work; we just use it. Works for ANY topic.

2. Token clustering — keywords sharing significant words get grouped.
   Uses basic stemming (plurals) but NO hardcoded synonym lists.
   "bitcoin atm" and "bitcoin fee calculator" share "bitcoin".
   This catches cross-source relationships the newsletter doesn't know about.

No domain-specific knowledge. Works the same whether the trend is
about loneliness, crypto, home security, or AI tutoring.
"""

import re
from collections import defaultdict

# Words too common to cluster on
STOP_WORDS = {
    "a", "an", "the", "of", "in", "to", "for", "and", "or", "is", "it",
    "at", "on", "as", "by", "my", "me", "do", "no", "so", "up", "if",
    "how", "what", "when", "where", "who", "why", "can", "are", "was",
    "not", "all", "you", "your", "with", "from", "that", "this", "will",
    "but", "more", "most", "very", "just", "than", "then", "also", "too",
    "much", "many", "some", "any", "each", "every", "been", "being",
    "have", "has", "had", "does", "did", "get", "got", "make", "made",
    "near", "best", "top", "new", "free", "after",
}

MIN_WORD_LEN = 3
MIN_SHARED_TOKENS = 1
MIN_CLUSTER_SIZE = 3

# Categories that are too vague to cluster on
SKIP_CATEGORIES = {"unknown", "technology", "finance", "health", ""}


def _stem(word: str) -> str:
    """Cheap stemming — normalize plurals and gerunds only."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _tokenize(keyword: str) -> set[str]:
    """Extract significant stemmed words. No synonym mapping."""
    words = re.findall(r'[a-z]+', keyword.lower())
    return {_stem(w) for w in words
            if len(w) >= MIN_WORD_LEN and w not in STOP_WORDS}



def detect_clusters(scored_trends: list[dict],
                    min_shared: int = MIN_SHARED_TOKENS,
                    min_size: int = MIN_CLUSTER_SIZE) -> list[dict]:
    """
    Group scored trends into clusters. Two passes:

    Pass 1: Category-based. Keywords sharing a specific newsletter section
            (category field from email_ingest) get grouped. Google already
            did the semantic analysis; we just use their groupings.

    Pass 2: Token-based. Remaining ungrouped keywords that share significant
            stemmed words get grouped. Catches cross-source relationships.

    Returns a list of cluster dicts, sorted by cluster_score descending.
    """
    assigned: set[int] = set()    # indices of trends already in a cluster
    clusters: list[dict] = []

    # --- Pass 1: Category clusters (from newsletter sections) ---
    cat_groups: dict[str, list[int]] = defaultdict(list)
    for i, t in enumerate(scored_trends):
        cat = t.get("category", "unknown")
        if cat.lower() not in SKIP_CATEGORIES:
            cat_groups[cat].append(i)

    for cat, indices in cat_groups.items():
        if len(indices) >= min_size:
            clusters.append(_build_cluster(scored_trends, indices, name=cat))
            assigned.update(indices)

    # --- Pass 2: Token clusters (remaining keywords) ---
    remaining = [(i, t) for i, t in enumerate(scored_trends)
                 if i not in assigned]

    if remaining:
        items = []
        for orig_idx, t in remaining:
            tokens = _tokenize(t["keyword"])
            if tokens:
                items.append({"orig_idx": orig_idx, "tokens": tokens})

        # Build adjacency
        n = len(items)
        adj = defaultdict(set)
        for i in range(n):
            for j in range(i + 1, n):
                shared = len(items[i]["tokens"] & items[j]["tokens"])
                if shared >= min_shared:
                    adj[i].add(j)
                    adj[j].add(i)

        # Greedy clustering
        local_assigned: set[int] = set()
        for seed in sorted(range(n), key=lambda i: len(adj[i]), reverse=True):
            if seed in local_assigned:
                continue
            cluster_local = {seed}
            local_assigned.add(seed)

            for neighbor in adj[seed]:
                if neighbor not in local_assigned:
                    connections = sum(1 for c in cluster_local if neighbor in adj[c])
                    if connections >= max(1, len(cluster_local) // 3):
                        cluster_local.add(neighbor)
                        local_assigned.add(neighbor)

            # Second pass for stragglers
            for idx in range(n):
                if idx in local_assigned:
                    continue
                connections = sum(1 for c in cluster_local if idx in adj[c])
                if connections >= max(1, len(cluster_local) // 3):
                    cluster_local.add(idx)
                    local_assigned.add(idx)

            if len(cluster_local) >= min_size:
                orig_indices = [items[i]["orig_idx"] for i in sorted(cluster_local)]
                clusters.append(_build_cluster(scored_trends, orig_indices))
                assigned.update(orig_indices)

    clusters.sort(key=lambda c: c["cluster_score"], reverse=True)
    return clusters


def _build_cluster(scored_trends: list[dict], indices: list[int],
                   name: str | None = None) -> dict:
    """Build a cluster record from member indices."""
    members = [scored_trends[i] for i in indices]
    scores = [m["score"] for m in members]
    avg = sum(scores) / len(scores)
    top = max(members, key=lambda m: m["score"])

    # Auto-name from most frequent tokens if no name given
    if not name:
        token_freq: dict[str, int] = defaultdict(int)
        for m in members:
            for tok in _tokenize(m["keyword"]):
                token_freq[tok] += 1
        top_tokens = sorted(token_freq, key=token_freq.get, reverse=True)[:3]
        name = " / ".join(top_tokens)

    # Growth signals
    growth_signals = []
    for m in members:
        gpct = m.get("_raw", {}).get("google_growth_pct", 0)
        if gpct >= 5000:
            growth_signals.append(f"{m['keyword']}: breakout")
        elif gpct >= 200:
            growth_signals.append(f"{m['keyword']}: +{gpct:.0f}%")

    # Cluster score: avg + size bonus + growth bonus
    size_bonus = min(25, len(members) * 3)
    growth_bonus = min(15, len(growth_signals) * 5)
    cluster_score = min(100, round(avg + size_bonus + growth_bonus))

    return {
        "cluster_name":   name,
        "cluster_score":  cluster_score,
        "member_count":   len(members),
        "top_keyword":    top["keyword"],
        "top_score":      top["score"],
        "avg_score":      round(avg, 1),
        "growth_signals": growth_signals,
        "members":        members,
    }


def get_unclustered(scored_trends: list[dict],
                    clusters: list[dict]) -> list[dict]:
    """Return trends that didn't land in any cluster."""
    clustered_kws = set()
    for c in clusters:
        for m in c["members"]:
            clustered_kws.add(m["keyword"].lower())

    return [t for t in scored_trends if t["keyword"].lower() not in clustered_kws]


# --- Standalone test ---
if __name__ == "__main__":
    # Simulate mixed data — categories from email + uncategorized from trendspy/RSS
    test = [
        # Email: same section -> category cluster
        {"keyword": "friend app", "score": 60, "category": "Making Friends",
         "_raw": {"google_growth_pct": 5000}},
        {"keyword": "friend website", "score": 55, "category": "Making Friends",
         "_raw": {"google_growth_pct": 5000}},
        {"keyword": "how to make friends", "score": 50, "category": "Making Friends",
         "_raw": {"google_growth_pct": 290}},
        {"keyword": "social groups", "score": 48, "category": "Making Friends",
         "_raw": {"google_growth_pct": 0}},
        # Email: different section
        {"keyword": "third space near me", "score": 45, "category": "Third Places",
         "_raw": {"google_growth_pct": 0}},
        {"keyword": "digital third spaces", "score": 50, "category": "Third Places",
         "_raw": {"google_growth_pct": 5000}},
        {"keyword": "coworking spaces", "score": 44, "category": "Third Places",
         "_raw": {"google_growth_pct": 0}},
        # Trendspy: no useful category -> token clustering
        {"keyword": "bitcoin atm", "score": 71, "category": "finance",
         "_raw": {"google_growth_pct": 1000}},
        {"keyword": "bitcoin fee calculator", "score": 55, "category": "finance",
         "_raw": {"google_growth_pct": 500}},
        {"keyword": "bitcoin price tracker", "score": 50, "category": "finance",
         "_raw": {"google_growth_pct": 300}},
        # Lone wolf
        {"keyword": "spacex launch today", "score": 62, "category": "unknown",
         "_raw": {"google_growth_pct": 900}},
    ]

    clusters = detect_clusters(test, min_size=2)
    for c in clusters:
        print(f"\n  CLUSTER: {c['cluster_name']}  score={c['cluster_score']}  "
              f"members={c['member_count']}")
        for m in c["members"]:
            print(f"    - {m['keyword']} (score={m['score']})")

    unclustered = get_unclustered(test, clusters)
    if unclustered:
        print("\n  UNCLUSTERED:")
        for t in unclustered:
            print(f"    - {t['keyword']} (score={t['score']})")
