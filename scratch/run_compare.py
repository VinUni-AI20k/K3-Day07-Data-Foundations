from src.chunking import ChunkingStrategyComparator
import glob

comparator = ChunkingStrategyComparator()
files = sorted(glob.glob("data/k3_university/hust-*.md"))

for path in files:  # compare all docs
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    res = comparator.compare(text, chunk_size=300)
    print("File: {}".format(path))
    for strategy, metrics in res.items():
        print("  {}: count={} avg_len={:.1f}".format(strategy, metrics["count"], metrics["avg_length"]))
