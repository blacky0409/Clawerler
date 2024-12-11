import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
import joblib
import os

model_file = 'kmeans_model.pkl'
# CSV 파일에서 데이터 로드
df = pd.read_csv('../../result/second_result/recipes.csv')
# 필요한 열만 선택
df = df[["title", "step", "source", "category"]]  # 필요한 열만 남김
df = df.dropna()
# 재료와 카테고리를 문자열로 결합 (텍스트 데이터 생성)
df['텍스트'] = df['source'] + ' '+df['category'] +' '+df['step']
# CountVectorizer를 사용해 텍스트 데이터를 벡터화
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['텍스트'])

if os.path.exists(model_file):
    kmeans = joblib.load(model_file)
    print("모델을 로드했습니다.")
else:
	# KMeans 클러스터링
    num_clusters = 10  # 클러스터 수 설정
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    # 모델 저장
    joblib.dump(kmeans, model_file)
    print("새로운 모델을 학습하고 저장했습니다.")

# 클러스터 결과를 데이터프레임에 추가
df['클러스터'] = kmeans.labels_

def find_similar_recipe_by_name(recipe_name, df):
    # 입력된 요리 이름으로 재료와 카테고리 찾기
    recipe_data = df[df['title'] == recipe_name]
    
    if recipe_data.empty:
        return None,None,None;

    # 선택된 레시피의 재료와 카테고리 가져오기
    ingredients = recipe_data['source']
    category = recipe_data['category']
    step = recipe_data['step']
    
    # 입력 레시피의 텍스트 생성
    input_text = ingredients + ' ' + category +' '+ step

    # 입력 레시피를 벡터화
    input_vector = vectorizer.transform(input_text)

    # 입력 레시피의 클러스터 찾기
    cluster_label = kmeans.predict(input_vector)[0]
    cluster_recipes = df[df['클러스터'] == cluster_label]

    cluster_vector = vectorizer.transform(cluster_recipes['텍스트'])

    # NearestNeighbors를 사용하여 유사한 레시피 찾기
    nbrs = NearestNeighbors(n_neighbors=2, algorithm='auto').fit(cluster_vector)
    distances, indices = nbrs.kneighbors(input_vector)

	# 주재료 대체 로직
    original_main_ingredient = ingredients.apply(lambda x: x.split(',')[0]).iloc[0]

    for idx in indices[0][1:]:  # 가장 유사한 레시피를 제외하고 탐색
        similar_recipe = cluster_recipes.iloc[idx]
        similar_main_ingredient = similar_recipe['source'].split(',')[0]  # 유사 레시피의 주재료

        if original_main_ingredient != similar_main_ingredient:
            # 주재료가 다를 경우 대체
            similar_recipe_source = similar_recipe['source'].replace(similar_main_ingredient, original_main_ingredient, 1)
            return original_main_ingredient, similar_recipe['title'], similar_main_ingredient

    # 주재료가 같은 경우, 다른 레시피를 찾지 못한 경우
    return ingredients, None, None  # 대체 레시피가 없음을 나타냄i

# 사용 예시
input_recipe_name = "간식 - 블루베리딸기스무디"  # 검색할 요리 이름
original_ingredient, similar_name, similar_ingredients = find_similar_recipe_by_name(input_recipe_name, df)

if original_ingredient is None:
    print(f"{input_recipe_name}에 대한 레시피를 찾을 수 없습니다.")
elif similar_name is None:
    print(f"'{input_recipe_name}'의 주재료와 같은 레시피가 없습니다.")
else:
    print(f"'{input_recipe_name}'의 origin 재료 : {original_ingredient}")
    print(f"similar name: {similar_name} 재료: {similar_ingredients}")
