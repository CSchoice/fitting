import uvicorn
import io
import os
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.services.local_service import LocalFileService
from app.services.ai_service import AIEngine

local_service = None
ai_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global local_service, ai_engine
    # 서버 시작 시 서비스 초기화
    local_service = LocalFileService()
    ai_engine = AIEngine()
    yield

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/v1/clothes")
def get_clothes(request: Request):
    """ 저장된 옷 목록 반환 """
    paths = local_service.get_cloth_list()
    base_url = str(request.base_url).rstrip("/")
    return [f"{base_url}{p}" for p in paths]

@app.post("/api/v1/clothes")
async def upload_cloth(request: Request, file: UploadFile = File(...)):
    """ 옷 업로드 및 저장 """
    path = local_service.save_cloth(file)
    base_url = str(request.base_url).rstrip("/")
    return {"url": f"{base_url}{path}"}

@app.post("/api/v1/try-on")
async def try_on(
    request: Request,
    person_image: UploadFile = File(...),
    cloth_url: str = Form(...),
    category: str = Form("upper_body") # 👈 [핵심] 프론트에서 보낸 카테고리 받기
):
    try:
        # 1. 내 사진 읽기
        person_bytes = await person_image.read()
        person_img = Image.open(io.BytesIO(person_bytes))
        
        # 2. 선택한 옷 이미지 경로 찾기
        relative_path = "/static" + cloth_url.split("/static")[-1]
        real_cloth_path = local_service.get_absolute_path(relative_path)
        
        if not os.path.exists(real_cloth_path):
            raise HTTPException(status_code=404, detail="Cloth image not found")
            
        cloth_img = Image.open(real_cloth_path)

        # 3. 옷 배경 제거
        processed_cloth = ai_engine.remove_background(cloth_img)
        
        # 4. 피팅 실행 (카테고리 전달!)
        # 👇 [핵심] 여기에 category를 꼭 넣어줘야 에러가 안 남!
        final_image = ai_engine.virtual_try_on(processed_cloth, person_img, category)
        
        # 5. 결과 저장
        result_url_path = local_service.save_image_from_bytes(final_image)
        base_url = str(request.base_url).rstrip("/")
        
        return {
            "status": "success",
            "result_image_url": f"{base_url}{result_url_path}"
        }

    except HTTPException:
        # Re-raise HTTPException (like 404) without wrapping in 500
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 포트 8001번 사용
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)