import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WORDS_FILE = os.path.join(ROOT, 'docs', 'words.json')
OUT_FILE = os.path.join(ROOT, 'data', 'fill_questions.json')

def is_candidate(word):
    if not word: return False
    # skip multi-word phrases
    if re.search(r"\s", word):
        return False
    # skip entries with punctuation or digits
    if re.search(r"[^A-Za-z'-]", word):
        return False
    # too short
    if len(re.sub("[^A-Za-z]", '', word)) < 3:
        return False
    return True

def make_sentences(word, subject):
    w = word
    # simple set of child-friendly templates; use underscore for blank
    templates = [
        f"I saw a _____ when I went outside.",
        f"Please give me the _____.",
        f"The _____ was on the table.",
    ]
    # For verbs ending with -ing or -ed, add an alternate template
    low = w.lower()
    if low.endswith('ing'):
        templates = [
            f"He was _____ behind the tree.",
            f"They are _____ in the yard.",
            f"Why are you _____ so fast?",
        ]
    elif low.endswith('ed'):
        templates = [
            f"She _____ very quickly.",
            f"They _____ the game yesterday.",
            f"Have you ever _____ before?",
        ]
    # Replace placeholder with blank (not answer) when presenting
    questions = []
    for t in templates[:3]:
        questions.append({
            'question': t.replace('_____', '_____'),
            'answer': w
        })
    return questions

def main():
    with open(WORDS_FILE, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    out = {}
    count_candidates = 0
    for month, blocks in data.items():
        for subject, words in blocks.items():
            for w in words:
                key = w.strip()
                if key in out:
                    out[key]['sources'].append({'month': month, 'subject': subject})
                    continue
                cand = is_candidate(key)
                qs = make_sentences(key, subject) if cand else []
                out[key] = {
                    'word': key,
                    'candidate': cand,
                    'questions': qs,
                    'sources': [{'month': month, 'subject': subject}]
                }
                if cand:
                    count_candidates += 1

    with open(OUT_FILE, 'w', encoding='utf-8') as fh:
        json.dump({'meta': {'total_words': len(out), 'candidates': count_candidates}, 'items': list(out.values())}, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT_FILE} — total words: {len(out)}, candidates: {count_candidates}")

if __name__ == '__main__':
    main()
