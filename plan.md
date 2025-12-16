전체 아키텍처 (MVP)
구성: React(Vite) SPA + Three.js 뷰어 → FastAPI 모놀리식(Uvicorn/Gunicorn) → 내부 Python AI 모듈 → S3/MinIO 오브젝트 스토리지 + RDB(SQLite 로컬, 추후 Postgres) → 단일 EC2(GPU) 호스트.
네트워크: CloudFront(정적 FE) → API Gateway/LB 없이 EC2 직접(초기) → S3/MinIO는 퍼블릭 리드(서명 URL) + 프라이빗 라이트.
프로세스: FastAPI 앱 하나에 REST + 백그라운드 워커(옵션: FastAPI BackgroundTasks / Celery+Redis-lite) 통합.
파일 경로: 원본 이미지·중간 멀티뷰·3D 결과(glTF/OBJ) 모두 S3/MinIO에 저장, DB에는 메타데이터/상태만 저장.
배포: Docker Compose 단일 호스트(서비스: api, minio, db). GPU 패스스루로 api 컨테이너에서 CUDA 사용.
기술 스택 (MVP 지향)
Frontend: React + Vite, TypeScript, Three.js, react-three-fiber + drei(편의), TanStack Query(데이터 패칭), Axios.
Backend: FastAPI, Pydantic v2, Uvicorn, SQLModel/SQLAlchemy, SQLite(파일), boto3(또는 minio-py), Pillow/Opencv-lite.
AI: 멀티뷰 생성 Zero123(또는 Zero123++), 3D 메시 추출 InstantMesh(경량), 대안: Shap-E(품질↓ 단순) / PIFuHD(인물 특화).
아바타: 사전 생성된 로우폴리 SMPL 프리셋 3종(slim/regular/curvy) glTF/DRACO, S3/MinIO에 저장하여 즉시 사용.
스토리지: MinIO(로컬 S3 호환) → prod 시 S3.
인프라: Docker + nvidia-container-runtime, 단일 GPU(예: T4/L4), CloudFront 정적 배포.
2D → 3D 의상 생성 파이프라인 (프로토타입)
입력: 단일 의류 전면 2D 이미지(배경 단색 권장).
단계:

1. 업로드 받은 이미지를 S3 저장, 배경 간략 제거(optional: rembg).
2. Zero123로 멀티뷰(8~16 view) 이미지 생성.
3. InstantMesh로 멀티뷰 → 포인트/메시 재구성(glTF/OBJ). 품질 튜닝: 해상도 512~768, 샘플 뷰 적게.
4. 메시 클린업: trimesh로 노이즈 제거/단순화, 스케일 정규화.
   기존 사례:
   Zero123 + InstantMesh 예제 레포 많음(Colab 다수) → 컨테이너화 쉬움.
   Shap-E 단독: 파이프라인 단순하지만 의류 디테일 낮음, “대략적” 데모에 적합.
   아바타 프리셋 (커스텀 생성 제거)
   사전 생성된 SMPL 로우폴리 아바타 3종(slim/regular/curvy) glTF/DRACO를 S3/MinIO에 저장.
   FastAPI는 프리셋 메타 반환만 수행(실시간 생성/스케일링 파이프라인 제거).
   필드 예: id, name, height_cm, notes, gltf_url, thumbnail_url.
   의상 피팅 알고리즘 (MVP, 무물리)
   파이프라인:
5. 의상 메시와 아바타를 공통 좌표계로 정규화(스케일/원점 힙 기준).
6. 카테고리별 단순 리타게팅 룰:
   상의: 바운딩박스 Y 정렬 + 어깨 폭 맞춤.
   하의: 힙 기준 정렬 + 다리 길이 스케일.
