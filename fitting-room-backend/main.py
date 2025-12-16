import uvicorn
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles # 👈 필수 추가
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 로컬 서비스 임포트
from app.services.local_service import LocalFileService
from app.services.ai_service import AIEngine

local_service = None
ai_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global local_service, ai_engine
    print("🚀 서버 시작: 로컬 환경 모드")
    local_service = LocalFileService()
    ai_engine = AIEngine()
    yield
    print("🛑 서버 종료")

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 정적 파일 서빙 설정 (핵심!)
# http://도메인/static/... 으로 접속하면 static 폴더 내용을 보여줌
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Local VTON Backend is running!"}

@app.post("/api/v1/try-on")
async def try_on(
    request: Request, # 👈 현재 도메인을 알아내기 위해 필요
    file: UploadFile = File(...),
    body_type: str = Form(...),
    category: str = Form("upper_body")
):
    try:
        # 1. 원본 옷 저장 (로컬)
        # file.file 포인터를 복사하므로 read()보다 먼저 수행하거나 주의 필요
        # 여기서는 바로 저장 서비스로 넘김
        cloth_url_path = local_service.save_upload_file(file)
        
        # 2. AI 처리를 위해 다시 읽기 (포인터 초기화 필요)
        await file.seek(0)
        contents = await file.read()
        
        # 3. 배경 제거 (AI Engine)
        processed_cloth = ai_engine.remove_background(contents)
        
        # 4. 가상 피팅 (AI Engine - Mock)
        final_image = ai_engine.virtual_try_on(processed_cloth, body_type)
        
        # 5. 결과 저장 (로컬)
        result_url_path = local_service.save_image_from_bytes(final_image)
        
        # 6. 풀 URL 생성 (프론트엔드에서 접근 가능하도록)
        # ngrok을 쓰든 localhost를 쓰든 현재 접속한 주소(base_url)를 붙여줌
        base_url = str(request.base_url).rstrip("/")
        full_result_url = f"{base_url}{result_url_path}"
        full_cloth_url = f"{base_url}{cloth_url_path}"

        return {
            "status": "success",
            "message": "Fitting complete (Local Storage)",
            "original_image_url": full_cloth_url,
            "result_image_url": full_result_url 
        }

    except Exception as e:
        print(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)