import argparse
import sys

from rag.chunk import Chunk, build_chunks, sample_zhang, summarize
from rag.config import DATA_DIR


def cmd_chunk(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="只切块并打印统计，不入库")
    parser.add_argument("--zhang", default="1.1", help="打印这一章在各书里的开头")
    parser.add_argument("--sample", type=int, default=12)
    args = parser.parse_args(argv)
    chunks = build_chunks(DATA_DIR)
    print(summarize(chunks))
    print()
    print(sample_zhang(chunks, args.zhang, args.sample))
    print()
    print(alignment_line(chunks, "论语", "原文", "学而第一"))
    print(alignment_line(chunks, "论语集注", "注疏", "学而第一"))
    print(alignment_line(chunks, "论语注疏", "注疏", "学而第一"))
    print()
    print(coverage_lines(chunks))


def zhang_sort(zhang: str) -> tuple[int, int]:
    left, right = zhang.split(".")
    return int(left), int(right)


def alignment_line(chunks: list[Chunk], book: str, layer: str, pian: str) -> str:
    original = {
        chunk.zhang
        for chunk in chunks
        if chunk.layer == "原文" and chunk.pian == pian and chunk.zhang
    }
    got = {
        chunk.zhang
        for chunk in chunks
        if chunk.book == book and chunk.layer == layer and chunk.pian == pian and chunk.zhang
    }
    missing = sorted(original - got, key=zhang_sort)
    shown = "、".join(missing[:8]) if missing else "无"
    return f"{book} {pian}：对上 {len(got)}/{len(original)} 章，缺 {shown}"


def coverage_lines(chunks: list[Chunk]) -> str:
    original = {chunk.zhang for chunk in chunks if chunk.layer == "原文" and chunk.zhang}
    books: list[str] = []
    for chunk in chunks:
        if chunk.layer == "注疏" and chunk.book not in books:
            books.append(chunk.book)
    lines = []
    for book in books:
        got = {chunk.zhang for chunk in chunks if chunk.book == book and chunk.zhang}
        lines.append(f"{book} 章覆盖 {len(got)}/{len(original)}")
    return "\n".join(lines)


def main() -> None:
    commands = {
        "chunk": cmd_chunk,
        "ingest": None,
        "search": None,
        "ask": None,
        "round": None,
        "talk": None,
        "serve": None,
    }
    parser = argparse.ArgumentParser(prog="python -m rag", description="典籍切块、入库、检索")
    parser.add_argument("command", choices=sorted(commands))
    args, rest = parser.parse_known_args()
    if args.command == "chunk":
        cmd_chunk(rest)
        return
    if args.command == "ingest":
        from rag.ingest import main as ingest_main

        sys.argv = ["rag ingest", *rest]
        ingest_main()
        return
    if args.command == "ask":
        from rag.ask import main as ask_main

        sys.argv = ["rag ask", *rest]
        ask_main()
        return
    if args.command == "round":
        from rag.sage import main_round

        sys.argv = ["rag round", *rest]
        main_round()
        return
    if args.command == "talk":
        from rag.sage import main_talk

        sys.argv = ["rag talk", *rest]
        main_talk()
        return
    if args.command == "serve":
        from rag.server import main as serve_main

        serve_main()
        return
    from rag.search import main as search_main

    sys.argv = ["rag search", *rest]
    search_main()


if __name__ == "__main__":
    main()
