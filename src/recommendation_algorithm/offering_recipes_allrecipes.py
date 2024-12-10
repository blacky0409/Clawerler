import pandas as pd
from datasketch import MinHash, MinHashLSH
import re

# CSV 파일에서 레시피 데이터 읽기
recipes_df = pd.read_csv("allrecipes_data.csv")

# MinHash LSH 초기화
lsh = MinHashLSH(threshold=0.1, num_perm=128)  # Threshold 값을 낮춤

# 정규 표현식을 사용하여 재료만 추출하는 함수
def extract_ingredients(ingredient_str):
    # 정규 표현식을 사용하여 재료만 추출
    ingredients = re.findall(r'([^,]+)(?=,|$)', ingredient_str)
    return [ingredient.split(' ')[-1] for ingredient in ingredients]  # 마지막 단어를 재료로 간주

# 레시피에 대한 MinHash 계산 및 저장
minhashes = {}
for index, row in recipes_df.iterrows():
    ingredients = extract_ingredients(row['Ingredients (Korean)'])
    m = MinHash(num_perm=128)
    for ingredient in ingredients:
        m.update(ingredient.strip().encode('utf-8'))
    lsh.insert(f"recipe_{index}", m)
    minhashes[f"recipe_{index}"] = m

# 사용자로부터 재료 입력 받기
user_input = input("요리 재료를 입력하세요: ")
user_ingredients = user_input.split(", ")

# 사용자 입력에 대한 MinHash 계산
user_minhash = MinHash(num_perm=128)
for ingredient in user_ingredients:
    user_minhash.update(ingredient.strip().encode('utf-8'))

# LSH를 통해 유사한 레시피 검색
result = lsh.query(user_minhash)

# 추천 결과 출력
if result:
    print("\n추천 레시피:")
    for recipe_id in result:
        index = int(recipe_id.split("_")[1])  # recipe_0 형식에서 인덱스 추출
        recipe_title = recipes_df.iloc[index]['Title (Korean)']  # 제목
        total_time = recipes_df.iloc[index]['Total Time']  # 총 시간
        servings = recipes_df.iloc[index]['Servings (Korean)']  # 인분 수
        steps = recipes_df.iloc[index]['Directions (Korean)']  # 조리 방법
        
        print(f"\n제목: {recipe_title}")
        print(f"총 시간: {total_time}")
        print(f"인분 수: {servings}")
        print(f"조리 방법: {steps}")  # 수정된 부분
else:
    print("\n추천할 레시피가 없습니다. 다른 재료를 입력해 보세요.")
