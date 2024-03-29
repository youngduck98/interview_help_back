# interview_help_back
cau 4-1 semester capstone project, this project is designed to provide simulation.

- 사용된 기술 스택
    - 언어: python(이유: ai module을 사용하기 위해)
    - 프레임워크: flask(이유: 확장성이 높아서-프로젝트에 사용될 기술이 명확히 정해지지 않은 상태에서 공부하여야 했음)
    - 라이브러리: sqlArchemy, flask restx
    - 데이터베이스: mysql(이유: 오픈소스 + 숙련도)
    
- 프로젝트 목적 및 기능
    - 해당 프로젝트를 하게 된 이유
        
        ```
        면접 준비는 많은 사람들에게 중대한 과제이며, 효과적인 준비는 성공적인 경력 개발로 이어집니다. 
        이를 인식하고, 저와 저의 팀원은 기술을 활용하여 이 과정을 지원하고 싶었습니다. 
        특히 기존 서비스의 경우 사용자에 특화된 질문을 제공하거나 사용자 답변의 내용까지는 판단해 주지 못하였는데, 
        당시 화제가 되었던 gpt-api를 활용하여 이러한 점을 보완할 수 있다 생각하여 서비스를 기획하게 되었습니다.
        ```
        
    - 프로젝트의 목적
        
        ```
        이 서비스는 사용자가 제출한 자기소개서를 분석하여 맞춤형 면접 질문을 생성함으로써, 
      사용자가 실제 면접 상황에서 자신감을 가지고 대응할 수 있도록 준비시킵니다. 
      또한, 사용자의 답변을 평가하여 실시간 피드백을 제공함으로써, 스스로 개선과 성찰을 가능하게 하고 
      의견을 나눌 수 있는 커뮤니티를 제공함으로써 지속적인 참여와 소통을 독려하는 것을 목적으로 합니다.
        ```
        
    - 기능(중요도 순 내림차순)
        
        ```
        1. 자기소개서를 기반으로 하여 사용자에 특화된 면접 질문 생성
        2. 각 직무별 기줄 질문과 생성된 질문을 활용하여 사용자에게 적합한 면접 시뮬레이션을 진행
        3. 면접 시뮬레이션에서의 사용자 답변에 기초하여 각 대답 별 피드백과 전체 면접에 대한 점수를 제공
        4. 한번 진행하였던 면접을 반복하여 다시 진행할 수 있는 기회 제공
        5. 본인의 면접 점수 추이를 살펴볼 수 있는 그래프 기능 제공
        6. 기출 문제에 대해 사람들과 의견을 나눌 수 있는 커뮤니티 기능 제공
        7. 본인의 github를 분석할 수 있는 기능 제공(사용한 언어의 %정도만 나와 있고 후에 리펙토링 하게 된다면 다른 분석 기능도 추가할 예정)
        ```
        
- 담당 역할 및 기여한 점(구현한 주요 기능에 대한 비즈니스 로직 + 문서 작성, 버그 수정, 기능 개선을 포함)
    
    ```
    1. 필요 기능 기획 및 api문서 기획
    2. 사용자 정보에 따른 면접 질문지 생성과 사용자 답변 채점에 대한 비즈니스 로직 기획 및 구현
    3. flask 서버 구현 및 aws-ec2를 활용한 배포
    4. database 설계 및 정규화
    5. mysql, aws-rds 를 활용한 database 구축
    6. swap 공간 할당과 같은 ai 모듈을 위한 Linux 환경설정 과정
    ```
    
- 성과
    - 2023 CAU 공학 학술제에서 학장 상 수상
    
- 관련 사진/링크/샘플 코드
    - db
      - https://dbdiagram.io/d/6455e51ddca9fb07c49aa985
        
    - database 설계
      - https://dynamic-ice-676.notion.site/database-25fde371b6684d7d8698fc12c51b7fb7?pvs=4
        
    - api 문서(notion 참고)
      - [https://dynamic-ice-676.notion.site/interviewMaster-2023-3-2023-6-2f46ba9fe9614fe9a5391a3043cd3543?pvs=4)
      - [5.17~5.18 capstone 작업량.txt](https://github.com/youngduck98/interview_help_back/blob/main/file/5-19%20capstone%20%EC%9E%91%EC%97%85%EB%9F%89.txt)
      - [5-19 capstone 작업량.txt](https://github.com/youngduck98/interview_help_back/blob/main/file/5.17~5.18%20capstone%20%EC%9E%91%EC%97%85%EB%9F%89.txt)
      - [self_introduction_document.txt](file%2Fself_introduction_document.txt)
      
