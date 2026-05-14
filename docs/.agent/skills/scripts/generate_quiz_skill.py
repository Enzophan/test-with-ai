import csv
import re
from difflib import SequenceMatcher
from pathlib import Path


def parse_questions(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    m_num = re.search(r"(?m)^\s*1\.\s+", text)
    legacy_text = text[: m_num.start()] if m_num else text
    numbered_text = text[m_num.start() :] if m_num else ""

    questions = []
    opt_re = re.compile(r"^\s*([A-Z])(?:\.|\t)\s*(.+?)\s*$")

    def next_nonempty(lines, idx):
        j = idx
        while j < len(lines) and not lines[j].strip():
            j += 1
        return j if j < len(lines) else None

    def is_label(s):
        x = s.strip().lower()
        return x == "correct answer" or x == "explanation"

    def is_question_start(lines, idx):
        s = lines[idx].strip()
        if not s or is_label(s) or opt_re.match(s):
            return False
        j = next_nonempty(lines, idx + 1)
        if j is None:
            return False
        return opt_re.match(lines[j].strip()) is not None

    # Parse legacy blocks.
    lines = legacy_text.split("\n")
    i = 0
    while i < len(lines):
        if not is_question_start(lines, i):
            i += 1
            continue

        q = lines[i].strip()
        i = next_nonempty(lines, i + 1) or len(lines)

        opts = []
        while i < len(lines):
            s = lines[i].strip()
            m = opt_re.match(s)
            if not m:
                break
            opts.append((m.group(1), m.group(2)))
            i += 1
            i = next_nonempty(lines, i) or len(lines)

        while i < len(lines) and lines[i].strip().lower() != "correct answer":
            i += 1
        if i >= len(lines):
            break

        i = next_nonempty(lines, i + 1)
        corr = lines[i].strip() if i is not None else ""
        i = (i + 1) if i is not None else len(lines)

        while i < len(lines) and lines[i].strip().lower() != "explanation":
            i += 1
        i = next_nonempty(lines, i + 1) if i < len(lines) else len(lines)

        expl_parts = []
        while i is not None and i < len(lines) and not is_question_start(lines, i):
            s = lines[i].strip()
            if s and not is_label(s):
                expl_parts.append(s)
            i = next_nonempty(lines, i + 1)

        corr_letter = None
        corr_text = ""
        m = re.match(r"^([A-Z])(?:\.|\t)?\s*(.*)$", corr)
        if m:
            corr_letter = m.group(1)
            corr_text = m.group(2).strip()
        if not corr_text and corr_letter:
            for letter, txt in opts:
                if letter == corr_letter:
                    corr_text = txt
                    break
        if not corr_text:
            corr_text = corr

        if opts:
            questions.append(
                {
                    "q": q,
                    "options": opts,
                    "correct_letter": corr_letter,
                    "correct_text": corr_text,
                    "explanation": " ".join(expl_parts).strip(),
                }
            )

        if i is None:
            break

    # Parse numbered blocks.
    pat_b = re.compile(
        r"(?ms)^\s*(\d+)\.\s+([^\n]+)\s*\n"
        r"((?:\s*[A-Z]\.\s*[^\n]+\n)+)"
        r"\s*✓\s*Correct Answer:\s*([A-Z])\s*\n"
        r"\s*Explanation:\s*(.+?)(?=\n\s*\d+\.\s+[^\n]+\n|\Z)"
    )
    for m in pat_b.finditer(numbered_text):
        q = m.group(2).strip()
        opts = []
        for ln in m.group(3).split("\n"):
            s = ln.strip()
            mo = re.match(r"^([A-Z])\.\s*(.+)$", s)
            if mo:
                opts.append((mo.group(1), mo.group(2).strip()))

        corr_letter = m.group(4).strip()
        corr_text = ""
        for letter, txt in opts:
            if letter == corr_letter:
                corr_text = txt
                break

        raw_expl = m.group(5).strip()
        for marker in [
            "Excellent! We have 50 questions.",
            "</think>Here is",
            "Here is a comprehensive set of 50",
            "📋 Quality Assurance Quiz (50 Questions)",
        ]:
            if marker in raw_expl:
                raw_expl = raw_expl.split(marker, 1)[0].strip()

        questions.append(
            {
                "q": q,
                "options": opts,
                "correct_letter": corr_letter,
                "correct_text": corr_text,
                "explanation": " ".join(raw_expl.split()),
            }
        )

    # Exact de-dup by question text.
    seen = set()
    uniq = []
    for it in questions:
        if it["q"] in seen:
            continue
        seen.add(it["q"])
        uniq.append(it)
    questions = uniq

    # Remove near-duplicate non-ASCII corrupted variants.
    filtered = []
    for i, it in enumerate(questions):
        q = it["q"]
        if any(ord(ch) > 127 for ch in q):
            skip = False
            for j, other in enumerate(questions):
                if i == j:
                    continue
                oq = other["q"]
                if any(ord(ch) > 127 for ch in oq):
                    continue
                if SequenceMatcher(None, q, oq).ratio() >= 0.9:
                    skip = True
                    break
            if skip:
                continue
        filtered.append(it)

    return filtered


def write_outputs(root: Path, questions):
    answer_rows = []
    quiz_rows = []
    next_id = 1

    for it in questions:
        id_by = {}
        for letter, opt in it["options"]:
            aid = f"Answer {next_id}"
            next_id += 1
            answer_rows.append([it["q"], aid, opt, ""])
            id_by[letter] = aid

        quiz_rows.append(
            [
                it["q"],
                it["explanation"],
                id_by.get(it["correct_letter"], ""),
                it["correct_text"],
            ]
        )

    with (root / "Answers_skill.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Question text", "Answer ID", "Quiz Answer Description", ""])
        w.writerows(answer_rows)

    with (root / "Quiz_skill.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Question text", "Explannation", "Correct Answer ID", " Correct Answer"])
        w.writerows(quiz_rows)

    return len(answer_rows), len(quiz_rows)


def main():
    root = Path(__file__).resolve().parents[3]
    text_path = root / "text.txt"

    if not text_path.exists():
        raise FileNotFoundError(f"Missing input file: {text_path}")

    text = text_path.read_text(encoding="utf-8", errors="ignore")
    questions = parse_questions(text)
    answer_count, quiz_count = write_outputs(root, questions)

    print(f"Questions={len(questions)} Answers={answer_count} QuizRows={quiz_count}")


if __name__ == "__main__":
    main()
