1) 서비스 구조 및 실행
단일 FastAPI 앱(monolith) + Uvicorn/Gunicorn.
Docker Compose: api(CUDA 사용), minio(S3 호환), db(SQLite 파일). Prod 전환 시 S3/PG.
옵션: 초기엔 FastAPI BackgroundTasks로 비동기 처리, 추후 Celery+Redis 전환 가능.
2) 모듈 구조 제안
app/main.py: 엔트리, 라우터 include, CORS, 예외 핸들러.
app/config.py: 환경변수/비밀키 로드(pydantic BaseSettings).
app/models.py: SQLModel/SQLAlchemy 모델(User, Cloth, Cloth3D, AvatarPreset, FittingSession).
app/schemas.py: 요청/응답 Pydantic 스키마.
app/storage.py: S3/MinIO 클라이언트(boto3/minio-py), presigned URL 생성.
app/ai/: Zero123, InstantMesh 파이프라인 래퍼, 경량 utils(rembg 옵션).
app/fitting.py: 무물리 피팅 로직(정규화/정렬/스냅/레이어링).
app/routers/: clothes, avatar_presets, fitting, session.
app/tasks.py: 비동기 태스크 진입점(BackgroundTasks/Celery 호환).
app/logger.py: 구조화 로깅(json), request/response 로깅 미들웨어.
3) 엔드포인트 상세
POST /clothes/upload-image
form-data: file, user_id(optional)
동작: 이미지 S3 업로드 → Cloth row 생성(status=uploaded) → 메타 반환.
POST /clothes/{id}/generate-3d
body: { model: "zero123+instantmesh", quality: "low|med" }
동작: 상태 processing → 백그라운드에서 Zero123 멀티뷰 → InstantMesh → 클린업/DRACO → S3 업로드 → Cloth3D row status=done.
GET /avatar-presets
동작: DB 시딩된 3건 반환.
POST /fit
body: { cloth3d_id, avatar_preset_id }
동작: 피팅 태스크 enqueue → 단순 스냅/레이어링 → fitted glTF S3 업로드 → FittingSession status=done.
GET /session/{id}/result
동작: 상태/URL 반환(processing|done|error).
4) 데이터 모델 (요약)
User(id, email, created_at)
Cloth(id, user_id, image_url, status, created_at)
Cloth3D(id, cloth_id, model_used, gltf_url, obj_url?, thumb_url?, status, log, created_at)
AvatarPreset(id, name, height_cm, notes?, gltf_url, thumbnail_url, created_at)
FittingSession(id, user_id, cloth3d_id, avatar_preset_id, fitted_gltf_url, thumb_url, status, created_at)
5) 파이프라인 구현 메모
업로드: 파일 크기 제한(예: 10MB), MIME 검증, 임시 디스크 저장 후 S3 put.
2D→3D:
rembg(optional) → Zero123 멀티뷰(8~16) → InstantMesh 재구성 → trimesh 클린업(노이즈 제거, decimation, scale normalize) → glTF/OBJ + DRACO.
파라미터: 해상도 512~768, 샘플뷰 축소로 속도 우선.
피팅(무물리):
공통 좌표계 정규화(힙/원점 기준).
카테고리 룰(상의/하의)로 위치/스케일 정렬.
최근접 노멀 방향 오프셋(3~5mm)으로 겹침 완화.
레이어링: 아바타 외곽으로 살짝 이동.
프리셋: glTF/DRACO 3종은 빌드 타임/부트 시 S3에 존재, API는 메타만 반환. 로컬 캐시로 로딩 속도 개선.
6) 설정/배포
환경변수: DB_URL, S3_ENDPOINT/KEY/SECRET/BUCKET, MODEL_PATH(Zero123/InstantMesh 체크포인트), TMP_DIR, LOG_LEVEL.
Dockerfile: nvidia/cuda 베이스, 모델 가중치 다운로드 스텝 포함 또는 런타임 lazy download.
헬스체크: /healthz (DB/S3 간단 체크).
로깅/모니터링: json logger, 간단한 request time 미들웨어, Prometheus/OpenTelemetry 옵션.
7) 에러/상태 관리
모든 비동기 작업은 status 필드(processing|done|error) + log 컬럼에 에러 메시지 기록.
4xx: 입력 검증, 5xx: 파이프라인 실패.
타임아웃: Zero123/InstantMesh 실행 시 상한(예: 120~180s) 설정.
8) 시딩/마이그레이션
초기 시딩: AvatarPreset 3건 insert.
마이그레이션: SQLite → Alembic(optional) 또는 초기 단계는 테이블 생성 스크립트로 단순화.
9) 테스트 전략
단위: storage mock(S3), ai 파이프라인은 stub로 대체, 피팅 함수 입력/출력 형태 검증.
통합: /clothes/* 업로드→generate-3d 모의 태스크, /fit에서 프리셋/의상 ID 검증 흐름.
부하: 소량 동시 요청으로 큐 처리/DB 락 확인.
10) 일정(백엔드 관점 압축)
주 1: 프로젝트 스캐폴드, 모델/스키마/스토리지 클라이언트, 업로드 API.
주 2: Zero123+InstantMesh 파이프라인 래퍼, generate-3d 연동, 상태 저장.
주 3: 아바타 프리셋 시딩/엔드포인트, 피팅 파이프라인 초안, /fit 완료.
주 4: 안정화(에러 핸들링, 로깅, 타임아웃), 헬스체크, 간단 테스트.