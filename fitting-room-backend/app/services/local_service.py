import os
import shutil
import uuid
from PIL import Image

class LocalFileService:
    def __init__(self):
        # 저장할 기본 디렉토리 설정
        self.UPLOAD_DIR = "static/uploads"
        self.RESULT_DIR = "static/results"
        
        # 폴더가 없으면 생성 (에러 방지)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.RESULT_DIR, exist_ok=True)

    def save_upload_file(self, file_obj) -> str:
        """
        사용자가 업로드한 파일을 로컬에 저장하고 접근 URL 경로를 반환
        """
        # 고유 파일명 생성
        file_extension = file_obj.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.UPLOAD_DIR, unique_filename)

        # 파일 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj.file, buffer)
            
        # URL 경로 반환 (나중에 도메인을 붙여서 씀)
        return f"/static/uploads/{unique_filename}"

    def save_image_from_bytes(self, image: Image.Image) -> str:
        """
        Pillow 이미지 객체(AI 결과물)를 저장하고 접근 URL 경로를 반환
        """
        unique_filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(self.RESULT_DIR, unique_filename)
        
        image.save(file_path, format="PNG")
        
        return f"/static/results/{unique_filename}"