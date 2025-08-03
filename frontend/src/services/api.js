// 檔案路徑: src/services/api.js
// 說明: 集中管理所有對後端 API 的請求。

const API_BASE_URL = "http://127.0.0.1:8000";

const request = async (endpoint, options = {}) => {
    const token = localStorage.getItem('authToken');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        if (!response.ok) {
            // 如果 token 失效 (401)，自動登出
            if (response.status === 401) {
                localStorage.removeItem('authToken');
                // 不直接重新導向，讓呼叫端處理
                throw new Error('未授權：請重新登入');
            }
            let errorMessage = 'API 請求失敗';
            try {
                const error = await response.json();
                errorMessage = error.detail || errorMessage;
            } catch {
                // 如果無法解析錯誤 JSON，使用預設訊息
            }
            throw new Error(errorMessage);
        }
        // 對於不需要回傳內容的請求 (如 DELETE)
        if (response.status === 204) {
            return null;
        }
        return response.json();
    } catch (error) {
        console.error(`API 錯誤 ${endpoint}:`, error);
        throw error;
    }
};

// --- API 函式 ---
export const getUserProfile = () => request('/api/users/me');
export const askQuestion = (question) => request('/api/ask', {
    method: 'POST',
    body: JSON.stringify({ question }),
});

// 之後可以陸續加入更多 API 呼叫...
// export const generateQuiz = (topic) => ...
// export const getQuizHistory = () => ...
