import pytz
import matplotlib
matplotlib.use('Agg')  # Agg 백엔드 사용 (GUI 없이 이미지 파일로만 저장)
import matplotlib.pyplot as plt
from datetime import datetime

class MyGraphMaker:   
    # 초기화 메서드 (__init__) - 객체가 생성될 때 자동으로 호출
    def __init__(self):
        # 한글 폰트 설정
        matplotlib.rcParams['font.family'] = 'NanumGothic'  # 또는 시스템에 맞는 다른 한글 글꼴 사용
    
    # 클래스 메서드 (메서드는 객체의 동작을 정의)
    def format_large_number(self, value):
        """거래량을 K, M, B 등의 단위로 포맷하는 함수"""
        if value >= 1_000_000_000:  # 10억 이상
            return f'{value / 1_000_000_000:.1f}B'
        elif value >= 1_000_000:  # 백만 이상
            return f'{value / 1_000_000:.1f}M'
        elif value >= 1_000:  # 천 이상
            return f'{value / 1_000:.1f}K'
        elif value < 1000 and value != int(value):  # 1000 미만의 소수점 값만 표시
            return f'{value:.1f}'
        else:
            return str(int(value))  # 그 외는 정수로 표시

    def create_n_save_graph(self, trade_records, export_filename, item_name):
        # 레코드 비어있으면 패스
        if len(trade_records) < 2:
            return False

        try:
            # 날짜를 기준으로 정렬 (딕셔너리의 'Date' 키를 기준으로 정렬)
            trade_records.sort(key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))

            # 결과 데이터를 Date, AvgPrice, TradeCount로 나누기
            dates = [row['Date'] for row in trade_records]  # 'Date' 키로 접근
            avgprices = [float(row['AvgPrice']) for row in trade_records]  # 'AvgPrice' 키로 접근
            tradecounts = [row['TradeCount'] for row in trade_records]  # 'TradeCount' 키로 접근

            # 그래프 생성
            fig, ax1 = plt.subplots(figsize=(10, 6))

            # 첫 번째 y축: avgprice 그리기
            ax1.plot(dates, avgprices, color='tab:blue', label='평균 가격', marker='o', zorder=2)
            ax1.set_xlabel(item_name)    
            ax1.set_ylabel('평균 가격', color='tab:blue')
            ax1.tick_params(axis='y', labelcolor='tab:blue')

            # 두 번째 y축: tradecount 막대그래프 그리기
            ax2 = ax1.twinx()  # 동일한 x축을 사용하여 y축을 추가로 생성
            ax2.bar(dates, tradecounts, color='tab:green', label='거래량', alpha=0.6, zorder=1)
            ax2.set_ylabel('거래량', color='tab:green')
            ax2.tick_params(axis='y', labelcolor='tab:green')

            # 거래량 y축에 K, M, B 단위 적용
            max_trade_count = max(tradecounts)  # 최대 거래량
            ax2.set_yticklabels([self.format_large_number(i) for i in ax2.get_yticks()])

            y1_min, y1_max = ax1.get_ylim()
            y_height = y1_max - y1_min
            print(f"높이: {y_height}")

            # 평균가격 점 위에 텍스트 추가 (평균가격 텍스트는 그대로 표시)
            for i, avg_price in enumerate(avgprices):          
                #ax1.text(dates[i], avg_price, f'{avg_price:.1f}', ha='center', color='tab:gray', fontsize=10)   
                if avg_price < 1000:         
                    ax1.text(dates[i], avg_price + (y_height * 0.01), f'{avg_price:.1f}', ha='center', color='tab:gray', fontsize=10)            
                else:
                    ax1.text(dates[i], avg_price + (y_height * 0.02), str(int(avg_price)), ha='center', color='tab:gray', fontsize=10)            

            # x축 레이블을 설정
            ax1.set_xticks(range(len(dates)))  # x축의 위치를 설정
            ax1.set_xticklabels(dates, rotation=45)  # x축의 레이블을 설정

            kst = pytz.timezone('Asia/Seoul')
            current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
            plt.figtext(0.02, 0.02, f'생성 일자 : {current_time}', horizontalalignment='left', fontsize=10, color='gray')

            # 그래프 레이아웃 조정
            plt.tight_layout()

            # 그래프를 이미지 파일로 저장
            plt.savefig(export_filename + '.png', format='png')  
            plt.close()

            return True           
        except Exception as e:
            print(f"Error: {e}")
            return False
