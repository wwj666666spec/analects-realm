# -*- coding: utf-8 -*-
"""Export the deck to PDF and per-slide PNG via local PowerPoint."""

import os
import sys

import win32com.client


def main():
    pptx = os.path.abspath(sys.argv[1])
    pdf = os.path.abspath(sys.argv[2])
    png_dir = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else ""
    if png_dir:
        os.makedirs(png_dir, exist_ok=True)

    ppt = win32com.client.Dispatch("PowerPoint.Application")
    pres = ppt.Presentations.Open(pptx, WithWindow=False)
    try:
        pres.SaveAs(pdf, 32)
        print("pdf:", pdf)
        if png_dir:
            n = pres.Slides.Count
            for i in range(1, n + 1):
                out = os.path.join(png_dir, "slide-%02d.png" % i)
                pres.Slides.Item(i).Export(out, "PNG", 1600, 900)
            print("png count:", n)
    finally:
        pres.Close()
        ppt.Quit()


if __name__ == "__main__":
    main()
