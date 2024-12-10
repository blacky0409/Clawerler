import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# CSV 파일에서 데이터 로드
df = pd.read_csv('../result/second_result/recipes.csv')

# 필요한 열만 선택
df = df[["title", "source", "category"]]
df = df.dropna()

# 재료와 카테고리를 문자열로 결합 (텍스트 데이터 생성)
df['텍스트'] = df['source'] + ' ' + df['category']

# CountVectorizer를 사용해 텍스트 데이터를 벡터화
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['텍스트'])

# 클러스터 수에 따른 평균 거리와 실루엣 점수 저장
inertia = []
silhouette_avg = []

# 클러스터 수를 2부터 50까지 변경
for num_clusters in range(40, 200 , 10):
    print(num_clusters)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    
    # 평균 거리 (inertia) 저장
    print(kmeans.inertia_)
    inertia.append(kmeans.inertia_)
