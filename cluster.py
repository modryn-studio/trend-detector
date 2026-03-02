"""
cluster.py — group related keywords into macro trends

The pipeline scores keywords independently. But when 8 keywords all
point at the same problem ("friend app", "friend website", "where to
meet people", "third space near me"), that's a macro trend that's
stronger than any single keyword score suggests.

This module detects those clusters, scores them as a group, and
returns a ranked list with cluster context.
"""

import re
from collections import defaultdict

# Words too common to cluster on — would group everything together
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

# Minimum word length to count as a significant token
MIN_WORD_LEN = 3

# Minimum shared tokens for two keywords to be "related"
MIN_SHARED_TOKENS = 1

# Minimum cluster members to qualify as a macro trend
MIN_CLUSTER_SIZE = 3

# Semantic synonym groups — words that mean the same *problem*.
# If two keywords each contain a word from the same group, they share
# a token even if the literal words differ.
SYNONYM_GROUPS = [
    {"friend", "friends", "friendship", "people", "meet", "social",
     "lonely", "loneliness", "community", "connect", "connection"},
    {"space", "spaces", "place", "places", "coworking", "cafe", "coffee",
     "hub", "spot"},
    {"club", "clubs", "group", "groups"},
    {"volunteer", "volunteering", "charity", "donate"},
    {"travel", "trip", "flight", "flights", "hotel", "hotels",
     "vacation", "destination"},
    {"app", "tool", "website", "platform", "finder", "tracker"},
]

# Build a fast lookup: word -> canonical form (first word in group)
_SYNONYM_MAP: dict[str, str] = {}
for _group in SYNONYM_GROUPS:
    _canonical = sorted(_group)[0]  # deterministic canonical form
    for _word in _group:
        _SYNONYM_MAP[_word] = _canonical


def _stem(word: str) -> str:
    """Cheap stemming: strip common suffixes to normalize plurals, etc."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _tokenize(keyword: str) -> set[str]:
    """Extract significant words from a keyword, with stemming + synonyms."""
    words = re.findall(r'[a-z]+', keyword.lower())
    tokens = set()
    for w in words:
        if len(w) < MIN_WORD_LEN or w in STOP_WORDS:
            continue
        stemmed = _stem(w)
        # Map to synonym canonical form if it exists
        canonical = _SYNONYM_MAP.get(stemmed, _SYNONYM_MAP.get(w, stemmed))
        tokens.add(canonical)
    return tokens


def _similarity(tokens_a: set[str], tokens_b: set[str]) -> int:
    """Number of shared tokens between two keyword token sets."""
    return len(tokens_a & tokens_b)


def detect_clusters(scored_trends: list[dict],
                    min_shared: int = MIN_SHARED_TOKENS,
                    min_size: int = MIN_CLUSTER_SIZE) -> list[dict]:
    """
    Group scored trends into clusters based on keyword similarity.

    Returns a list of cluster dicts, sorted by cluster_score descending:
    {
        "cluster_name": "friend / social / people",
        "cluster_score": 78,
        "member_count": 8,
        "top_keyword": "friend app",
        "top_score": 62,
        "avg_score": 55,
        "growth_signals": ["all-time high", "breakout", "+290%"],
        "members": [... scored trend dicts ...],
    }
    """
    # Tokenize all keywords
    items = []
    for t in scored_trends:
        tokens = _tokenize(t["keyword"])
        if tokens:  # skip if no significant words
            items.append({"trend": t, "tokens": tokens, "assigned": False})

    # Build adjacency — which items share enough tokens
    n = len(items)
    adj = defaultdict(set)
    for i in range(n):
        for j in range(i + 1, n):
            shared = _similarity(items[i]["tokens"], items[j]["tokens"])
            if shared >= min_shared:
                adj[i].add(j)
                adj[j].add(i)

    # Greedy clustering — start from highest-connected nodes
    clusters: list[list[int]] = []
    for seed in sorted(range(n), key=lambda i: len(adj[i]), reverse=True):
        if items[seed]["assigned"]:
            continue
        # Start a cluster with this seed
        cluster = {seed}
        items[seed]["assigned"] = True

        # Add all directly connected unassigned nodes
        for neighbor in adj[seed]:
            if not items[neighbor]["assigned"]:
                # Check the neighbor connects to at least half the cluster
                # (prevents loose chains)
                connections = sum(1 for c in cluster if neighbor in adj[c])
                if connections >= max(1, len(cluster) // 3):
                    cluster.add(neighbor)
                    items[neighbor]["assigned"] = True

        # Second pass — check remaining unassigned for cluster fit
        for idx in range(n):
            if items[idx]["assigned"]:
                continue
            connections = sum(1 for c in cluster if idx in adj[c])
            if connections >= max(1, len(cluster) // 3):
                cluster.add(idx)
                items[idx]["assigned"] = True

        if len(cluster) >= min_size:
            clusters.append(sorted(cluster))

    # Build cluster records
    results = []
    for member_indices in clusters:
        members = [items[i]["trend"] for i in member_indices]
        scores = [m["score"] for m in members]
        avg = sum(scores) / len(scores)
        top = max(members, key=lambda m: m["score"])

        # Collect all significant tokens for naming
        all_tokens = set()
        for i in member_indices:
            all_tokens |= items[i]["tokens"]

        # Pick top 3 most frequent tokens across members as cluster name
        token_freq = defaultdict(int)
        for i in member_indices:
            for tok in items[i]["tokens"]:
                token_freq[tok] += 1
        top_tokens = sorted(token_freq, key=token_freq.get, reverse=True)[:3]
        cluster_name = " / ".join(top_tokens)

        # Gather growth signals from raw data
        growth_signals = []
        for m in members:
            gpct = m.get("_raw", {}).get("google_growth_pct", 0)
            if gpct >= 5000:
                growth_signals.append(f"{m['keyword']}: breakout")
            elif gpct >= 200:
                growth_signals.append(f"{m['keyword']}: +{gpct:.0f}%")

        # Cluster score: average member score + size bonus + growth bonus
        size_bonus = min(25, len(members) * 3)  # up to +25 for big clusters
        growth_bonus = min(15, len(growth_signals) * 5)  # up to +15 for growth
        cluster_score = min(100, round(avg + size_bonus + growth_bonus))

        results.append({
            "cluster_name":   cluster_name,
            "cluster_score":  cluster_score,
            "member_count":   len(members),
            "top_keyword":    top["keyword"],
            "top_score":      top["score"],
            "avg_score":      round(avg, 1),
            "growth_signals": growth_signals,
            "members":        members,
        })

    results.sort(key=lambda c: c["cluster_score"], reverse=True)
    return results


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
    # Fake data to test clustering
    test = [
        {"keyword": "friend app", "score": 60, "_raw": {"google_growth_pct": 5000}},
        {"keyword": "friend website", "score": 55, "_raw": {"google_growth_pct": 5000}},
        {"keyword": "how to make friends", "score": 50, "_raw": {"google_growth_pct": 290}},
        {"keyword": "where to meet people", "score": 48, "_raw": {"google_growth_pct": 5000}},
        {"keyword": "social clubs", "score": 52, "_raw": {"google_growth_pct": 5000}},
        {"keyword": "third space near me", "score": 45, "_raw": {"google_growth_pct": 0}},
        {"keyword": "digital third spaces", "score": 50, "_raw": {"google_growth_pct": 5000}},
        {"keyword": "bitcoin atm", "score": 71, "_raw": {"google_growth_pct": 1000}},
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
