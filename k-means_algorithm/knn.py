import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans

# CSV 파일에서 데이터 로드
df = pd.read_csv('recipes.csv')

# 필요한 열만 선택
df = df[["title", "step", "source", "category"]]  # 필요한 열만 남김

df = df.dropna()

# 재료와 카테고리를 문자열로 결합 (텍스트 데이터 생성)
df['텍스트'] = df['source'] + ' '+df['category'] +' '+df['step']

# CountVectorizer를 사용해 텍스트 데이터를 벡터화
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['텍스트'])

# KMeans 클러스터링
num_clusters = 16  # 클러스터 수 설정
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(X)

# 클러스터 결과를 데이터프레임에 추가
df['클러스터'] = kmeans.labels_

def find_similar_recipe_by_name(recipe_name, df):
    # 입력된 요리 이름으로 재료와 카테고리 찾기
    recipe_data = df[df['title'] == recipe_name]
    
    if recipe_data.empty:
        return f"{recipe_name}에 대한 레시피를 찾을 수 없습니다."

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

    # 가장 유사한 레시피의 인덱스 찾기
    similar_recipe_index = indices[0][1]
    similar_recipe = cluster_recipes.iloc[similar_recipe_index]

    return ingredients, similar_recipe['title'], similar_recipe['source']

# 사용 예시
input_recipe_name = "소고기 대파 볶음"  # 검색할 요리 이름
original_ingredient, similar_name, similar_ingredients = find_similar_recipe_by_name(input_recipe_name, df)

print(f"'{input_recipe_name}'의  origin 재료 :  {original_ingredient}")
print(f"similar name: {similar_name} 재료: {similar_ingredients}")
