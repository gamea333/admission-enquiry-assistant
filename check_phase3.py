# check_phase3.py
from app.rag.generator import answer_query

TEST_QUERIES = [
    "What documents are required for admission?",
    "What are the fees for Grade 5?",
    "Is transport available near Koramangala?",       # seeded as unavailable
    "Is transport available near Jayanagar?",          # seeded as unavailable
    "Are seats available for Grade 3?",                 # seeded as full
    "Are seats available for LKG?",                      # seeded as open
    "What's the fee for Grade 5 and is transport available in Koramangala?",
    "Do you have a swimming pool?",                       # no data — should refuse
]

for i, q in enumerate(TEST_QUERIES, 1):
    print(f"\n{'='*70}")
    print(f"Q{i}: {q}")
    print('='*70)
    result = answer_query(q)
    print(f"\nANSWER:\n{result['answer']}")
    print(f"\nSOURCES: {result['sources']}")