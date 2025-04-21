import httpx
import json
import time
import os
import random
import firebase_admin
from firebase_admin import credentials, firestore
from urllib.parse import quote
from tqdm import tqdm
import pandas as pd

API_KEY = "+s0NUb2AGeNvZeAYnnG8bAaG/yGAfLzGIwREsVfm7vUrwCX2vbI2CCkv0Z9rV/4Wy9iK5VpIIiWLrxblEatGoA=="
BASE_URL = "https://apis.data.go.kr/1471000/FoodNtrCpntDbInfo02/getFoodNtrCpntDbInq02"
encoded_key = quote(API_KEY, safe='')

def get_total_pages():
    url = f"{BASE_URL}?serviceKey={encoded_key}&type=json&pageNo=1&numOfRows=100"
    with httpx.Client(http2=True, timeout=10.0) as client:
        r = client.get(url)
        r.raise_for_status()
        body = r.json().get("body", {})
        total = int(body.get("totalCount", 0))
        return (total // 100) + 1

def fetch_all_pages():
    all_items = []
    total_pages = get_total_pages()
    print(f"총 {total_pages} 페이지 수집 시작")

    with httpx.Client(http2=True, timeout=10.0) as client:
        for page in range(1, total_pages + 1):
            url = f"{BASE_URL}?serviceKey={encoded_key}&type=json&pageNo={page}&numOfRows=100"
            try:
                r = client.get(url)
                r.raise_for_status()
                body = r.json().get("body", {})
                items = body.get("items", [])
                all_items.extend(items)
                print(f"✅ {page}페이지 완료 ({len(items)}건)")
            except Exception as e:
                print(f"❌ {page}페이지 에러: {e}")
            time.sleep(0.2)
    return all_items

def save_json(data, filename="food_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"📁 저장 완료: {filename}")

def generate_food_name_map(data, output_file="food_name_to_num_map.json"):
    mapping = {
        item.get("FOOD_NM_KR", ""): item.get("NUM", "")
        for item in data if item.get("FOOD_NM_KR") and item.get("NUM")
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"📁 음식이름:번호 매핑 저장 완료: {output_file}")

def initialize_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred_path = input("Firebase 서비스 계정 키 파일 경로를 입력하세요: ")
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase 초기화 완료")
        except Exception as e:
            print(f"❌ Firebase 초기화 실패: {e}")
            return False
    return True

def upload_to_firebase(data, collection_name="nutritionData"):
    if not initialize_firebase():
        return False

    db = firestore.client()
    batch_size = 250
    current_time = firestore.SERVER_TIMESTAMP

    success_count = 0
    error_count = 0

    for i in tqdm(range(0, len(data), batch_size)):
        batch = db.batch()
        batch_data = data[i:i + batch_size]

        for item in batch_data:
            if "NUM" not in item:
                error_count += 1
                continue

            doc_ref = db.collection(collection_name).document(str(item["NUM"]))
            item_with_timestamp = item.copy()
            item_with_timestamp["lastUpdated"] = current_time
            batch.set(doc_ref, item_with_timestamp)

        for retry in range(5):
            try:
                batch.commit()
                success_count += len(batch_data)
                break
            except Exception as e:
                print(f"❌ [배치 {i // batch_size + 1}] 커밋 실패 (시도 {retry + 1}): {e}")
                wait_time = 2 + retry + random.uniform(0.2, 0.8)
                print(f"⏳ {wait_time:.1f}초 후 재시도 중...")
                time.sleep(wait_time)
                if retry == 4:
                    error_count += len(batch_data)

        time.sleep(1.5)

    print(f"✅ Firebase 업로드 완료: 성공 {success_count}건, 실패 {error_count}건")

    try:
        meta_ref = db.collection("metadata").document("nutritionDataInfo")
        meta_ref.set({
            "lastFullUpdate": current_time,
            "totalItems": success_count,
            "updateMethod": "bulk_upload_safe_retry"
        })
        print("✅ 메타데이터 업데이트 완료")
    except Exception as e:
        print(f"❌ 메타데이터 업데이트 오류: {e}")

    return success_count > 0

def upload_csv_to_firebase(file_path, collection_name="nutritionCsvData"):
    if not initialize_firebase():
        return False

    df = pd.read_csv(file_path) if file_path.endswith(".csv") else pd.read_excel(file_path)
    df = df.fillna("")

    # 컬럼 매핑
    column_mapping = {
        "식품코드": "NUM",
        "식품명": "FOOD_NM_KR"
    }
    df.rename(columns=column_mapping, inplace=True)

    data = df.to_dict(orient="records")
    upload_to_firebase(data, collection_name)

def run_cli():
    while True:
        print("\n==== 메뉴 선택 ====")
        print("1. 식약처 전체 데이터 수집")
        print("2. 음식 이름 → 번호 매핑 JSON 생성")
        print("3. 데이터를 Firebase로 이관")
        print("4. CSV/Excel 파일 → Firebase 업로드")
        print("0. 종료")

        choice = input("번호를 입력하세요: ")

        if choice == "1":
            data = fetch_all_pages()
            save_json(data)
        elif choice == "2":
            if not os.path.exists("food_data.json"):
                print("❗ food_data.json이 없습니다. 먼저 1번으로 데이터를 수집해주세요.")
                continue
            with open("food_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            generate_food_name_map(data)
        elif choice == "3":
            if not os.path.exists("food_data.json"):
                print("❗ food_data.json이 없습니다. 먼저 1번으로 데이터를 수집해주세요.")
                continue
            with open("food_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            collection_name = input("Firebase 컬렉션 이름을 입력하세요 (기본: nutritionData): ") or "nutritionData"
            upload_to_firebase(data, collection_name)
            if input("음식 이름-코드 매핑 JSON도 업데이트할까요? (y/n): ").lower() == 'y':
                generate_food_name_map(data)
        elif choice == "4":
            file_path = input("CSV 또는 Excel 파일 경로를 입력하세요: ")
            collection_name = input("Firebase 컬렉션 이름을 입력하세요 (기본: nutritionCsvData): ") or "nutritionCsvData"
            upload_csv_to_firebase(file_path, collection_name)
        elif choice == "0":
            print("👋 종료합니다!")
            break
        else:
            print("⚠️ 잘못된 입력입니다.")

if __name__ == "__main__":
    run_cli()
