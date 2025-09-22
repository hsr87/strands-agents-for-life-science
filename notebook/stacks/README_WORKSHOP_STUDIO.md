# AWS Workshop Studio 배포 가이드

## 🎯 목적
이 문서는 AWS Workshop Studio 이벤트 엔진을 통해 Strands Agents for Life Science 워크샵을 자동으로 배포하는 방법을 설명합니다.

## 📋 배포 옵션

### 옵션 1: Workshop Studio Event Engine (권장)
이벤트 참가자들을 위한 완전 자동화 배포

### 옵션 2: 개인 AWS 계정
개인 학습을 위한 수동/반자동 배포

## 🚀 옵션 1: Workshop Studio Event Engine 설정

### 1. Event Blueprint 구성

Workshop Studio에서 이벤트 생성 시 다음 CloudFormation 템플릿을 사용:

```yaml
Template: event_engine_template.yaml
Stack Name: strands-workshop-auto
Region: us-east-1
```

### 2. 자동 배포 프로세스

이벤트 계정 생성 시 자동으로:
1. Bedrock 모델 액세스 활성화
2. 전체 인프라 스택 배포
3. SageMaker Studio 도메인 생성
4. 워크샵 자료 S3 업로드

### 3. 예상 시간
- 계정 프로비저닝: 5분
- 인프라 배포: 35-45분
- 총 소요 시간: 40-50분

## 💻 옵션 2: 개인 계정 배포

### Quick Start (자동 파라미터)

```bash
# 원클릭 배포 URL
https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/quickcreate?stackName=strands-workshop&templateURL=https://aws-workshop-templates-public.s3.amazonaws.com/strands-agents-life-science/master_stack.yaml&param_DatabaseName=agentdb&param_DBUsername=dbadmin&param_DBPassword=StrandsWorkshop2024!
```

### Manual Setup

```bash
# 1. 리포지토리 클론
git clone https://github.com/aws-samples/strands-agents-for-life-science.git
cd strands-agents-for-life-science/notebook/stacks

# 2. 셋업 스크립트 실행
./event_engine_setup.sh

# 3. 배포 상태 확인
aws cloudformation describe-stacks --stack-name strands-workshop-auto --query 'Stacks[0].StackStatus'
```

## 📁 파일 구조

```
stacks/
├── master_stack.yaml              # 메인 배포 템플릿
├── postgres_stack.yaml            # PostgreSQL 스택
├── kb_stack.yaml                  # Knowledge Base 스택
├── protein_design_stack.yaml      # 단백질 설계 스택
├── workshop_quickstart.yaml       # Quick Start 템플릿
├── event_engine_template.yaml     # Event Engine 자동 배포
├── event_engine_setup.sh          # 셋업 스크립트
└── README_WORKSHOP_STUDIO.md      # 이 문서
```

## 🔧 필수 사전 요구사항

### AWS 서비스 권한
- CloudFormation
- IAM
- VPC/EC2
- RDS
- S3
- Bedrock
- SageMaker
- HealthOmics

### Bedrock 모델 액세스
다음 모델들이 활성화되어야 함:
- Amazon Titan Embeddings G1 - Text
- Anthropic Claude 3.5 Sonnet
- Anthropic Claude 3 Sonnet

## 📊 배포 모니터링

### CloudFormation 콘솔
```
https://console.aws.amazon.com/cloudformation/home?region=us-east-1
```

### 스택 상태 확인
```bash
# 메인 스택 상태
aws cloudformation describe-stacks \
  --stack-name strands-workshop-auto \
  --query 'Stacks[0].StackStatus'

# 중첩 스택 확인
aws cloudformation list-stack-resources \
  --stack-name strands-workshop-auto \
  --query 'StackResourceSummaries[?ResourceType==`AWS::CloudFormation::Stack`]'
```

## 🎓 워크샵 시작하기

### 1. SageMaker Studio 접속
```
https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/studio
```

### 2. 코드 다운로드
```bash
git clone https://github.com/aws-samples/strands-agents-for-life-science.git
cd strands-agents-for-life-science/notebook/
```

### 3. 환경 설정
```bash
pip install -r requirements.txt
```

### 4. 첫 번째 노트북 실행
```
00-setup_environment.ipynb
```

## 🆘 문제 해결

### 일반적인 문제

| 문제 | 원인 | 해결 방법 |
|------|------|----------|
| Stack CREATE_FAILED | 권한 부족 | IAM 권한 확인 |
| Bedrock 모델 오류 | 모델 미활성화 | Bedrock 콘솔에서 활성화 |
| RDS 생성 실패 | 서브넷 문제 | us-east-1 리전 확인 |
| SageMaker 도메인 오류 | 기존 도메인 | 기존 도메인 사용 |

### 로그 확인
```bash
# CloudFormation 이벤트
aws cloudformation describe-stack-events \
  --stack-name strands-workshop-auto \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'

# Lambda 로그 (Event Engine)
aws logs tail /aws/lambda/strands-workshop-auto-setup --follow
```

## 📝 참고사항

### Workshop Studio 관리자용
1. 이벤트 생성 시 `event_engine_template.yaml` 사용
2. 참가자당 예상 비용: ~$50-100 (8시간 워크샵 기준)
3. 이벤트 종료 후 자동 정리 설정 권장

### 참가자용
1. 모든 인프라는 자동 배포됨
2. 배포 중에도 Lab 1 시작 가능
3. Lab 2는 배포 완료 후 진행

## 🔗 관련 링크

- [GitHub Repository](https://github.com/aws-samples/strands-agents-for-life-science)
- [AWS Workshop Studio](https://workshop.aws/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [AWS HealthOmics](https://aws.amazon.com/healthomics/)

## 📧 지원

문제 발생 시:
- GitHub Issues: https://github.com/aws-samples/strands-agents-for-life-science/issues
- AWS Support: https://console.aws.amazon.com/support/

---

*Last Updated: 2024*
*Version: 1.0*