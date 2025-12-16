import os
import shutil
import time
from gradio_client import Client, handle_file
from PIL import Image, ImageEnhance # 👈 ImageEnhance 추가 필수!

class AIEngine:
    def __init__(self):
        print("🤖 AI Engine: IDM-VTON (Warping Mode) 초기화 중...")
        try:
            self.client = Client("yisol/IDM-VTON")
            print("   ✅ IDM-VTON 엔진 연결 성공! (Remote GPU)")
        except Exception as e:
            print(f"   ❌ 엔진 연결 실패: {e}")
            self.client = None

    def remove_background(self, image: Image.Image) -> Image.Image:
        from rembg import remove
        return remove(image.convert("RGB"))

    # === [신규 추가] 옷 화질 개선 함수 ===
    def enhance_cloth(self, image: Image.Image) -> Image.Image:
        """
        AI가 옷의 특징을 더 잘 잡도록 선명도와 콘트라스트를 강조
        """
        # 1. 선명도 강화 (흐릿한 로고 방지)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2) # 20% 더 선명하게

        # 2. 색상 대비 강화 (주름/질감 강조)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1) # 10% 더 진하게
        
        # 3. 색 농도 강화 (물빠짐 방지)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)

        return image

    def virtual_try_on(self, cloth_image: Image.Image, person_image: Image.Image, category: str) -> Image.Image:
        print(f"\n📢 [IDM-VTON] 피팅 요청: 카테고리={category}")
        
        if self.client is None:
            print("🚨 엔진이 연결되지 않았습니다.")
            return cloth_image

        # 1. 파일 임시 저장용 폴더
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = int(time.time())
        person_path = f"{temp_dir}/person_{timestamp}.png"
        cloth_path = f"{temp_dir}/cloth_{timestamp}.png"
        
        # === [수정] 저장하기 전에 옷 화질 개선 적용 ===
        print("   ✨ 옷 이미지 화질 개선(Enhancing) 적용 중...")
        enhanced_cloth = self.enhance_cloth(cloth_image)
        
        person_image.save(person_path)
        enhanced_cloth.save(cloth_path) # 개선된 이미지를 저장

        # 2. 카테고리 매핑
        vton_desc = "short sleeve shirt"
        if category == "lower_body":
            vton_desc = "trousers"
        elif category == "dresses" or category == "outer":
            vton_desc = "dress"
        elif category == "upper_body":
            vton_desc = "shirt"

        print("   🚀 원격 GPU로 데이터 전송 및 처리 시작 (약 15~30초 소요)...")
        
        try:
            result = self.client.predict(
                {"background": handle_file(person_path), "layers": [], "composite": None},
                handle_file(cloth_path),
                vton_desc,
                True,      # Auto-masking
                30,        # Steps
                30,        # Seed
                api_name="/tryon"
            )
            
            print(f"   ✅ 처리 완료! 결과 경로: {result}")
            
            if not result:
                raise ValueError("서버응답이 비어있습니다")

            if isinstance(result, (list, tuple)):
                final_image_path = result[0]
            else:
                final_image_path = result

            final_image = Image.open(final_image_path)
            return final_image

        except Exception as e:
            print(f"   💥 IDM-VTON 처리 중 에러: {e}")
            return cloth_image