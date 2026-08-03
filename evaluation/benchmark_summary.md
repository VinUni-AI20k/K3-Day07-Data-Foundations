# Semantic Benchmark Summary

- Python: `3.11.15`
- Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Vector dimension: `384`
- Corpus: 6 documents
- Queries: 5
- Top-k: 3
- Fallback: `False`

| Strategy | Member | Chunks | Hit@1 | Hit@3 | MRR | Precision@3 | Coherence | Grounding |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S1_RECURSIVE_450 | Trương Đình Khoa | 17 | 0.6000 | 1.0000 | 0.7667 | 0.3333 | 2.0000 | 1.6000 |
| S2_FIXED_450_50 | Diêm Công Thành | 17 | 0.6000 | 1.0000 | 0.8000 | 0.3333 | 1.0000 | 1.6000 |
| S3_SENTENCE_3 | Nguyễn Quang Huy | 15 | 0.6000 | 1.0000 | 0.7667 | 0.3333 | 2.0000 | 1.6000 |
| S1B_HEADING_RECURSIVE_450 | Trương Đình Khoa (thử nghiệm bổ sung) | 17 | 0.6000 | 1.0000 | 0.7667 | 0.3333 | 2.0000 | 1.6000 |

## Per-query evidence

| Query | Strategy | Top-1 correct | Top-3 evidence | Correct rank | Score | Document |
|---|---|---:|---:|---:|---:|---|
| Q1 | S1_RECURSIVE_450 | yes | yes | 1 | 0.734731 | k3-course-registration |
| Q2 | S1_RECURSIVE_450 | yes | yes | 1 | 0.745473 | k3-tuition-extension |
| Q3 | S1_RECURSIVE_450 | no | yes | 3 | 0.648734 | k3-bcu-scholarship-2026 |
| Q4 | S1_RECURSIVE_450 | yes | yes | 1 | 0.769018 | k3-dormitory-registration |
| Q5 | S1_RECURSIVE_450 | no | yes | 2 | 0.804110 | k3-health-insurance-2026 |
| Q1 | S2_FIXED_450_50 | yes | yes | 1 | 0.679393 | k3-course-registration |
| Q2 | S2_FIXED_450_50 | no | yes | 2 | 0.702119 | k3-tuition-extension |
| Q3 | S2_FIXED_450_50 | yes | yes | 1 | 0.816587 | k3-bcu-scholarship-2026 |
| Q4 | S2_FIXED_450_50 | yes | yes | 1 | 0.778972 | k3-dormitory-registration |
| Q5 | S2_FIXED_450_50 | no | yes | 2 | 0.634148 | k3-health-insurance-2026 |
| Q1 | S3_SENTENCE_3 | yes | yes | 1 | 0.677109 | k3-course-registration |
| Q2 | S3_SENTENCE_3 | no | yes | 3 | 0.668696 | k3-tuition-extension |
| Q3 | S3_SENTENCE_3 | yes | yes | 1 | 0.806809 | k3-bcu-scholarship-2026 |
| Q4 | S3_SENTENCE_3 | yes | yes | 1 | 0.746993 | k3-dormitory-registration |
| Q5 | S3_SENTENCE_3 | no | yes | 2 | 0.662585 | k3-health-insurance-2026 |
| Q1 | S1B_HEADING_RECURSIVE_450 | yes | yes | 1 | 0.734731 | k3-course-registration |
| Q2 | S1B_HEADING_RECURSIVE_450 | yes | yes | 1 | 0.745473 | k3-tuition-extension |
| Q3 | S1B_HEADING_RECURSIVE_450 | no | yes | 3 | 0.648734 | k3-bcu-scholarship-2026 |
| Q4 | S1B_HEADING_RECURSIVE_450 | yes | yes | 1 | 0.769018 | k3-dormitory-registration |
| Q5 | S1B_HEADING_RECURSIVE_450 | no | yes | 2 | 0.804110 | k3-health-insurance-2026 |

## Failure cases

- Q3 / S1_RECURSIVE_450: expected k3-bcu-scholarship-2026; complete evidence first appears at rank 3.
- Q5 / S1_RECURSIVE_450: expected k3-health-insurance-2026; complete evidence first appears at rank 2.
- Q2 / S2_FIXED_450_50: expected k3-tuition-extension; complete evidence first appears at rank 2.
- Q5 / S2_FIXED_450_50: expected k3-health-insurance-2026; complete evidence first appears at rank 2.
- Q2 / S3_SENTENCE_3: expected k3-tuition-extension; complete evidence first appears at rank 3.
- Q5 / S3_SENTENCE_3: expected k3-health-insurance-2026; complete evidence first appears at rank 2.
- Q3 / S1B_HEADING_RECURSIVE_450: expected k3-bcu-scholarship-2026; complete evidence first appears at rank 3.
- Q5 / S1B_HEADING_RECURSIVE_450: expected k3-health-insurance-2026; complete evidence first appears at rank 2.
