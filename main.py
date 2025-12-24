"""
[2025-2학기 파이썬 프로그래밍 최종 프로젝트]
- 프로젝트명: Global IT Job Scout
- 학번: 2025006260
- 이름: 박소영
- 제출일: 2025년 12월 24일
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import sys

# 한글 폰트 설정 (Windows: Malgun Gothic, Mac: AppleGothic)
# 그래프에서 한글이 깨지는 것을 방지하기 위함
import platform
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='sans-serif')
plt.rcParams['axes.unicode_minus'] = False

class JobScout:
    def __init__(self):
        self.api_url = "https://remotive.com/api/remote-jobs"
        self.jobs_df = None # 데이터를 저장할 DataFrame

    # [REQ-1, REQ-NF-2] 실시간 데이터 수집 및 에러 처리
    def fetch_data(self):
        print("\n[시스템] 최신 채용 공고 데이터를 수집 중입니다...")
        try:
            # [REQ-NF-2] 5초 타임아웃 설정
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            jobs_list = data.get('jobs', [])
            
            if not jobs_list:
                print("[알림] 가져온 데이터가 없습니다.")
                return False

            # 데이터프레임으로 변환 및 필요한 컬럼만 추출
            self.jobs_df = pd.DataFrame(jobs_list)
            # 분석에 필요한 주요 컬럼만 선택 (제목, 회사, 카테고리, 지역, URL, 게시일)
            columns = ['title', 'company_name', 'category', 'candidate_required_location', 'url', 'publication_date']
            # 존재하는 컬럼만 선택하여 에러 방지
            existing_cols = [c for c in columns if c in self.jobs_df.columns]
            self.jobs_df = self.jobs_df[existing_cols]
            
            print(f"[성공] 총 {len(self.jobs_df)}건의 데이터를 성공적으로 불러왔습니다.")
            return True

        except requests.exceptions.Timeout:
            print("[에러] 서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요.") # [REQ-NF-2]
        except requests.exceptions.ConnectionError:
            print("[에러] 인터넷 연결을 확인해주세요.") # [REQ-1]
        except Exception as e:
            print(f"[에러] 데이터를 가져오는 중 문제가 발생했습니다: {e}")
        return False

    # [REQ-2] 사용자 맞춤 검색 및 필터링
    def search_jobs(self):
        if self.jobs_df is None:
            if not self.fetch_data():
                return

        keyword = input("\n[검색] 검색할 키워드 또는 직군을 입력하세요 (예: Python, Data): ").strip()
        
        # 대소문자 구분 없이 검색 (제목 또는 카테고리에 키워드가 포함된 경우)
        mask = (self.jobs_df['title'].str.contains(keyword, case=False, na=False)) | \
               (self.jobs_df['category'].str.contains(keyword, case=False, na=False))
        
        result_df = self.jobs_df[mask]

        if result_df.empty:
            print("[결과] 해당 조건의 채용 공고가 없습니다.") # [REQ-2]
        else:
            print(f"\n[결과] '{keyword}' 키워드로 총 {len(result_df)}건이 검색되었습니다.")
            print(result_df[['title', 'company_name', 'category']].head().to_string(index=False))
            print("... (상위 5건만 표시됨)")
            
            # 검색 후 바로 시각화 또는 저장으로 이어질 수 있도록 기능 연결
            self.visualize_data(result_df, keyword)
            self.save_data(result_df)

    # [REQ-3] 데이터 시각화
    def visualize_data(self, df, title_keyword="전체"):
        print("\n[시스템] 데이터 시각화를 준비 중입니다...")
        
        # 직군(Category)별 공고 수 집계
        if 'category' not in df.columns:
            print("[에러] 시각화할 카테고리 정보가 부족합니다.")
            return

        category_counts = df['category'].value_counts().head(10) # 상위 10개만

        plt.figure(figsize=(10, 6))
        # 막대 그래프 그리기
        bars = plt.bar(category_counts.index, category_counts.values, color='skyblue')
        
        plt.title(f"Job Distribution - {title_keyword}")
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # 그래프 저장 옵션 [REQ-3]
        save_graph = input("그래프를 이미지 파일로 저장하시겠습니까? (Y/N): ").strip().upper()
        if save_graph == 'Y':
            filename = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename)
            print(f"[저장] 그래프가 '{filename}'으로 저장되었습니다.")

        plt.show() # 팝업 출력

    # [REQ-4] 파일 저장
    def save_data(self, df):
        choice = input("\n[저장] 검색 결과를 파일로 저장하시겠습니까? (Y/N): ").strip().upper()
        if choice == 'Y':
            try:
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"job_data_{timestamp}.csv" # [REQ-4] CSV 저장
                df.to_csv(filename, index=False, encoding='utf-8-sig') # 엑셀 호환을 위해 utf-8-sig 사용
                print(f"[성공] 파일이 '{filename}' 이름으로 저장되었습니다.")
            except Exception as e:
                print(f"[에러] 파일 저장 실패: {e}")

    # [REQ-4] 파일 불러오기
    def load_file(self):
        filename = input("\n[불러오기] 불러올 파일명(확장자 포함)을 입력하세요: ").strip()
        try:
            if not os.path.exists(filename):
                print("[에러] 해당 파일이 존재하지 않습니다.")
                return

            if filename.endswith('.csv'):
                self.jobs_df = pd.read_csv(filename)
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                self.jobs_df = pd.read_excel(filename)
            else:
                print("[에러] 지원하지 않는 파일 형식입니다. (CSV, Excel만 가능)")
                return

            print(f"[성공] '{filename}'에서 {len(self.jobs_df)}건의 데이터를 불러왔습니다.")
            
            # 불러온 데이터로 바로 시각화 가능하도록 유도
            viz_choice = input("불러온 데이터로 그래프를 그리시겠습니까? (Y/N): ").strip().upper()
            if viz_choice == 'Y':
                self.visualize_data(self.jobs_df, "Loaded Data")

        except Exception as e:
            print(f"[에러] 파일 로딩 중 문제가 발생했습니다: {e}")

    # [REQ-5] 메인 메뉴 UI
    def run(self):
        print("="*40)
        print("   Global IT Job Scout (v1.0)") # 
        print("="*40)

        while True:
            print("\n[메인 메뉴]")
            print("1. 실시간 데이터 수집 및 검색")
            print("2. 저장된 파일 불러오기")
            print("3. 종료")
            
            choice = input("메뉴를 선택하세요 (번호 입력): ").strip()

            if choice == '1':
                self.search_jobs()
            elif choice == '2':
                self.load_file()
            elif choice == '3':
                print("프로그램을 종료합니다. 이용해 주셔서 감사합니다.")
                sys.exit()
            else:
                # [REQ-5] 잘못된 입력 처리
                print("[경고] 잘못된 입력입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    app = JobScout()
    app.run()
