"""
extract_dict.py — Sinh file Prompt để nạp từ điển Oxford A1–C1 vào hệ thống.

Chiến lược:
  - Đọc CSV (word, pos, pronunciation, meaning_vi) theo từng CEFR level.
  - Chia thành batch 50 từ mỗi prompt (có thể thay đổi).
  - PK toàn cục: tịnh tiến liên tục qua tất cả file (A1 → A2 → B1 → B2 → C1).
  - Mỗi prompt yêu cầu LLM làm giàu dữ liệu: gán domain, bổ sung definition_en,
    example_en/vi, collocations, synonyms, antonyms, mnemonic.

Cách dùng:
  1. Kiểm tra max pk hiện tại trong DB:
       cd /home/n2t/Documents/english_study/backend
       ../.venv/bin/python manage.py shell -c \
         "from apps.vocabulary.models import Word; w=Word.objects.order_by('-pk').first(); print('Max pk:', w.pk if w else 0)"

  2. Đặt PK_GLOBAL_OFFSET = (max_pk + 1) bên dưới, sau đó chạy:
       python extract_dict.py

  3. Các file prompt sẽ được lưu vào thư mục prompts/.
     Paste từng prompt vào ChatGPT/Claude → lấy JSON → lưu vào
     backend/apps/vocabulary/fixtures/<tên_file>.json
     rồi chạy loaddata.
"""

import os
import math
import pandas as pd

# ── CẤU HÌNH ──────────────────────────────────────────────────────────────────
# Tự động detect thư mục script để tìm CSV files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Đặt bằng (max_pk_trong_db + 1) trước khi chạy
PK_GLOBAL_OFFSET = 101

BATCH_SIZE = 50          # số từ mỗi prompt (~50 tốt hơn 100 để LLM không bỏ sót)
OUTPUT_DIR = "prompts"   # thư mục lưu file prompt

# Thứ tự file: quan trọng — PK sẽ tịnh tiến theo đúng thứ tự này
CSV_FILES = [
    ("A1.csv", "A1"),
    ("A2.csv", "A2"),
    ("B1.csv", "B1"),
    ("B2.csv", "B2"),
    ("C1.csv", "C1"),
]

# Domain hợp lệ (phải khớp với DOMAINS trong VocabularyView.vue)
VALID_DOMAINS = [
    "general", "everyday", "business", "technology",
    "academic", "medical", "health", "travel",
    "food", "vegetables", "animals", "nature", "art",
]

# ── Mapping POS từ viết tắt CSV → giá trị trong model ──────────────────────
POS_MAP = {
    "n": "noun", "noun": "noun",
    "v": "verb", "verb": "verb", "modal verb": "verb", "modal": "verb",
    "adj": "adjective", "adjective": "adjective",
    "adv": "adverb", "adverb": "adverb",
    "phrase": "phrase", "phrasal verb": "phrase", "idiom": "phrase",
    "prep": "other", "conj": "other", "det": "other",
    "pron": "other", "pronoun": "other", "number": "other",
    "exclamation": "other", "preposition": "other", "determiner": "other",
}

def map_pos(raw: str) -> str:
    """Chuyển POS viết tắt/đầy đủ sang giá trị model. Lấy part đầu tiên nếu có dấu phẩy."""
    if not raw or pd.isna(raw):
        return "other"
    first = raw.strip().split(",")[0].strip().lower()
    return POS_MAP.get(first, "other")


