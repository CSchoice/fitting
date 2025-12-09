from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "virtual-fitting-backend"
    environment: str = "dev"

    # Database
    database_url: str = "sqlite:///./data.db"

    # Storage (S3 or MinIO)
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "fitting"
    s3_region: str = "us-east-1"
    s3_secure: bool = False

    # Model checkpoints (paths or URLs)
    zero123_path: str = "./models/zero123"
    instantmesh_path: str = "./models/instantmesh"

    # Local temp dir
    tmp_dir: str = "./tmp"

    # Preset assets (defaults are placeholders; override via .env)
    preset_slim_gltf: str = "https://example.com/presets/slim.gltf"
    preset_slim_thumb: str = "https://example.com/presets/slim.png"
    preset_regular_gltf: str = "https://example.com/presets/regular.gltf"
    preset_regular_thumb: str = "https://example.com/presets/regular.png"
    preset_curvy_gltf: str = "https://example.com/presets/curvy.gltf"
    preset_curvy_thumb: str = "https://example.com/presets/curvy.png"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

