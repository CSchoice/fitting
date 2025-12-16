import { useState } from "react";

// 백엔드 주소 (혹시 포트를 8001로 바꿨다면 여기를 수정해!)
const API_URL = "http://localhost:8000";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [bodyType, setBodyType] = useState("type_1"); // 기본 체형
  const [resultImage, setResultImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // 파일 선택 핸들러
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file)); // 미리보기 URL 생성
      setResultImage(null); // 새 이미지 올리면 결과 초기화
    }
  };

  // 피팅 요청 핸들러
  const handleTryOn = async () => {
    if (!selectedFile) {
      alert("옷 사진을 먼저 올려주세요!");
      return;
    }

    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("body_type", bodyType);
    formData.append("category", "upper_body"); // 일단 상의로 고정

    try {
      const response = await fetch(`${API_URL}/api/v1/try-on`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("서버 에러 발생");
      }

      const data = await response.json();
      // 백엔드가 준 결과 이미지 URL 저장
      setResultImage(data.result_image_url);
    } catch (error) {
      console.error(error);
      alert("피팅 실패! 백엔드 터미널을 확인하세요.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">
          👕 AI Virtual Fitting Room
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* 왼쪽: 입력 섹션 */}
          <div className="bg-white p-6 rounded-xl shadow-md space-y-6">
            {/* 1. 체형 선택 */}
            <div>
              <h3 className="text-lg font-semibold mb-3">1. 모델 체형 선택</h3>
              <div className="flex gap-2">
                {["type_1", "type_2", "type_3"].map((type) => (
                  <button
                    key={type}
                    onClick={() => setBodyType(type)}
                    className={`flex-1 py-3 rounded-lg border font-medium transition-colors
                      ${
                        bodyType === type
                          ? "bg-blue-600 text-white border-blue-600"
                          : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"
                      }`}
                  >
                    {type === "type_1"
                      ? "Slim"
                      : type === "type_2"
                      ? "Average"
                      : "Muscular"}
                  </button>
                ))}
              </div>
            </div>

            {/* 2. 옷 업로드 */}
            <div>
              <h3 className="text-lg font-semibold mb-3">2. 옷 사진 업로드</h3>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 transition-colors relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="h-48 mx-auto object-contain"
                  />
                ) : (
                  <div className="text-gray-400">
                    <p>클릭하여 옷 사진 업로드</p>
                    <p className="text-sm">(JPG, PNG)</p>
                  </div>
                )}
              </div>
            </div>

            {/* 3. 실행 버튼 */}
            <button
              onClick={handleTryOn}
              disabled={isLoading || !selectedFile}
              className={`w-full py-4 rounded-lg text-lg font-bold text-white transition-all
                ${
                  isLoading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl"
                }`}
            >
              {isLoading ? "AI가 옷을 입히는 중..." : "피팅 시작하기 ✨"}
            </button>
          </div>

          {/* 오른쪽: 결과 섹션 */}
          <div className="bg-white p-6 rounded-xl shadow-md flex flex-col items-center justify-center min-h-[400px]">
            <h3 className="text-lg font-semibold mb-4 w-full text-left">
              3. 피팅 결과
            </h3>

            {isLoading ? (
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-500 animate-pulse">
                  배경 제거 및 합성 중...
                </p>
              </div>
            ) : resultImage ? (
              <div className="w-full">
                <img
                  src={resultImage}
                  alt="Fitting Result"
                  className="w-full h-auto rounded-lg shadow-sm border"
                />
                <a
                  href={resultImage}
                  download
                  className="block w-full text-center mt-4 py-2 text-blue-600 hover:text-blue-800 font-medium"
                >
                  이미지 다운로드
                </a>
              </div>
            ) : (
              <div className="text-gray-400 text-center">
                <p>
                  왼쪽에서 옷을 선택하고
                  <br />
                  피팅을 시작해보세요!
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
