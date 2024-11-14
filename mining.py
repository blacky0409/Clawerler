#요리 이름, 재료, 레시피, 인분, 조리시간
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import csv
import pandas as pd

baseUrl = 'https://www.10000recipe.com'

def PageCrawler(Url):
	url = baseUrl + Url

	session = requests.Session()
	retry = Retry(total=5,  # 최대 재시도 횟수
		backoff_factor=1,  # 재시도 간 대기 시간 증가
		status_forcelist=[500, 502, 503, 504])  # 재시도할 상태 코드
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)

	page = requests.get(url)
	recipe_source = [] #재료
	recipe_step = [] #레시피 순서
	recipe_title = ""
	recipe_num = ""
	recipe_time = ""
	try:
		if page.status_code == 200:
			soup= BeautifulSoup(page.content, 'html.parser')
	
			#이름 recipe_title
			#인분 recipe_num
			#조리시간 recipe_time

			try:
				title = soup.select_one('#contents_area_full > div.view2_summary.st3 > h3')
				recipe_title = title.get_text()
			except(AttributeError):
				return
	
			try:
				num = soup.select_one('#contents_area_full > div.view2_summary.st3 > div.view2_summary_info > span.view2_summary_info1')
				recipe_num = num.get_text()
			except(AttributeError):
				print("num")

			try:
				time = soup.select_one('#contents_area_full > div.view2_summary.st3 > div.view2_summary_info > span.view2_summary_info2')
				recipe_time = time.get_text()

			except(AttributeError):
				print("time")
		#재료
			try:
				ingredient_tags = soup.select('#divConfirmedMaterialArea > ul > li')  # 재료 목록 선택

				for ingredient in ingredient_tags:
					name_tag = ingredient.find('a')  # <a> 태그에서 재료 이름 추출
					if name_tag:
						recipe_source.append(name_tag.get_text().replace('\n','').replace(' ',''))
			
		
			except(AttributeError):
				return	
		
			# 조리 순서
			try:
				step_divs = soup.select('#obx_recipe_step_start > div[id^="stepDiv"]')  # 조리 단계 선택

				for step in step_divs:
					for p in step.find_all('p'):
						p.extract()

					recipe_step.append(step.get_text(strip=True))
	

			except(AttributeError):
				return
		
		else:
			print(page.status_code)

	except requests.exceptions.RequestException as e:
		print(f"Error: {e}")
	
	
	recipe_all = [recipe_title, recipe_source, recipe_step, recipe_num, recipe_time]
	return (recipe_all)

def SaveData(rlist):
	data = {
		'title': [],
		'source': [],
		'step': [],
		'num': [],
		'time': []
	}

	for recipe in rlist:
		title, source, step, num, time = recipe
		data['title'].append(title if title is not None else '')
		data['source'].append(', '.join(source) if source is not None else '')  # 리스트를 문자열로 변환
		data['step'].append('; '.join(step) if step is not None else '')  # 리스트를 문자열로 변환
		data['num'].append(num if num is not None else 0)  # 기본값 0
		data['time'].append(time if time is not None else '')  # 빈 문자열

	df = pd.DataFrame(data)

	df.to_csv('recipes.csv', index=False, encoding='utf-8-sig')

def GetData(size):
	recipes = []

	for i in range(1,size+1):

		if i % 100 == 0:
			print(f'current page is {i}')

		url = f'https://www.10000recipe.com/recipe/list.html?order=reco&page={i}'  


		session = requests.Session()
		retry = Retry(total=5,  # 최대 재시도 횟수
					backoff_factor=1,  # 재시도 간 대기 시간 증가
					status_forcelist=[500, 502, 503, 504])  # 재시도할 상태 코드
		adapter = HTTPAdapter(max_retries=retry)
		session.mount('http://', adapter)
		session.mount('https://', adapter)

		try:

			page = requests.get(url) 
		
			if page.status_code == 200:
				soup = BeautifulSoup(page.content, 'html.parser')

				try:
					step_divs = soup.select('#contents_area_full > ul > ul > li')
				
					for step in step_divs:
						link = step.find('div',{'class':'common_sp_thumb'}).find('a')['href']
						re = PageCrawler(link)
					
						if re is not None:
							recipes.append(re)


				except(AttributeError):
					print("error")

			else:
				break
		
		except requests.exceptions.RequestException as e:
			print(f"Error: {e}")
	

	SaveData(recipes)


page = 100000

GetData(page)




