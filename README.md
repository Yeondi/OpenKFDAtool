# OpenKFDAtool  
🇰🇷 이 문서는 한국어와 영어로 작성되어 있습니다.  
🇺🇸 This document is written in both Korean and English.

---

## 🧾 소개 (Introduction)

**OpenKFDAtool**은 식품의약품안전처(식약처)의 공공 API를 이용해  
한국 식품 영양성분 데이터를 수집하고, Firebase에 업로드 및 매핑하는 Python 기반 툴입니다.

This tool fetches nutrition data from the Korean MFDS (Ministry of Food and Drug Safety) API,  
then uploads and manages it via Firebase with optional local JSON or CSV processing.

---

## 🔧 주요 기능 (Features)

- ✅ 식약처 영양정보 전체 페이지 수집 (`fetch_all_pages`)
- ✅ JSON 파일로 저장 (`save_json`)
- ✅ 음식 이름 ↔ 식품코드 매핑 JSON 생성 (`generate_food_name_map`)
- ✅ Firebase Firestore에 업로드 (`upload_to_firebase`)
- ✅ CSV/엑셀 파일을 Firebase에 업로드 (`upload_csv_to_firebase`)
- ✅ CLI(터미널 메뉴) 기반 인터페이스 제공

---

## 🚀 설치 및 실행 방법 (Setup & Usage)

### 🔹 1. 필수 라이브러리 설치 (Install dependencies)
```bash
pip install httpx firebase-admin pandas tqdm
```

### 🔹 2. 실행 (Run script)
```bash
python custom.py
```

### 🔹 3. 메뉴 예시 (Menu Example)
```
==== 메뉴 선택 ====
1. 식약처 전체 데이터 수집
2. 음식 이름 → 번호 매핑 JSON 생성
3. 데이터를 Firebase로 이관
4. CSV/Excel 파일 → Firebase 업로드
0. 종료
```

---

## 🔐 Firebase 설정 방법 (Firebase Setup)

- Firebase 콘솔에서 Firestore 프로젝트 생성
- 서비스 계정 키(JSON) 다운로드
- 실행 시 경로 입력 → 자동 초기화

---

## 📁 생성 파일 구조 (Generated Files)

| 파일명 | 설명 |
|--------|------|
| `food_data.json` | 수집된 전체 영양소 데이터 | 예시
| `food_name_to_num_map.json` | 음식명 ↔ 식품 코드 매핑 | 예시
| `remapped_food_database.json` | (옵션) 새로운 코드 기준으로 정제된 매핑 | 예시
| `nutritionData` (Firebase 컬렉션) | 영양정보 업로드 대상 |
| `nutritionCsvData` (Firebase 컬렉션) | CSV/엑셀 업로드 대상 |

---

## 📜 라이선스 (License)

이 프로젝트는 MIT 라이선스를 따릅니다.  
This project is licensed under the MIT License.

---

## 🙋‍♂️ 만든 사람 (Author)

개발자: 유재윤 (James Ryu / [Yeondi](https://github.com/Yeondi))  
GitHub: https://github.com/Yeondi/OpenKFDAtool  
문의: atlantis2568@gmail.com
