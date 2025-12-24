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
import platform

# 운영체제별 한글 폰트 설정
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
        self.jobs_df = None

    # API 데이터 수집
    def fetch_data(self):
        print("\n>> 최신 채용 공고를 불러오는 중입니다...")
        try:
            # 5초 타임아웃 설정
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            jobs_list = data.get('jobs', [])
            
            if not jobs_list:
                print(">> 가져온 데이터가 없습니다.")
                return False

            # 데이터프레임 변환
            self.jobs_df = pd.DataFrame(jobs_list)
            
            # 분석에 필요한 컬럼만 추출
            columns = ['title', 'company_name', 'category', 'candidate_required_location', 'url', 'publication_date']
            existing_cols = [c for c in columns if c in self.jobs_df.columns]
            self.jobs_df = self.jobs_df[existing_cols]
            
            print(f">> 총 {len(self.jobs_df)}건의 데이터를 가져왔습니다.")
            return True

        except requests.exceptions.Timeout:
            print(">> 서버 응답이 지연되고 있습니다.")
        except requests.exceptions.ConnectionError:
            print(">> 인터넷 연결을 확인해주세요.")
        except Exception as e:
            print(f">> 데이터 통신 오류: {e}")
        return False

    # 키워드 검색
    def search_jobs(self):
        if self.jobs_df is None:
            if not self.fetch_data():
                return

        keyword = input("\n[검색] 찾고 싶은 키워드나 직군을 입력하세요 (예: Python): ").strip()
        
        # 대소문자 구분 없이 제목이나 카테고리에서 검색
        mask = (self.jobs_df['title'].str.contains(keyword, case=False, na=False)) | \
               (self.jobs_df['category'].str.contains(keyword, case=False, na=False))
        
        result_df = self.jobs_df[mask]

        if result_df.empty:
            print(">> 검색 결과가 없습니다.")
        else:
            print(f"\n>> '{keyword}' 관련 공고가 {len(result_df)}건 있습니다.")
            print("-" * 50)
            print(result_df[['title', 'company_name', 'category']].head().to_string(index=False))
            print("-" * 50)
            print("... (상위 5개만 표시)")
            
            # 기능 연결
            self.visualize_data(result_df, keyword)
            self.save_data(result_df)

    # 시각화 (그래프 출력)
    def visualize_data(self, df, title_keyword="전체"):
        print("\n>> 그래프를 생성하는 중입니다...")
        
        if 'category' not in df.columns:
            print(">> 카테고리 정보가 없어 그래프를 그릴 수 없습니다.")
            return

        # 상위 10개 직군 집계
        category_counts = df['category'].value_counts().head(10)

        plt.figure(figsize=(10, 6))
        plt.bar(category_counts.index, category_counts.values, color='skyblue')
        
        plt.title(f"Job Trend - {title_keyword}")
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # 그래프 이미지 저장 여부
        save_graph = input("현재 그래프를 이미지로 저장할까요? (Y/N): ").strip().upper()
        if save_graph == 'Y':
            filename = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename)
            print(f">> '{filename}' 저장 완료.")

        plt.show()

    # 파일 저장 (CSV)
    def save_data(self, df):
        choice = input("\n[저장] 검색 결과를 파일로 저장하시겠습니까? (Y/N): ").strip().upper()
        if choice == 'Y':
            try:
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"job_data_{timestamp}.csv"
                # 엑셀 호환을 위해 utf-8-sig 인코딩 사용
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f">> '{filename}' 파일로 저장되었습니다.")
            except Exception as e:
                print(f">> 파일 저장 실패: {e}")

    # 파일 불러오기
    def load_file(self):
        filename = input("\n[불러오기] 파일 이름을 입력하세요 (확장자 포함): ").strip()
        try:
            if not os.path.exists(filename):
                print(">> 파일이 존재하지 않습니다.")
                return

            if filename.endswith('.csv'):
                self.jobs_df = pd.read_csv(filename)
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                self.jobs_df = pd.read_excel(filename)
            else:
                print(">> 지원하지 않는 파일 형식입니다.")
                return

            print(f">> '{filename}'에서 {len(self.jobs_df)}건을 불러왔습니다.")
            
            viz_choice = input("불러온 데이터로 그래프를 그릴까요? (Y/N): ").strip().upper()
            if viz_choice == 'Y':
                self.visualize_data(self.jobs_df, "Loaded Data")

        except Exception as e:
            print(f">> 파일 로딩 오류: {e}")

    # 메인 메뉴
    def run(self):
        print("="*40)
        print("   Global IT Job Scout")
        print("="*40)

        while True:
            print("\n1. 실시간 데이터 수집 및 검색")
            print("2. 저장된 파일 불러오기")
            print("3. 종료")
            
            choice = input("메뉴 번호를 입력하세요: ").strip()

            if choice == '1':
                self.search_jobs()
            elif choice == '2':
                self.load_file()
            elif choice == '3':
                print("프로그램을 종료합니다.")
                sys.exit()
            else:
                print(">> 잘못된 입력입니다.")

if __name__ == "__main__":
    app = JobScout()
    app.run()
