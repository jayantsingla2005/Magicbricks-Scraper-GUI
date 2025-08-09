import csv
import json
from collections import Counter

def analyze_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    n = len(rows)
    cols = list(rows[0].keys()) if rows else []

    def nz(field: str) -> int:
        return sum(1 for r in rows if r.get(field, "").strip())

    non_empty = {c: nz(c) for c in cols}
    unique_urls = len({r.get("property_url", "") for r in rows if r.get("property_url", "").strip()})

    # Field coverage ratios for key fields
    key_fields = [
        "title", "price", "price_per_sqft", "carpet_area", "super_area", "area",
        "bedrooms", "bathrooms", "floor", "locality", "property_url", "image_urls"
    ]
    coverage = {k: (non_empty.get(k, 0) / n if n else 0.0) for k in key_fields}

    # Sample few rows (sanitized for readability)
    sample = [{k: r.get(k, "") for k in cols} for r in rows[:5]]

    # Top localities
    locs = [r.get("locality", "").strip() for r in rows if r.get("locality", "").strip()]
    top_localities = Counter(locs).most_common(10)

    result = {
        "total_rows": n,
        "columns": cols,
        "non_empty_counts": non_empty,
        "unique_urls": unique_urls,
        "coverage_ratios": coverage,
        "top_localities": top_localities,
        "sample_rows": sample,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    analyze_csv("magicbricks_gurgaon_properties_complete.csv")