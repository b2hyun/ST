#!/usr/bin/env python3
"""이미지를 Python 코드로 변환하는 도구.

생성된 Python 스크립트를 실행하면 원본 이미지가 그대로 복원됩니다.

사용법:
    python img2code.py input.png                    # input_generated.py 생성
    python img2code.py input.png -o my_image.py     # 출력 파일명 지정
    python img2code.py input.png --mode draw        # 픽셀을 직접 그리는 코드 생성

모드:
    embed (기본): 이미지 데이터를 압축해 코드에 내장. 어떤 이미지든 무손실 복원.
    draw: PIL ImageDraw로 픽셀을 한 줄씩 그리는 코드를 생성. 코드가 사람이
          읽을 수 있는 형태이지만, 색이 많은 사진은 파일이 커질 수 있음.
"""

import argparse
import base64
import io
import sys
import textwrap
import zlib
from pathlib import Path

from PIL import Image

EMBED_TEMPLATE = '''\
#!/usr/bin/env python3
"""{source_name} 이미지를 복원하는 자동 생성 스크립트.

실행하면 원본 이미지가 무손실로 복원됩니다:
    python {script_name} [-o 출력파일.png]
"""

import argparse
import base64
import io
import zlib

from PIL import Image

# 원본: {source_name} ({width}x{height}, {mode})
DATA = (
{data_literal}
)


def build_image() -> Image.Image:
    raw = zlib.decompress(base64.b85decode(DATA))
    return Image.open(io.BytesIO(raw))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default="{default_output}",
                        help="저장할 이미지 경로 (기본: %(default)s)")
    args = parser.parse_args()
    image = build_image()
    image.save(args.output)
    print(f"이미지 복원 완료: {{args.output}} ({{image.width}}x{{image.height}})")


if __name__ == "__main__":
    main()
'''

DRAW_TEMPLATE = '''\
#!/usr/bin/env python3
"""{source_name} 이미지를 픽셀 단위로 다시 그리는 자동 생성 스크립트.

실행하면 원본과 동일한 이미지를 그려서 저장합니다:
    python {script_name} [-o 출력파일.png]
"""

import argparse

from PIL import Image, ImageDraw

WIDTH, HEIGHT = {width}, {height}

# 각 항목: (y, x_start, x_end, (r, g, b, a)) — 같은 색이 이어지는 가로 구간
RUNS = [
{runs_literal}
]


def build_image() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for y, x0, x1, color in RUNS:
        draw.line([(x0, y), (x1, y)], fill=color)
    return image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default="{default_output}",
                        help="저장할 이미지 경로 (기본: %(default)s)")
    args = parser.parse_args()
    image = build_image()
    image.save(args.output)
    print(f"이미지 복원 완료: {{args.output}} ({{image.width}}x{{image.height}})")


if __name__ == "__main__":
    main()
'''


def make_embed_code(image_path: Path, script_name: str, default_output: str) -> str:
    """이미지 파일을 PNG로 정규화한 뒤 압축·인코딩해 코드에 내장한다."""
    with Image.open(image_path) as im:
        width, height, mode = im.width, im.height, im.mode
        buffer = io.BytesIO()
        im.save(buffer, format="PNG")
    encoded = base64.b85encode(zlib.compress(buffer.getvalue(), 9)).decode("ascii")
    lines = textwrap.wrap(encoded, 88)
    data_literal = "\n".join(f'    "{line}"' for line in lines)
    return EMBED_TEMPLATE.format(
        source_name=image_path.name,
        script_name=script_name,
        width=width,
        height=height,
        mode=mode,
        data_literal=data_literal,
        default_output=default_output,
    )


def make_draw_code(image_path: Path, script_name: str, default_output: str) -> str:
    """이미지를 가로 방향 같은 색 구간(run)으로 나눠 그리는 코드를 만든다."""
    with Image.open(image_path) as im:
        rgba = im.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()

    runs = []
    for y in range(height):
        x = 0
        while x < width:
            color = pixels[x, y]
            end = x
            while end + 1 < width and pixels[end + 1, y] == color:
                end += 1
            runs.append((y, x, end, color))
            x = end + 1

    runs_literal = "\n".join(
        f"    ({y}, {x0}, {x1}, {color!r})," for y, x0, x1, color in runs
    )
    return DRAW_TEMPLATE.format(
        source_name=image_path.name,
        script_name=script_name,
        width=width,
        height=height,
        runs_literal=runs_literal,
        default_output=default_output,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="이미지를 Python 코드로 변환합니다. "
        "생성된 코드를 실행하면 이미지가 복원됩니다."
    )
    parser.add_argument("image", type=Path, help="변환할 이미지 파일")
    parser.add_argument("-o", "--output", type=Path,
                        help="생성할 Python 파일 (기본: <이미지이름>_generated.py)")
    parser.add_argument("--mode", choices=["embed", "draw"], default="embed",
                        help="embed: 데이터 내장(기본, 모든 이미지에 적합) / "
                             "draw: 픽셀을 직접 그리는 코드 생성")
    args = parser.parse_args()

    if not args.image.is_file():
        sys.exit(f"오류: 이미지 파일을 찾을 수 없습니다: {args.image}")

    output = args.output or args.image.with_name(f"{args.image.stem}_generated.py")
    default_output = f"{args.image.stem}_restored.png"

    if args.mode == "embed":
        code = make_embed_code(args.image, output.name, default_output)
    else:
        code = make_draw_code(args.image, output.name, default_output)

    output.write_text(code, encoding="utf-8")
    print(f"코드 생성 완료: {output}")
    print(f"복원 방법: python {output} -o {default_output}")


if __name__ == "__main__":
    main()
