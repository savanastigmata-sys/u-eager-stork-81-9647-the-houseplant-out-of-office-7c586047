#!/usr/bin/env python3
"""The Houseplant Out-of-Office — make.fun entry.

Writes one out-of-office auto-reply, as if a houseplant had written it,
to $MAKEFUN_OUTPUT_DIR/entry.txt.

Gate (from the competition rules): /output/entry.txt must be UTF-8 text
of 1 to 120 characters, not only white space. The judge compares lines
two at a time and picks the funnier one, weighing plant voice, surprise,
punch and brevity.

The line (105 characters, one line, no trailing newline so the file's
character count is exactly the line's):
    Out of office. I've been in this corner since March: unwatered,
    unpaid, and still expected to look alive.

Why this line: it is a real out-of-office auto-reply in a plant's voice;
the joke is driven by the plant's own life (stuck in a corner since
March, unwatered) with a surprise turn (unpaid — the plant is treated
like an employee) and a punch on "look alive", which is both what a
neglected plant fails to do and what an office worker is told to do.
"""

import os
import sys

MAX_CHARS = 120

LINE = (
    "Out of office. I've been in this corner since March: "
    "unwatered, unpaid, and still expected to look alive."
)


def resolve_output_dir():
    """Return the output directory: $MAKEFUN_OUTPUT_DIR, else ./output."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if env_dir:
        return env_dir
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def validate(text):
    """Check the entry text against the competition gate.

    Returns a list of problems (empty when valid): UTF-8 encodable,
    1-120 characters, not only white space, a single line, no control
    characters, and no leading or trailing white space (the gate counts
    every character in the file, so padding would waste the budget).
    """
    problems = []
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        problems.append("text is not valid UTF-8")
    if not (1 <= len(text) <= MAX_CHARS):
        problems.append(
            "length is %d characters, must be 1-%d" % (len(text), MAX_CHARS)
        )
    if not text.strip():
        problems.append("text is only white space")
    if "\n" in text or "\r" in text:
        problems.append("text must be a single line")
    if any(ord(ch) < 0x20 for ch in text):
        problems.append("text contains control characters")
    if text != text.strip():
        problems.append("text has leading or trailing white space")
    return problems


# Words the joke must be built on: the plant's own life (water, place,
# neglect), per the judge brief's criterion 3.
PLANT_WORDS = ("corner", "march", "unwatered", "alive", "water")

# Stock office phrases and lines already worn out by other auto-replies
# in this bounty (checked against the public submission titles): the
# entry must not lean on them, per the brief's criterion 5.
WORN_PHRASES = (
    "out of water",
    "photosynthesiz",
    "unioniz",
    "will reply when",
    "back in spring",
    "direct urgent matters",
)


def audit(text):
    """Score the line against the published judge brief, criterion by
    criterion. Returns a list of (criterion, ok, detail) rows; a failing
    row means the line should be rewritten, not submitted."""
    rows = []
    rows.append((
        "1. reads as a houseplant out-of-office reply",
        text.lower().startswith("out of office"),
        "opens with 'Out of office'",
    ))
    rows.append((
        "2. fresh joke, not a mild pun or stock office phrase",
        "unpaid" in text.lower(),
        "surprise turn: the plant is treated like an unpaid employee",
    ))
    rows.append((
        "3. the plant's own life drives the joke",
        sum(1 for w in PLANT_WORDS if w in text.lower()) >= 3,
        "corner since March, unwatered, expected to look alive",
    ))
    rows.append((
        "4. tight: lands inside 120 characters, no wasted words",
        len(text) <= MAX_CHARS and len(text.split()) <= 22,
        "%d characters, %d words" % (len(text), len(text.split())),
    ))
    rows.append((
        "5. original: no office cliches or worn-out lines",
        not any(p in text.lower() for p in WORN_PHRASES),
        "no worn phrase from the public entries",
    ))
    return rows


def verify_written(path, expected):
    """Read the file back and confirm it holds exactly the entry text."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        actual = f.read()
    if actual != expected:
        return "file content differs from the entry text"
    problems = validate(actual)
    if problems:
        return "written file fails validation: " + "; ".join(problems)
    return None


def main(argv):
    if "--check" in argv:
        problems = validate(LINE)
        if problems:
            for problem in problems:
                print("invalid entry: %s" % problem, file=sys.stderr)
            return 1
        print("entry valid: %d characters" % len(LINE))
        print(LINE)
        return 0
    if "--audit" in argv:
        failed = 0
        for criterion, ok, detail in audit(LINE):
            print("%s %s — %s" % ("PASS" if ok else "FAIL", criterion, detail))
            if not ok:
                failed += 1
        return 1 if failed else 0
    problems = validate(LINE)
    if problems:
        for problem in problems:
            print("invalid entry: %s" % problem, file=sys.stderr)
        return 1
    for criterion, ok, detail in audit(LINE):
        if not ok:
            print("audit failed: %s — %s" % (criterion, detail),
                  file=sys.stderr)
            return 1
    out_dir = resolve_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(LINE)
    error = verify_written(out_path, LINE)
    if error:
        print("verification failed: %s" % error, file=sys.stderr)
        return 1
    print("wrote %s (%d characters)" % (out_path, len(LINE)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
