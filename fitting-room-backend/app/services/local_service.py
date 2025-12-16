import os
import shutil
import uuid
from PIL import Image
from glob import glob

class LocalFileService:
    def __init__(self):
        # 폴더 구분: 옷(clothes) / 결과(results)
        self.CLOTH_DIR = "static/clothes"
        self.RESULT_DIR = "static/results"
        
        os.makedirs(self.CLOTH_DIR, exist_ok=True)
        os.makedirs(self.RESULT_DIR, exist_ok=True)

    def save_cloth(self, file_obj) -> str:
        """ 옷 사진을 저장하고 URL 경로 반환 """
        file_extension = file_obj.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.CLOTH_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj.file, buffer)
            
        return f"/static/clothes/{unique_filename}"

    def get_cloth_list(self):
        """ 저장된 모든 옷 사진 목록 반환 """
        # 최신순 정렬
        files = sorted(glob(os.path.join(self.CLOTH_DIR, "*")), key=os.path.getmtime, reverse=True)
        # 웹 경로로 변환
        return [f"/static/clothes/{os.path.basename(f)}" for f in files]

    def save_image_from_bytes(self, image: Image.Image) -> str:
        unique_filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(self.RESULT_DIR, unique_filename)
        image.save(file_path, format="PNG")
        return f"/static/results/{unique_filename}"
        
    def get_absolute_path(self, web_path: str):
        """ 웹 경로(/static/...)를 실제 파일 경로로 변환 """
        # 맨 앞의 '/' 제거
        if web_path.startswith("/"):
            web_path = web_path[1:]
        return os.path.join(os.getcwd(), web_path)