import pandas as pd
import json

def create_food_name_to_code_map(excel_paths, output_json_path):
    food_code_map = {}

    for path in excel_paths:
        print(f"📄 엑셀 파일 읽는 중: {path}")
        try:
            df = pd.read_excel(path)
        except Exception as e:
            print(f"❌ 파일 열기 실패: {path}\n   에러: {e}")
            continue

        for _, row in df.iterrows():
            name = str(row.get('식품명', '')).strip()
            code = str(row.get('식품코드', '')).strip()
            if name and code:
                food_code_map[name] = code

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(food_code_map, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 총 {len(food_code_map)}개의 항목 저장 완료 → {output_json_path}")

# ========================
# 사용 예시
# ========================
if __name__ == "__main__":
    excel_files = [
        "C:/Users/atlan/Documents/py/SortFields/20250327_instantDB_147999.xlsx",
        "C:/Users/atlan/Documents/py/SortFields/20250408_FoodDB.xlsx"
    ]

    create_food_name_to_code_map(
        excel_paths=excel_files,
        output_json_path="C:/Users/atlan/Documents/py/SortFields/food_name_to_foodcd_map.json"
    )
