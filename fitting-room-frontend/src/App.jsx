import { useState, useEffect } from "react";

// 백엔드 포트 확인 (8001로 설정했으므로 유지)
const API_URL = "http://localhost:8001";

function App() {
  // === 상태 관리 (State Management) ===

  // 1. 옷장(Closet) 관련 상태
  const [clothes, setClothes] = useState([]);
  const [selectedCloth, setSelectedCloth] = useState(null);
  const [isUploadingCloth, setIsUploadingCloth] = useState(false);

  // 2. 피팅룸(Fitting Room) 관련 상태
  const [myPhoto, setMyPhoto] = useState(null);
  const [myPhotoPreview, setMyPhotoPreview] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [isFitting, setIsFitting] = useState(false);
  const [category, setCategory] = useState("upper_body"); // 기본값: 상의

  // === 초기화 및 API 통신 ===

  // 화면 로딩 시 옷 목록 가져오기
  useEffect(() => {
    fetchClothes();
  }, []);

  const fetchClothes = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/clothes`);
      if (!res.ok) throw new Error("Failed to fetch");
      const data = await res.json();
      setClothes(data);
    } catch (err) {
      console.error("옷 목록 로딩 실패:", err);
    }
  };

  // 옷 업로드 핸들러
  const handleUploadCloth = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploadingCloth(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/api/v1/clothes`, {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        await fetchClothes(); // 목록 갱신
      } else {
        alert("옷 업로드에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("서버 연결 오류");
    } finally {
      setIsUploadingCloth(false);
    }
  };

  // 내 사진 선택 핸들러
  const handleMyPhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setMyPhoto(file);
      setMyPhotoPreview(URL.createObjectURL(file));
      setResultImage(null); // 새 사진 올리면 기존 결과 초기화
    }
  };

  // 피팅 시작 핸들러
  const handleTryOn = async () => {
    if (!selectedCloth) return alert("옷장에서 입을 옷을 선택해주세요!");
    if (!myPhoto) return alert("본인의 전신 사진을 업로드해주세요!");

    setIsFitting(true);

    // API로 전송할 데이터 구성
    const formData = new FormData();
    formData.append("person_image", myPhoto); // 내 사진 파일
    formData.append("cloth_url", selectedCloth); // 선택한 옷의 경로
    formData.append("category", category); // 선택한 카테고리 (upper/lower)

    try {
      const res = await fetch(`${API_URL}/api/v1/try-on`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Fitting Failed");

      const data = await res.json();
      if (data.result_image_url) {
        setResultImage(data.result_image_url);
      } else {
        alert("이미지 생성에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("피팅 실패! 백엔드 터미널의 에러 로그를 확인하세요.");
    } finally {
      setIsFitting(false);
    }
  };

  // === UI 렌더링 ===
  return (
    <div className="min-h-screen bg-gray-100 p-4 md:p-8 flex flex-col items-center">
      <h1 className="text-3xl md:text-4xl font-extrabold text-gray-800 mb-8 tracking-tight">
        🛍️ My AI Closet & Fitting Room
      </h1>

      <div className="flex flex-col lg:flex-row gap-6 w-full max-w-6xl h-auto lg:h-[800px]">
        {/* =========================================
            LEFT COLUMN: 옷장 (Closet Gallery) 
           ========================================= */}
        <div className="flex-1 bg-white rounded-2xl shadow-xl p-6 flex flex-col h-[500px] lg:h-full">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-700">👗 내 옷장</h2>
            <label
              className={`bg-gray-800 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-black transition text-sm flex items-center gap-2
              ${isUploadingCloth ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {isUploadingCloth ? (
                <span>업로드 중...</span>
              ) : (
                <>
                  <span>+ 새 옷 추가</span>
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={handleUploadCloth}
                    disabled={isUploadingCloth}
                  />
                </>
              )}
            </label>
          </div>

          {/* 옷 목록 그리드 */}
          <div className="flex-1 overflow-y-auto grid grid-cols-2 md:grid-cols-3 gap-4 content-start pr-2 scrollbar-thin scrollbar-thumb-gray-300">
            {clothes.length === 0 ? (
              <div className="col-span-full flex flex-col items-center justify-center text-gray-400 h-64">
                <p>옷장이 비었습니다.</p>
                <p className="text-sm">새 옷을 추가해보세요!</p>
              </div>
            ) : (
              clothes.map((url, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectedCloth(url)}
                  className={`aspect-[3/4] rounded-lg overflow-hidden cursor-pointer border-4 transition-all relative group bg-gray-50
                    ${
                      selectedCloth === url
                        ? "border-blue-500 shadow-lg scale-105 z-10"
                        : "border-transparent hover:border-gray-200"
                    }`}
                >
                  <img
                    src={url}
                    alt="Cloth"
                    className="w-full h-full object-cover"
                  />
                  {/* 선택 표시 오버레이 */}
                  {selectedCloth === url && (
                    <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center animate-fadeIn">
                      <div className="bg-blue-500 text-white rounded-full p-2 shadow-lg">
                        <svg
                          className="w-6 h-6"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="3"
                            d="M5 13l4 4L19 7"
                          ></path>
                        </svg>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* =========================================
            RIGHT COLUMN: 피팅룸 (Fitting Room) 
           ========================================= */}
        <div className="flex-1 bg-white rounded-2xl shadow-xl p-6 flex flex-col h-auto lg:h-full">
          <h2 className="text-2xl font-bold text-gray-700 mb-6">💃 피팅룸</h2>

          <div className="flex-1 flex flex-col gap-4 min-h-0">
            {/* 1. 내 사진 업로드 구역 */}
            <div className="flex-1 border-2 border-dashed border-gray-300 rounded-xl overflow-hidden relative group bg-gray-50 hover:bg-gray-100 transition min-h-[200px]">
              {myPhotoPreview ? (
                <img
                  src={myPhotoPreview}
                  className="w-full h-full object-contain"
                  alt="My Photo"
                />
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 pointer-events-none">
                  <span className="text-5xl mb-2">📸</span>
                  <p className="font-medium">내 전신 사진 올리기</p>
                  <p className="text-xs mt-1">클릭하여 업로드</p>
                </div>
              )}
              <input
                type="file"
                className="absolute inset-0 opacity-0 cursor-pointer"
                accept="image/*"
                onChange={handleMyPhotoChange}
              />

              {/* 사진 변경 버튼 (사진이 있을 때만 보임) */}
              {myPhotoPreview && (
                <div className="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded pointer-events-none">
                  클릭해서 변경
                </div>
              )}
            </div>

            {/* 화살표 아이콘 */}
            <div className="flex justify-center -my-2 z-10">
              <div className="bg-white rounded-full p-1 shadow-md text-gray-400">
                ⬇️
              </div>
            </div>

            {/* 2. 결과 이미지 구역 */}
            <div className="flex-1 bg-gray-900 rounded-xl overflow-hidden relative flex items-center justify-center min-h-[300px] border border-gray-800">
              {isFitting ? (
                <div className="text-center text-white z-10">
                  <div className="animate-spin rounded-full h-10 w-10 border-4 border-white border-t-transparent mx-auto mb-3"></div>
                  <p className="font-semibold text-lg">
                    AI가 옷을 입히는 중...
                  </p>
                  <p className="text-sm text-gray-400 mt-1">
                    잠시만 기다려주세요 (약 10초)
                  </p>
                </div>
              ) : resultImage ? (
                <div className="relative w-full h-full">
                  <img
                    src={resultImage}
                    className="w-full h-full object-contain"
                    alt="Result"
                  />
                  <a
                    href={resultImage}
                    download
                    className="absolute bottom-4 right-4 bg-white text-gray-900 px-4 py-2 rounded-lg font-bold shadow-lg hover:bg-gray-100 transition flex items-center gap-2"
                  >
                    <span>다운로드</span>
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                      ></path>
                    </svg>
                  </a>
                </div>
              ) : (
                <div className="text-gray-500 flex flex-col items-center">
                  <span className="text-4xl mb-2">✨</span>
                  <p>결과가 여기에 나타납니다</p>
                </div>
              )}
            </div>
          </div>

          {/* 3. 컨트롤 패널 (카테고리 & 버튼) */}
          <div className="mt-6 space-y-4">
            {/* 카테고리 선택 (2버튼) */}
            <div className="flex gap-2">
              <button
                onClick={() => setCategory("upper_body")}
                className={`flex-1 py-3 rounded-lg font-bold border-2 transition flex items-center justify-center gap-2
                  ${
                    category === "upper_body"
                      ? "bg-blue-50 border-blue-500 text-blue-700 shadow-sm"
                      : "bg-white border-gray-200 text-gray-400 hover:bg-gray-50 hover:text-gray-600"
                  }`}
              >
                <span>👕</span> 상의 (Upper)
              </button>
              <button
                onClick={() => setCategory("lower_body")}
                className={`flex-1 py-3 rounded-lg font-bold border-2 transition flex items-center justify-center gap-2
                  ${
                    category === "lower_body"
                      ? "bg-blue-50 border-blue-500 text-blue-700 shadow-sm"
                      : "bg-white border-gray-200 text-gray-400 hover:bg-gray-50 hover:text-gray-600"
                  }`}
              >
                <span>👖</span> 하의 (Lower)
              </button>
            </div>

            {/* 실행 버튼 */}
            <button
              onClick={handleTryOn}
              disabled={isFitting || !selectedCloth || !myPhoto}
              className={`w-full py-4 rounded-xl text-xl font-bold text-white shadow-lg transition-all transform active:scale-[0.98]
                ${
                  isFitting || !selectedCloth || !myPhoto
                    ? "bg-gray-300 cursor-not-allowed text-gray-500 shadow-none"
                    : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-blue-500/30"
                }`}
            >
              {isFitting ? "작업 중입니다..." : "✨ 이 옷으로 입어보기"}
            </button>

            {/* 도움말 메시지 */}
            {(!selectedCloth || !myPhoto) && (
              <p className="text-center text-xs text-red-400 font-medium animate-pulse">
                {!selectedCloth
                  ? "👈 왼쪽에서 옷을 먼저 선택해주세요."
                  : "👆 위에 본인 사진을 업로드해주세요."}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
