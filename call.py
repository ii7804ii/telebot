import requests
import telegram
from datetime import datetime
import time
import schedule
import xml.etree.ElementTree as ET

# 텔레그램 봇 토큰과 채팅 ID (본인 정보로 변경)
TOKEN = '8291253249:AAGTxG5qi1rA01e6GzHx1g7jxMYzjU1jNNQ'
CHAT_ID = '-1002804190562'

bot = telegram.Bot(token=TOKEN)

SEOUL_DISTRICTS = [
    '종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '중랑구', '성북구', '강북구',
    '도봉구', '노원구', '은평구', '서대문구', '마포구', '양천구', '강서구', '구로구', '금천구',
    '영등포구', '동작구', '관악구', '서초구', '강남구', '송파구', '강동구'
]

GU_CODE = {
    '종로구': '11110', '중구': '11140', '용산구': '11170', '성동구': '11200', '광진구': '11215',
    '동대문구': '11230', '중랑구': '11260', '성북구': '11290', '강북구': '11305', '도봉구': '11320',
    '노원구': '11350', '은평구': '11380', '서대문구': '11410', '마포구': '11440', '양천구': '11470',
    '강서구': '11500', '구로구': '11530', '금천구': '11545', '영등포구': '11560', '동작구': '11590',
    '관악구': '11620', '서초구': '11650', '강남구': '11680', '송파구': '11710', '강동구': '11740'
}

# 아파트 실거래가 API (공공데이터포털)
BASE_URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
SERVICE_KEY = '8gOjRZeGbJbMYAoUhN+0ScO2USzZ/lDps0lwEkm8xOCqNYcYIb3SSwM5VMCQDDZlUPQgrNCGsP3dqrgTrFxUCg=='

# 금액 변환 함수
def convert_to_억(amt_str):
    try:
        amt_num = int(amt_str.replace(',', ''))
        억 = amt_num / 10000
        return f"{억:.2f}억"
    except:
        return amt_str

# API 데이터 요청
def get_apt_data(lawd_cd, deal_ymd):
    params = {
        'serviceKey': SERVICE_KEY,
        'LAWD_CD': lawd_cd,
        'DEAL_YMD': deal_ymd,
        'pageNo': 1,
        'numOfRows': 10
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"{lawd_cd} 구 요청 실패:", e)
        return None

# XML 파싱 및 메시지 포맷
def parse_xml_and_format(xml_text, gu_name):
    root = ET.fromstring(xml_text)
    items = root.find('.//items')
    if items is None:
        return f"{gu_name} 데이터가 없습니다.\n"

    message = f"🏠 *{gu_name} 실거래가 (최근 5건)*\n\n"
    count = 0

    for item in items.findall('item'):
        if count >= 5:
            break
        aptNm = item.findtext('aptNm', default='정보없음')
        dealAmount = item.findtext('dealAmount', default='0')
        buildYear = item.findtext('buildYear', default='정보없음')
        floor = item.findtext('floor', default='정보없음')
        dealDay = item.findtext('dealDay', default='정보없음')

        # 전용면적(m²) → 평 변환
        exclusiveArea_m2 = item.findtext('exclusiveArea', default='0')
        try:
            exclusiveArea_m2 = float(exclusiveArea_m2)
            exclusiveArea_py = round(exclusiveArea_m2 / 3.3058, 1)
            area_str = f"{exclusiveArea_m2:.1f}㎡ ({exclusiveArea_py}평)"
        except:
            area_str = "정보없음"

        dealAmount_억 = convert_to_억(dealAmount)

        message += (
            f"🏢 아파트: {aptNm}\n"
            f"💰 거래금액: {dealAmount_억}\n"
            f"📐 전용면적: {area_str}\n"
            f"🏗️ 준공년도: {buildYear}\n"
            f"⬆️ 층수: {floor}층\n"
            f"📅 거래일: {dealDay}일\n"
            "---------------------\n"
        )
        count += 1

    message += f"\n📅 기준일: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    return message

# 전체 구 데이터 전송
def send_seoul_trade_report():
    print("실거래가 알림 전송 시작...")
    deal_ymd = datetime.now().strftime('%Y%m')

    for gu in SEOUL_DISTRICTS:
        lawd_cd = GU_CODE.get(gu)
        if not lawd_cd:
            print(f"{gu} 코드가 없습니다.")
            continue

        xml_data = get_apt_data(lawd_cd, deal_ymd)
        if xml_data is None:
            continue

        msg = parse_xml_and_format(xml_data, gu)
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

        print(f"{gu} 실거래가 메시지 전송 완료.")
        time.sleep(1)  # API 과부하 방지

if __name__ == "__main__":
    # 매일 오전 10시에 실행 예약
    schedule.every().day.at("10:00").do(send_seoul_trade_report)
    print("봇이 실행 중입니다. 매일 10시에 자동으로 실거래가를 보냅니다.")

    # 프로그램 계속 실행
    while True:
        schedule.run_pending()
        time.sleep(1)
