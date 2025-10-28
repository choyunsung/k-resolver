# 🚀 K-Resolver 배포 가이드

## GitHub Actions 자동 배포 설정

### 1. GitHub Secrets 설정

저장소 Settings → Secrets and variables → Actions에서 다음 시크릿을 추가하세요:

#### 필수 시크릿

- **DOCKER_USERNAME**: Docker Registry 사용자명
- **DOCKER_PASSWORD**: Docker Registry 비밀번호

#### 선택 시크릿

- **SLACK_WEBHOOK**: Slack 알림을 받으려면 Webhook URL 추가

### 2. Self-hosted Runner 설정 (배포 서버)

배포 서버에서 다음 작업을 수행하세요:

#### 2.1 GitHub Runner 설치

```bash
# 서버에 접속
ssh your-server

# Runner 디렉토리 생성
mkdir -p ~/actions-runner && cd ~/actions-runner

# Runner 다운로드 (최신 버전 확인: https://github.com/actions/runner/releases)
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# 압축 해제
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Runner 설정
./config.sh --url https://github.com/choyunsung/k-resolver --token YOUR_RUNNER_TOKEN --labels k-resolver
```

**Runner Token 얻기:**
1. GitHub 저장소 → Settings → Actions → Runners
2. "New self-hosted runner" 클릭
3. 토큰 복사

#### 2.2 Runner를 서비스로 등록

```bash
# 서비스 설치
sudo ./svc.sh install

# 서비스 시작
sudo ./svc.sh start

# 상태 확인
sudo ./svc.sh status
```

#### 2.3 필요한 도구 설치

```bash
# Podman 또는 Docker 설치
# Podman (권장)
sudo apt update
sudo apt install -y podman podman-compose

# 또는 Docker
# sudo apt install -y docker.io docker-compose

# Git 설치
sudo apt install -y git

# 배포 디렉토리 생성
sudo mkdir -p /data/k-resolver
sudo chown $USER:$USER /data/k-resolver
```

### 3. 배포 프로세스

#### 자동 배포 (권장)

main 브랜치에 푸시하면 자동으로 배포됩니다:

```bash
git push origin main
```

배포 단계:
1. **Build**: Docker 이미지 빌드 (멀티 플랫폼: amd64, arm64)
2. **Push**: Docker Registry에 푸시
3. **Deploy**: 서버에서 컨테이너 재시작
4. **Migrate**: 데이터베이스 마이그레이션 자동 실행
5. **Notify**: Slack 알림 (설정한 경우)

#### 수동 배포

GitHub Actions 페이지에서 "Run workflow" 버튼 클릭

### 4. 서버 초기 설정

배포 서버에서 처음 한 번만 실행:

```bash
# 배포 디렉토리로 이동
cd /data/k-resolver

# 환경 변수 설정
cp .env.example .env
nano .env  # 데이터베이스 비밀번호 등 수정

# 초기 데이터 시드
podman-compose exec api python scripts/seed_data.py
```

### 5. 배포 확인

```bash
# 서비스 상태 확인
cd /data/k-resolver
podman-compose ps

# 로그 확인
podman-compose logs -f api

# 헬스체크
curl http://localhost:8000/health

# API 테스트
curl http://localhost:8000/api/isps
```

### 6. Nginx/OpenResty 설정 (선택사항)

서비스를 도메인으로 노출하려면:

```nginx
# /etc/nginx/sites-available/k-resolver.conf
server {
    listen 80;
    server_name k-resolver.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

SSL 인증서 설정:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d k-resolver.yourdomain.com
```

### 7. 데이터베이스 백업 (권장)

정기적인 백업을 위한 크론잡:

```bash
# 백업 스크립트 생성
cat > ~/backup-k-resolver.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/data/backups/k-resolver"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# PostgreSQL 백업
podman exec k-resolver-db pg_dump -U kresolver kresolver | gzip > $BACKUP_DIR/kresolver_$DATE.sql.gz

# 7일 이상된 백업 삭제
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
EOF

chmod +x ~/backup-k-resolver.sh

# 크론잡 추가 (매일 새벽 3시)
crontab -e
# 다음 줄 추가:
# 0 3 * * * /home/yourusername/backup-k-resolver.sh
```

### 8. 모니터링 (선택사항)

#### Watchtower로 자동 업데이트

```bash
podman run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 300 \
  k-resolver-api
```

#### 로그 모니터링

```bash
# 실시간 로그
journalctl -u actions.runner.* -f

# 서비스 로그
podman-compose logs -f --tail=100
```

### 9. 롤백 방법

문제가 발생하면 이전 버전으로 롤백:

```bash
cd /data/k-resolver

# 이전 이미지 태그로 변경
# compose.yml에서 image 태그를 이전 커밋 SHA로 수정
nano compose.yml

# 컨테이너 재시작
podman-compose up -d

# 또는 특정 태그 사용
podman pull docker.quetta-soft.com/yunsung/k-resolver:abc1234
podman tag docker.quetta-soft.com/yunsung/k-resolver:abc1234 docker.quetta-soft.com/yunsung/k-resolver:latest
podman-compose up -d
```

### 10. 트러블슈팅

#### 컨테이너가 시작되지 않음

```bash
# 로그 확인
podman-compose logs api

# 이미지 재빌드
podman-compose build --no-cache
podman-compose up -d
```

#### 데이터베이스 연결 실패

```bash
# 데이터베이스 상태 확인
podman-compose ps db

# 데이터베이스 재시작
podman-compose restart db

# 연결 테스트
podman-compose exec db psql -U kresolver -d kresolver -c "SELECT 1"
```

#### Runner가 작동하지 않음

```bash
# Runner 상태 확인
cd ~/actions-runner
sudo ./svc.sh status

# 재시작
sudo ./svc.sh stop
sudo ./svc.sh start

# 로그 확인
journalctl -u actions.runner.* -f
```

## 보안 체크리스트

- [ ] `.env` 파일에 강력한 데이터베이스 비밀번호 설정
- [ ] GitHub Secrets에 민감 정보 저장
- [ ] 방화벽 설정 (필요한 포트만 개방)
- [ ] SSL/TLS 인증서 설치
- [ ] 정기적인 데이터베이스 백업
- [ ] 로그 모니터링 설정
- [ ] Runner 서버 보안 업데이트

## 참고 링크

- GitHub Actions: https://github.com/choyunsung/k-resolver/actions
- Docker Registry: https://docker.quetta-soft.com
- Self-hosted Runner 설정: https://docs.github.com/en/actions/hosting-your-own-runners
