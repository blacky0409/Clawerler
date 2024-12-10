import pandas as pd
from datasketch import MinHash, MinHashLSH
import re

# CSV 파일에서 레시피 데이터 읽기
recipes_df = pd.read_csv("recipes.csv")

# NaN 값을 빈 문자열로 대체
recipes_df['source'] = recipes_df['source'].fillna('')

# MinHash LSH 초기화
lsh = MinHashLSH(threshold=0.1, num_perm=64)  # num_perm 값을 줄임

# 정규 표현식을 사용하여 재료만 추출하는 함수
def extract_ingredients(ingredient_str):
    if isinstance(ingredient_str, str):  # 문자열인지 확인
        ingredients = re.findall(r'([^,]+)(?=,|$)', ingredient_str)
        return [ingredient.strip() for ingredient in ingredients]  # 공백 제거
    return []  # 문자열이 아닐 경우 빈 리스트 반환

# 레시피에 대한 MinHash 계산 및 저장
def calculate_minhash(row):
    ingredients = extract_ingredients(row['source'])
    if ingredients:  # 재료가 있을 경우에만 처리
        m = MinHash(num_perm=64)
        for ingredient in ingredients:
            m.update(ingredient.strip().encode('utf-8'))
        return m
    return None

# MinHash 계산
recipes_df['minhash'] = recipes_df.apply(calculate_minhash, axis=1)

# MinHash를 LSH에 삽입
for index, row in recipes_df.iterrows():
    if row['minhash'] is not None:
        lsh.insert(f"recipe_{index}", row['minhash'])

# 사용자로부터 재료 입력 받기
user_input = input("요리 재료를 입력하세요: ")
user_ingredients = user_input.split(", ")

# 사용자 입력에 대한 MinHash 계산
user_minhash = MinHash(num_perm=64)
for ingredient in user_ingredients:
    user_minhash.update(ingredient.strip().encode('utf-8'))

# LSH를 통해 유사한 레시피 검색
result = lsh.query(user_minhash)

# 추천 결과 출력
if result:
    print("\n추천 레시피:")
    for recipe_id in result:
        index = int(recipe_id.split("_")[1])  # recipe_0 형식에서 인덱스 추출
        recipe_title = recipes_df.iloc[index]['title']  # 'title' 열에서 제목 추출
        total_time = recipes_df.iloc[index]['time']  # 'time' 열에서 조리 시간 추출
        servings = recipes_df.iloc[index]['num']  # 'num' 열에서 인분 수 추출
        steps = recipes_df.iloc[index]['step']  # 'step' 열에서 조리 방법 추출

        # 결과 출력
        print(f"\n제목: {recipe_title}")
        print(f"총 시간: {total_time}")
        print(f"인분 수: {servings}")
        print(f"조리 방법: {steps}")
else:
    print("\n추천할 레시피가 없습니다. 다른 재료를 입력해 보세요.")