7. 최근접 점/스키닝 기반 스냅: 의상 버텍스를 아바타 표면 노멀 방향으로 소폭 오프셋(예: 3~5mm)해 충돌 최소화.
8. 겹침 최소 후 단순 레이어링: 의상 메시를 아바타보다 살짝 바깥쪽에 위치.
   추후 고도화: 바디 파트별 리지드 스킨 웨이트 전이, 간단한 Laplacian smoothing, Cloth simulation(Lite) 등 단계적 확장.
   API 설계 (FastAPI)
   POST /clothes/upload-image
   req: multipart/form-data file, user_id
   resp: { cloth_id, image_url, status: "uploaded" }
   POST /clothes/{id}/generate-3d
   req: { model: "zero123+instantmesh", quality: "low|med" }
   resp: { cloth3d_id, status: "processing" }
   GET /avatar-presets
   resp: [ { id, name, height_cm, gltf_url, thumbnail_url } ]
   POST /fit
   req: { cloth3d_id, avatar_preset_id }
   resp: { fitting_session_id, status: "processing" }
   GET /session/{id}/result
   resp 예: { status: "done", cloth3d_url, avatar_preset_id, fitted_gltf_url, thumb_url } (processing|error 포함)
   데이터 모델 / DB 스키마 (필수 필드)
   User: id, email, created_at
   Cloth: id, user_id, image_url, status(uploaded|failed), created_at
   Cloth3D: id, cloth_id, model_used, gltf_url, obj_url?, thumb_url?, status(processing|done|error), log, created_at
   AvatarPreset: id, name, height_cm, notes?, gltf_url, thumbnail_url, created_at
   FittingSession: id, user_id, cloth3d_id, avatar_preset_id, fitted_gltf_url, thumb_url, status(processing|done|error), created_at
   프론트엔드 설계 (React + Three.js)
   주요 컴포넌트:
   UploadPanel(이미지 업로드) → useMutation으로 /clothes/upload-image.
   PresetSelector(프리셋 카드 선택) → /avatar-presets.
   Viewer3D(react-three-fiber): OrbitControls, HDRI/pmrem light, GLTFLoader/DRACOLoader.
   ResultPanel: 폴링으로 /session/{id}/result 확인 후 뷰어에 glTF 로드.
   흐름: 파일 업로드 → 3D 생성 요청 → 프리셋 선택 → /fit → 폴링/웹소켓로 결과 → Viewer3D에서 glTF 로딩, 회전/줌/애니메이션 없음.
   glTF 로더: DRACO 압축 지원, useLoader(GLTFLoader, url) + suspense.
   상태 관리: TanStack Query로 캐시/리트라이, 로딩 상태 표준화.
   성능·비용 최적화 (MVP)
   glTF: DRACO 압축 + 텍스처 1K 이하, mesh decimation(10~20k tri).
   GPU: T4/L4 on-demand, inference는 직렬/소량 병렬; 백그라운드 태스크 큐로 API 응답 빠르게 반환.
   비동기 처리: FastAPI BackgroundTasks(초기) → 필요 시 Celery+Redis 전환.
   스토리지 비용: 중간 산출물 주기적 정리, 썸네일만 장기 보관.
   캐시: CloudFront 정적 리소스, 결과 glTF는 서명 URL 단기 캐시.
   개발 인력/일정 (4~8주, FE1/BE1/AI1)
   1주차: 요구정의/와이어프레임/인프라 도커 스캐폴드.
   2주차: FE 업로드/뷰어 기본, BE 업로드/DB/스토리지 연동.
   3~4주차: AI 파이프라인 컨테이너라이즈(Zero123+InstantMesh) + API 연동.
   5주차: 아바타 프리셋 3종 준비/업로드, /avatar-presets 엔드포인트, FE 프리셋 선택 UI.
   6주차: 피팅 파이프라인(정렬/스냅), 결과 뷰어 통합.
   7주차: 안정화/에러 핸들링/로깅/모니터링 최소.
   8주차: 배포(EC2+S3/MinIO+CloudFront), 데모 리허설.
   리스크: 모델 성능/속도 변동 → 품질 파라미터 낮추고 타임아웃 관리. SMPL 라이선스/모델 파일 관리 → 내부 배포/액세스 제어. GPU 드라이버 이슈 → nvidia-container-runtime 테스트.
   MVP 스코프 정의
   데모 가능 기준:
   단일 의류 이미지 업로드 → 3D 의상(저폴리) 생성 성공.
   프리셋 선택 → 의상-아바타 간 단순 피팅 glTF 제공, 웹 뷰어에서 회전/줌 가능.
   다음 버전으로 미룸: 고품질 천 시뮬, 모션/포즈 애니메이션, 고해상 텍스처 베이크, 실측 보정, 멀티카테고리 정밀 리타게팅, 인증/결제/멀티테넌시.
   추가 구현 메모
   백엔드 컨테이너에 AI 모델(Zero123, InstantMesh) 체크포인트를 미리 bake하거나 런타임에 S3/Weights 저장소에서 lazy download.
   에러/상태: 모든 비동기 작업은 status 필드와 log를 DB에 저장해 FE에서 노출.
   보안: 초기엔 토큰 없이 데모 가능하되, 프록시 차단/업로드 크기 제한(예: 10MB) 적용.
   모니터링: 최소 Prometheus/Grafana or CloudWatch metrics, 로깅은 구조화 JSON.
