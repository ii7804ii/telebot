import requests
import telegram
import os
from datetime import datetime
import time 
import xml.etree.ElementTree as ET

# 서비스 키와 텔레그램 토큰/챗ID는 Secrets에서 불러오기
SERVICE_KEY = os.environ["SERVICE_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = telegram.Bot(token=TELEGRAM_TOKEN)

# 구 리스트
GUS = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구",
    "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구",
    "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구",
    "은평구", "종로구", "중구", "중랑구"
]

# 아파트 매매 실거래가 조회 API 호출
def get_apt_data(gu):
    url = f"http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
    params = {
        "serviceKey": SERVICE_KEY,
        "LAWD_CD": get_lawd_cd(gu),
        "DEAL_YMD": get_current_ym()
    }
    r = requests.get(url, params=params)
    xml_data = r.text

    # ✅ 응답 원문 앞부분 찍기 (디버깅용)
    print(f"[{gu}] 응답 원문: {xml_data[:500]}")

    return xml_data

# 구 이름을 코드로 변환
def get_lawd_cd(gu):
    gu_cd_map = {
        "강남구": "11680", "강동구": "11740", "강북구": "11305", "강서구": "11500",
        "관악구": "11620", "광진구": "11215", "구로구": "11530", "금천구": "11545",
        "노원구": "11350", "도봉구": "11320", "동대문구": "11230", "동작구": "11590",
        "마포구": "11440", "서대문구": "11410", "서초구": "11650", "성동구": "11200",
        "성북구": "11290", "송파구": "11710", "양천구": "11470", "영등포구": "11560",
        "용산구": "11170", "은평구": "11380", "종로구": "11110", "중구": "11140",
        "중랑구": "11260"
    }
    return gu_cd_map[gu]

# 현재 연월 (YYYYMM)
def get_current_ym():
    from datetime import datetime
    return datetime.now().strftime("%Y%m")

# XML 파싱 후 메시지 포맷
def parse_xml_and_format(xml_data, gu):
    root = ET.fromstring(xml_data)
    items = root.findall(".//item")

    if not items:
        return f"[{gu}] 데이터가 없습니다."

    messages = []
    for item in items[:5]:  # 최근 5개만
        try:
            apt_name = item.find("아파트").text
            deal_amount = item.find("거래금액").text.strip()
            deal_date = f"{item.find('년').text}.{item.find('월').text}.{item.find('일').text}"
            exclu_use_ar = item.find("전용면적").text
            messages.append(f"{deal_date} | {apt_name} | {exclu_use_ar}㎡ | {deal_amount}만원")
        except Exception as e:
            messages.append(f"[오류 발생] {e}")

    return f"[{gu}] 최신 거래\n" + "\n".join(messages)

# 메인 실행
if __name__ == "__main__":
    for gu in GUS:
        xml_data = get_apt_data(gu)
        message = parse_xml_and_format(xml_data, gu)
        bot.send_message(chat_id=CHAT_ID, text=message)




















