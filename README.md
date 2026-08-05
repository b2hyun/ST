# img2code — 이미지 ↔ Python 코드 변환기

이미지를 Python 코드로 변환하고, 그 코드를 실행하면 원본 이미지가 그대로 복원됩니다.

```
이미지 파일 ──(img2code.py)──▶ Python 스크립트 ──(실행)──▶ 이미지 파일
```

## 설치

```bash
pip install Pillow
```

## 사용법

### 1. 이미지 → Python 코드

```bash
python img2code.py photo.png
# → photo_generated.py 생성
```

### 2. Python 코드 → 이미지

```bash
python photo_generated.py
# → photo_restored.png 생성 (원본과 픽셀 단위로 동일)

python photo_generated.py -o other_name.png   # 출력 파일명 지정
```

## 변환 모드

| 모드 | 설명 | 적합한 경우 |
|------|------|-------------|
| `embed` (기본) | 이미지 데이터를 압축·인코딩해 코드에 내장 | 사진 등 모든 이미지. 코드 크기가 작음 |
| `draw` | PIL `ImageDraw`로 픽셀 구간을 한 줄씩 그리는 코드 생성 | 색 수가 적은 아이콘·도형. 코드가 사람이 읽을 수 있는 형태 |

```bash
python img2code.py icon.png --mode draw -o icon_draw.py
python icon_draw.py -o icon_restored.png
```

두 모드 모두 **무손실**입니다 — 복원된 이미지는 원본과 픽셀 단위로 완전히 동일합니다.

## 지원 형식

PNG, JPEG, BMP, GIF 등 Pillow가 읽을 수 있는 모든 형식을 입력으로 받습니다.
복원 시 출력 형식은 `-o` 확장자를 따릅니다 (기본 PNG).