# ── Mẫu JSON fixture dùng để minh hoạ trong prompt ──────────────────────────
TEMPLATE_INPUT = """\
PHẦN 1: DỮ LIỆU TỪ CSV (fixed — KHÔNG thay đổi):
  "pk": 101,                          [từ CSV]
  "word": "apple",                    [từ CSV]
  "part_of_speech": "noun",           [từ CSV]
  "ipa_uk": "ˈæp.əl",                 [từ CSV]
  "meaning_vi": "quả táo",            [từ CSV]

PHẦN 2: PLACEHOLDER CẦN ĐIỀN BỞI LLM:
  "ipa_us": "<IPA US — nếu khác UK, không thì copy ipa_uk>",
  "definition_en": "<1–2 câu tiếng Anh đơn giản>",
  "example_en": "<câu ví dụ có dùng từ này>",
  "example_vi": "<dịch ví dụ sang Việt>",
  "collocations_json": ["<cụm từ 1>", "<cụm từ 2>", "<cụm từ 3>"],
  "synonyms_json": ["<từ đồng nghĩa 1>", "<từ đồng nghĩa 2>"],
  "antonyms_json": ["<từ trái nghĩa 1>"],
  "mnemonic": "<1 câu gợi nhớ sáng tạo>",
  "frequency_rank": <1–15000>,
  "register": null,  [hoặc "formal"|"informal"|"slang"|"academic"]

PHẦN 3: FIXED VALUES (không thay đổi):
  "model": "vocabulary.word",
  "audio_uk_s3_key": null,
  "audio_us_s3_key": null,
  "image_key": null,
  "is_oxford_3000": true,    [A1/A2/B1 = true, B2/C1 = false]
  "is_oxford_5000": true,    [A1–B2 = true, C1 = false]
  "created_at": "2026-03-25T00:00:00Z"\
"""

FIXTURE_EXAMPLE = """\
[
  {
    "model": "vocabulary.word",
    "pk": 101,
    "fields": {
      "word": "apple",
      "part_of_speech": "noun",
      "cefr_level": "A1",
      "domain": "food",
      "ipa_uk": "ˈæp.əl",
      "ipa_us": "ˈæp.əl",
      "audio_uk_s3_key": null,
      "audio_us_s3_key": null,
      "meaning_vi": "quả táo",
      "definition_en": "A round fruit with red, green, or yellow skin and firm white flesh.",
      "example_en": "She eats an apple every morning.",
      "example_vi": "Cô ấy ăn một quả táo mỗi sáng.",
      "collocations_json": ["apple juice", "apple pie", "fresh apple", "an apple a day"],
      "synonyms_json": [],
      "antonyms_json": [],
      "mnemonic": "Think of the letter A — the first letter of the alphabet, just like apple is the first fruit most people learn.",
      "frequency_rank": 500,
      "register": null,
      "image_key": null,
      "is_oxford_3000": true,
      "is_oxford_5000": true,
      "created_at": "2026-03-25T00:00:00Z"
    }
  }
]"""


def build_word_table(batch_rows: list[dict]) -> str:
    """Tạo bảng từ với dữ liệu đã biết từ CSV để nhúng vào prompt."""
    lines = ["| pk | word | part_of_speech | ipa_uk |",
             "|----|------|---------------|--------|"]
    for row in batch_rows:
        lines.append(
            f"| {row['pk']} | {row['word']} | {row['pos_mapped']} "
            f"| {row['ipa']} |"
        )
    return "\n".join(lines)


