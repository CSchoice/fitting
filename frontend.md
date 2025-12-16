# 프론트엔드 계획 (MVP, React + Vite + Three.js)

## 1) 목표/범위
- 단일 SPA로 업로드 → 3D 생성 요청 → 프리셋 선택 → 피팅 결과 glTF 조회/뷰잉.
- 아바타 커스텀 입력 없음, 프리셋 3종 선택만 지원.
- 데모 우선: 빠른 응답, 명확한 로딩/상태 표시, 최소한의 폼/버튼.

## 2) 스택/도구
- React + Vite + TypeScript.
- 3D: three.js, react-three-fiber, @react-three/drei(OrbitControls, Environment).
- Data fetching: TanStack Query, axios.
- UI: 최소 컴포넌트(자체 스타일) 또는 lightweight UI lib(optional).
- 번들: code splitting, DRACO loader 포함.

## 3) 주요 페이지/플로우
- 메인 단일 페이지:
  1) 파일 업로드 영역
  2) 의상 3D 생성 상태 표시
  3) 아바타 프리셋 선택 카드
  4) 피팅 실행 버튼
  5) 결과 뷰어 + 상태/에러 표시
- 폴링으로 세션 상태 확인(`/session/{id}/result`), 필요시 웹소켓 확장 여지.

## 4) 컴포넌트 구조(예시)
- `AppLayout`: 헤더/본문/푸터, 토스트 컨테이너.
- `UploadPanel`: 이미지 업로드, `/clothes/upload-image`.
- `Generate3DPanel`: 3D 생성 트리거, 상태 표시(`/clothes/{id}/generate-3d`).
- `PresetSelector`: `/avatar-presets` 조회, 3카드 라디오 선택.
- `FitAction`: 피팅 실행(`/fit`).
- `ResultPanel`: `/session/{id}/result` 폴링, 다운로드/썸네일 링크.
- `Viewer3D`: react-three-fiber 기반 glTF 로더.
- `LoadingState`/`ErrorState` 공통 컴포넌트.

## 5) 상태/데이터 패칭
- TanStack Query로 각 API useQuery/useMutation 래핑.
- 키 예시:
  - `["avatar-presets"]`
  - `["cloth", clothId]`
  - `["cloth3d", cloth3dId]`
  - `["session", sessionId]` (폴링: refetchInterval 2~3s, status done/error 시 중단)
- 전역 상태는 최소화; 세션 ID/선택 프리셋은 상위 state + query 캐시 조합.

## 6) 3D 뷰어 구현
- react-three-fiber `Canvas` + `Suspense`.
- `GLTFLoader` + `DRACOLoader` (CDN 또는 로컬 wasm, 버전 고정).
- 조명: `Environment`(HDRI) + `hemisphereLight` + `directionalLight` 기본.
- 컨트롤: `OrbitControls`(회전/줌), 초기 카메라 포지션 고정.
- 모델 로딩 시:
  - 프리셋 아바타 glTF: 피팅 결과가 없을 때 기본 표시(optional).
  - 피팅 결과 glTF: done 상태 시 로드.
- 메쉬 수 줄이기 위해 R3F `useLoader` 결과를 캐시, unmount 시 dispose.

## 7) 업로드→생성→피팅 플로우
1) 사용자가 이미지 업로드 → `/clothes/upload-image` → cloth_id 획득.
2) “3D 생성” 클릭 → `/clothes/{id}/generate-3d` → cloth3d_id 반환, 상태 processing.
3) 프리셋 선택(slim/regular/curvy) → `avatar_preset_id` 보관.
4) “피팅” → `/fit`(cloth3d_id, avatar_preset_id) → fitting_session_id, status processing.
5) 폴링 `/session/{id}/result` → status done 시 `fitted_gltf_url` 로드하여 뷰어에 표시.

## 8) 에러/로딩/UX 가이드
- 모든 버튼에 로딩 스피너/비활성 처리.
- 업로드 실패/모델 실패 시 토스트 + 상세 로그 링크(없으면 단문 메시지).
- 타임아웃/대기: 폴링 2~3s, 최대 2~3분 경고 후 재시도 안내.
- 파일 제한: 확장자(jpg/png/webp), 크기(예: 10MB) 클라이언트 선검증.

## 9) 빌드/배포
- Vite build → 정적 산출물 S3 배포 → CloudFront 캐시.
- 환경변수: `VITE_API_BASE_URL`, `VITE_DRACO_PATH` 등.
- CI 단계: lint(TypeScript/ESLint), build. 테스트는 최소 smoke.

## 10) 테스트 전략(경량)
- 유닛: 업로드 유틸, 상태머신(단순 플로우) 테스트.
- 통합: 가짜 API(mock service worker)로 happy-path 플로우 테스트.
- E2E(옵션): Playwright/Cypress로 업로드→피팅→뷰 확인 한 시나리오.

## 11) 일정(프론트 관점 압축 4주)
- 주 1: 프로젝트 세팅(Vite/TS/R3F), 공용 UI/토스트, 업로드 패널, API 래퍼.
- 주 2: 3D 생성 패널 + 상태 표시, 프리셋 조회/선택 UI.
- 주 3: 피팅 호출/폴링, Viewer3D에서 결과 렌더, 에러/로딩 정리.
- 주 4: 스타일 다듬기, 빌드/배포 스크립트, 경량 테스트, 데모 리허설.

## 12) 추후 확장 메모
- 웹소켓 푸시로 폴링 대체, 멀티 세션 관리.
- 썸네일/리스트 뷰 추가, 최근 작업 히스토리.
- 간단한 로그인/토큰, 다국어(i18n).


