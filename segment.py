"""Segment the Mingshi with jieba, sentence by sentence.

Steps: convert Traditional -> Simplified with OpenCC, split into sentences on
。！？……, segment each sentence with jieba, and write one segmented sentence
per line to data/mingshi_segmented.txt.

Run from the repository root:  python segment.py
"""
import re

import jieba
from opencc import OpenCC

RAW = "data/mingshi.txt"
OUT = "data/mingshi_segmented.txt"

SENT_END = re.compile(r"([。！？\.!?……]+)")


def split_sentences(text):
    parts = SENT_END.split(text)
    sentences, buf = [], ""
    for part in parts:
        if SENT_END.fullmatch(part):
            buf += part
            if buf.strip():
                sentences.append(buf)
            buf = ""
        else:
            buf += part
    if buf.strip():
        sentences.append(buf)
    return sentences


def main():
    text = OpenCC("t2s").convert(open(RAW, encoding="utf-8").read())
    sentences = split_sentences(text)
    print(f"{len(sentences)} sentences")

    with open(OUT, "w", encoding="utf-8") as f:
        for sentence in sentences:
            tokens = [w for w in jieba.cut(sentence) if w.strip()]
            f.write(" ".join(tokens) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