def generate_prompt(batch_rows: list[dict], cefr_level: str, batch_num: int,
                    total_batches: int, file_label: str) -> str:
    word_table = build_word_table(batch_rows)
    start_pk = batch_rows[0]['pk']
    end_pk   = batch_rows[-1]['pk']
    count    = len(batch_rows)

    return f"""\
# NHIỆM VỤ: Sinh Django JSON Fixture — {file_label} Batch {batch_num}/{total_batches}

Bạn là chuyên gia ngôn ngữ học và kỹ sư dữ liệu.
Làm giàu dữ liệu (data enrichment) cho **{count} từ tiếng Anh trình độ {cefr_level}** bên dưới.
Dữ liệu đầu vào đã có sẵn: pk, word, part_of_speech, ipa_uk.
Bạn cần **bổ sung TẤT CẢ** các trường còn lại theo đúng quy tắc dưới đây.

---
## DỮ LIỆU ĐẦU VÀO (đã biết — KHÔNG thay đổi):

{word_table}

---
## QUY TẮC BỔ SUNG:

### 1. domain
Gán MỘT domain phù hợp nhất từ danh sách sau (chỉ dùng đúng giá trị này, viết thường):
`general` | `everyday` | `business` | `technology` | `academic` | `medical` | `health` | `travel` | `food` | `vegetables` | `animals` | `nature` | `art`

Hướng dẫn gán domain:
- **general**: từ chức năng/từ cơ bản không thuộc ngữ cảnh cụ thể (about, after, again, can, do, good, big…)
- **everyday**: đời sống hằng ngày, gia đình, nhà cửa, cảm xúc, thời gian (morning, family, happy, house…)
- **business**: kinh tế, tài chính, marketing, công ty (price, market, report, profit…)
- **technology**: máy tính, internet, phần mềm (computer, software, wifi, data…)
- **academic**: giáo dục, nghiên cứu, khoa học (theory, analysis, evidence…)
- **medical**: y tế, bệnh viện, thuốc (doctor, medicine, symptom…)
- **health**: lối sống, thể dục, dinh dưỡng (exercise, diet, sleep…)
- **travel**: di chuyển, địa điểm, du lịch (airport, hotel, map, ticket…)
- **food**: ẩm thực, nấu ăn, thức uống (cooking, recipe, soup, juice, restaurant…)
- **vegetables**: rau xanh, quả, nguyên liệu nấu ăn (apple, rice, carrot, bread, flour…)
- **animals**: động vật, côn trùng, sinh vật hoang dã (dog, cat, fish, bird, insect…)
- **nature**: thiên nhiên, địa lý, thời tiết, cảnh quan (rain, mountain, river, sea, wind…)
- **art**: nghệ thuật, âm nhạc, hội hoạ, văn học (music, paint, novel, dance…)

### 2. ipa_us
Nếu IPA Mỹ khác IPA Anh, điền đúng. Nếu giống hệt thì copy ipa_uk.

### 3. definition_en
1–2 câu tiếng Anh đơn giản, phù hợp trình độ {cefr_level}.

### 4. example_en / example_vi
Câu ví dụ tiếng Anh có dùng đúng từ đó. Dịch sang tiếng Việt tự nhiên.

### 5. collocations_json
Mảng 3–5 cụm từ hay gặp (string). Ví dụ: ["go to school", "school bus", "after school"]

### 6. synonyms_json / antonyms_json
Mảng string, 1–3 từ đồng nghĩa/trái nghĩa. Để [] nếu không có.

### 7. mnemonic
1 câu gợi nhớ vui, sáng tạo bằng tiếng Việt hoặc tiếng Anh.

### 8. frequency_rank
Ước lượng hạng tần suất (1 = phổ biến nhất). Từ A1 thường 1–2000, C1 thường 5000–15000.

### 9. Các trường cố định (giữ nguyên):
- `audio_uk_s3_key`, `audio_us_s3_key`, `image_key`: null
- `register`: null (trừ khi từ rõ ràng là formal/informal/slang/academic)
- `is_oxford_3000`: true nếu trình độ A1/A2/B1, false nếu B2/C1
- `is_oxford_5000`: true nếu trình độ A1–B2, false nếu C1
- `created_at`: "2026-03-25T00:00:00Z"

---
## FORMAT ĐẦU RA:

Trả về **CHỈ** một JSON array hợp lệ (không có text thêm), bọc trong block ```json ... ```.
Số lượng object: đúng **{count}** (pk từ {start_pk} đến {end_pk}, KHÔNG thêm, KHÔNG bỏ).

### HƯỚNG DẪN ĐIỀN:

**Dữ liệu từ CSV (KHÔNG thay đổi):**
- "pk", "word", "part_of_speech", "ipa_uk"

**Dữ liệu cần điền bởi LLM:**
- "domain": gán theo hướng dẫn mục 1
- "meaning_vi": nghĩa tiếng Việt ngắn gọn (3–8 từ)
- "ipa_us": IPA Mỹ (hoặc copy ipa_uk nếu giống)
- "definition_en", "example_en", "example_vi", "collocations_json", "synonyms_json", "antonyms_json", "mnemonic", "frequency_rank", "register"

**Dữ liệu cố định:**
- model: "vocabulary.word"
- audio_uk_s3_key, audio_us_s3_key, image_key: null
- is_oxford_3000: true (A1/A2/B1), false (B2/C1)
- is_oxford_5000: true (A1–B2), false (C1)
- created_at: "2026-03-25T00:00:00Z"

### MẪU THAM KHẢO (1 object hoàn chỉnh):
```json
{FIXTURE_EXAMPLE}
```

> ⚠️ QUAN TRỌNG:
> - Giữ đúng "pk" từ bảng đầu vào. KHÔNG thay đổi pk, word, part_of_speech, ipa_uk.
> - "model" luôn là "vocabulary.word"
> - "domain" phải là đúng 1 trong 13 giá trị: general, everyday, business, technology, academic, medical, health, travel, food, vegetables, animals, nature, art
> - JSON phải parse được: không có trailing comma, không có comment
> - "meaning_vi" nên ngắn gọn (3-8 từ), không 1 đoạn văn dài
"""


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["word", "pos", "pronunciation", "meaning_vi"])
    df["word"]         = df["word"].str.strip()
    df["pos"]          = df["pos"].fillna("").str.strip()
    df["pronunciation"]= df["pronunciation"].fillna("").str.strip()
    df["meaning_vi"]   = df["meaning_vi"].fillna("").str.strip()
    return df.dropna(subset=["word"])


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    current_pk = PK_GLOBAL_OFFSET
    total_prompts_created = 0

    for csv_file, cefr_level in CSV_FILES:
        if not os.path.exists(csv_file):
            print(f"⚠  Không tìm thấy {csv_file} — bỏ qua.")
            continue

        df = load_csv(csv_file)
        total_words   = len(df)
        total_batches = math.ceil(total_words / BATCH_SIZE)
        file_pk_start = current_pk

        print(f"\n📂 {csv_file} ({cefr_level}): {total_words} từ → {total_batches} batch "
              f"[pk {current_pk} – {current_pk + total_words - 1}]")

        for batch_idx in range(total_batches):
            start_i = batch_idx * BATCH_SIZE
            end_i   = min(start_i + BATCH_SIZE, total_words)
            batch_df = df.iloc[start_i:end_i]

            # Xây danh sách row dict với pk toàn cục
            batch_rows = []
            for _, row in batch_df.iterrows():
                batch_rows.append({
                    "pk":         current_pk,
                    "word":       row["word"],
                    "pos_mapped": map_pos(row["pos"]),
                    "ipa":        row["pronunciation"] or "",
                    "meaning_vi": row["meaning_vi"],
                })
                current_pk += 1

            prompt_text = generate_prompt(
                batch_rows, cefr_level,
                batch_num=batch_idx + 1,
                total_batches=total_batches,
                file_label=f"{csv_file}",
            )

            out_file = os.path.join(
                OUTPUT_DIR,
                f"Prompt_{cefr_level}_Batch_{batch_idx + 1:02d}"
                f"_pk{batch_rows[0]['pk']}-{batch_rows[-1]['pk']}.txt"
            )
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(prompt_text)

            total_prompts_created += 1
            print(f"  ✅ Batch {batch_idx + 1:2d}/{total_batches}: pk {batch_rows[0]['pk']}–{batch_rows[-1]['pk']} → {out_file}")

        print(f"   {csv_file}: pk {file_pk_start} – {current_pk - 1}")

    print(f"\n🎉 Hoàn thành! {total_prompts_created} file prompt trong thư mục '{OUTPUT_DIR}/'")
    print(f"   PK tiếp theo (để dùng cho lần sau): {current_pk}")
    print(f"\n📋 Workflow tiếp theo:")
    print(f"   1. Paste từng .txt vào ChatGPT/Claude → copy JSON output")
    print(f"   2. Lưu vào backend/apps/vocabulary/fixtures/<level>-batch-<N>.json")
    print(f"   3. cd backend && ../.venv/bin/python manage.py loaddata apps/vocabulary/fixtures/<file>.json")


if __name__ == "__main__":
    run()