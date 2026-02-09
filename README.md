# 프로젝트 개요
* 개발 기간 : 2025.09.02 ~ 2025.09.03
* 개발 인원 : 5인
* 핵심역할 : 끝말잇기 게임
* 주요 특징
    * MVC 패턴 기반의 깔끔한 소스 구조 (Controller, DAO, DTO 분리)
    * 좌석 예매, 음식/굿즈 주문, 경기 일정 관리 기능을 통합한 올인원 플랫폼
    * 사용자 권한(User/Admin)에 따른 차별화된 대시보드 제공

# Tech Stack
* Backend : Java (Servlet), JDBC
* Frontend : JSP, HTML5, CSS3, JavaScript
* Database : Oracle DB, H2
* Server : Apache Tomcat

# 핵심 기능
1. 스마트 티켓 예매 시스템 (project1)
    * 실시간 좌석 선택 : SeatDAO를 통해 좌석 현황을 파악하고 등급별(내야/외야 등) 가격 정책(Ticket_priceDTO) 반영
    * 예매 프로세스 : 인원 선택 → 좌석 지정 → 결제 확인까지 이어지는 단계별 서비스 로직 구현

2. 푸드 및 굿즈 이커머스 (baseballSystem.Controller)
    * 장바구니 및 주문 : 야구장의 꽃인 먹거리 주문 시스템(FoodController)과 굿즈 판매 시스템(ProductController) 운영
    * 결제 처리 : 장바구니 데이터를 기반으로 최종 금액을 산출하고 주문 내역을 DB에 기록

3. 관리자 대시보드 (admin)
    * 시스템 제어 : 관리자 권한을 통해 경기 스케줄을 업데이트하거나(ScheduleController), 전체 회원 및 판매 현황 관리
    * 데이터 영속성 : Oracle DB와 연동하여 모든 트랜잭션 데이터를 안전하게 관리

4. 사용자 인증 관리 (login, AuthFilter)
    * 세션 관리 : AuthFilter를 통한 보안 강화 및 사용자 로그인 상태 유지
    * 권한 분리 : 일반 사용자와 관리자의 접근 가능 메뉴를 구분하여 설계
