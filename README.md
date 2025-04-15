# 🤖 **Cano Bot**

**Cano Bot**은 Discord 서버에서 다양한 편의 기능을 제공하는 **다기능 Discord 봇**입니다.  
Python 학습을 목적으로 개발되었으며, 실생활에서 유용한 기능들을 직접 구현하며 확장해 나가고 있습니다.

---

## 🎯 **개발 목적**

- Python 실전 프로젝트 경험
- Discord 서버에서 필요한 편의 기능 직접 구현
- TTS, 게임 API, 서버 상태 등 다양한 기능 통합

---

## 🚀 **주요 기능**

### 🗣️ **TTS (Text-to-Speech)**
- 디스코드 음성 채널에서 실시간으로 텍스트 읽어주기

### 🎮 **게임 연동**
- **로스트아크 API**
  - 캐릭터 정보 조회 (장비, 능력치 등)
  - 거래소 아이템 시세 확인
- **마인크래프트 서버**
  - 개인 운영 중인 서버의 접속자 목록 확인
  - 서버 상태 모니터링

---

## 🛠 **기술 스택**

- **언어**: Python
- **라이브러리**: discord.py, Google TTS / pyttsx3, mcstatus
- **API**: 로스트아크 Open API

---

## 📸 **스크린샷**
> (추가 예정)

---

## 🧾 **사용 가능한 명령어**

### 🗣️ **TTS (음성 출력)**
- `!tts <메시지>` 또는 `!ㅅㅅㄴ <메시지>`  
  → 봇이 입력한 사람의 **음성 채널**에 접속해 메시지를 TTS로 읽어줍니다.
- `!나가`  
  → 봇이 음성 채널에서 퇴장합니다.

> ⚙ **사용 API**: [gTTS (Google Text-to-Speech)](https://pypi.org/project/gTTS/)

---

### 🎮 **마인크래프트 서버**
- `!마크 주소`  
  → 개인 운영 중인 마인크래프트 서버의 IP 주소 표시
- `!마크 접속자`  
  → 현재 접속 중인 인원과 닉네임 확인

> ⚙ **사용 API**: [mcstatus](https://github.com/Dinnerbone/mcstatus)

---

### 🔍 **로스트아크 연동**
- `!로아가격 <아이템명>`  
  → 최근 거래 가격, 현재 최저가, 어제 평균가, 최근 2주 거래량 및 가격 그래프 출력
- `!로아캐릭 <닉네임>`  
  → 해당 캐릭터의 상세 장비 및 능력치 정보 표시

> ⚙ **사용 API**: 로스트아크 Open API (RESTful 방식)

---

## ➕ **Cano Bot 추가하기**

[Cano Bot을 Discord 서버에 추가하려면 여기를 클릭하세요.](https://discord.com/oauth2/authorize?client_id=1352533887007330324&permissions=0&integration_type=0&scope=bot+applications.commands)

---

## 📝 **기타**

> 해당 봇은 개인 및 지인 서버에서 사용 중이며, 일부 기능은 API 키 또는 인증이 필요할 수 있습니다.
