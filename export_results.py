import argparse
from pathlib import Path

import pandas as pd

from wikirecommender import WikipediaRecommender


def main():
    parser = argparse.ArgumentParser(description="Export two next-article recommendation examples.")
    parser.add_argument("model_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    model = WikipediaRecommender.load_from_file(str(args.model_csv))
    ml = "https://en.wikipedia.org/wiki/Machine_learning"
    ai = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    cases = [("one_article", [ml]), ("two_articles", [ml, ai])]
    tables = []
    for case, inputs in cases:
        query = inputs[0] if len(inputs) == 1 else inputs
        ranked = model.recommend(query, include_provided_urls=False)
        top = ranked.head(5).rename(columns={"URL": "recommended_url", "Similarity": "cosine_similarity"})
        assert len(top) == 5 and top["recommended_url"].is_unique
        assert not set(inputs).intersection(top["recommended_url"])
        assert top["cosine_similarity"].between(0, 1 + 1e-12).all()
        assert top["cosine_similarity"].is_monotonic_decreasing
        top = top.rename_axis("rank").reset_index()
        top.insert(0, "input_urls", " | ".join(inputs))
        top.insert(0, "case", case)
        tables.append(top)
    combined = pd.concat(tables, ignore_index=True)
    combined.to_csv(args.output_csv, index=False, float_format="%.12f")
    print(f"Indexed pages: {len(model.dataset)}, distinct URLs: {model.dataset['wikipedia_url'].nunique()}")
    print(combined[["case", "rank", "recommended_url", "cosine_similarity"]].to_string(index=False))


if __name__ == "__main__":
    main()
