import requests
import telegram
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import time

# 환경변수에서 서비스 키와 텔레그램 정보 가져오기
SERVICE_KEY = os.environ["SERVICE_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = telegram.Bot(token=TELEGRAM_TOKEN)

# 서울 구 리스트
GUS = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구",
    "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구",
    "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구",
    "은평구", "종로구", "중구", "중랑구"
]

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

def get_current_ym():
    return datetime.now().strftime("%Y%m")

def get_apt_data(gu):
    url = "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
    params = {
        "serviceKey": SERVICE_KEY,
        "LAWD_CD": get_lawd_cd(gu),
        "DEAL_YMD": get_current_ym()
    }
    r = requests.get(url, params=params)
    xml_data = r.text
    print(f"[{gu}] 응답 원문: {xml_data[:500]}")
    return xml_data

def parse_xml_and_format(xml_data, gu):
    root = ET.fromstring(xml_data)
    items = root.findall(".//item")
    if not items:
        return f"[{gu}] 데이터가 없습니다."

    messages = []
    for item in items[:5]:
        try:
            apt_name = item.find("아파트").text
            deal_amount = item.find("거래금액").text.strip()
            deal_date = f"{item.find('년').text}.{item.find('월').text}.{item.find('일').text}"
            exclu_use_ar = item.find("전용면적").text
            messages.append(f"{deal_date} | {apt_name} | {exclu_use_ar}㎡ | {deal_amount}만원")
        except Exception as e:
            messages.append(f"[오류 발생] {e}")

    return f"[{gu}] 최신 거래\n" + "\n".join(messages)

if __name__ == "__main__":
    for gu in GUS:
        try:
            xml_data = get_apt_data(gu)
            message = parse_xml_and_format(xml_data, gu)
            bot.send_message(chat_id=CHAT_ID, text=message)
            time.sleep(1)
        except Exception as e:
            print(f"[{gu}] 처리 중 오류 발생: {e}")
