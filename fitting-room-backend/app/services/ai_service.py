from rembg import remove
from PIL import Image
import io
import time

class AIEngine:
    def __init__(self):
        print("🤖 AI Engine: 모델 로딩 중... (Rembg & VTON)")
        # 여기서 무거운 VTON 모델을 미리 로드해야 함 (예: Stable Diffusion Pipeline)
        # self.pipe = load_model(...) 
        print("✅ AI Engine: 준비 완료")

    def remove_background(self, image_bytes: bytes) -> Image.Image:
        """
        옷 이미지의 배경을 제거한다 (전처리 필수 과정)
        """
        input_image = Image.open(io.BytesIO(image_bytes))
        output_image = remove(input_image) # AI가 배경 제거
        return output_image

    def virtual_try_on(self, cloth_image: Image.Image, body_type: str) -> Image.Image:
        """
        [TODO] 실제 VTON 모델 인퍼런스가 들어갈 자리
        지금은 프로토타입 파이프라인 테스트를 위해 
        단순히 옷 이미지를 리사이징해서 돌려주는 Mock 기능을 수행함.
        """
        print(f"👕 피팅 시작: 체형={body_type}")
        
        # --- 실제 개발 시 이 부분에 IDM-VTON 등의 인퍼런스 코드가 들어감 ---
        # result = self.pipe(cloth_image, body_images[body_type])
        
        # TODO: 구현 필요
        time.sleep(2) 
        
        # (임시) 단순히 이미지를 리사이징해서 반환
        return cloth_image.resize((768, 1024))