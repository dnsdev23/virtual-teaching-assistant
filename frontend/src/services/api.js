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

// 獲取可用章節列表
export const getChapters = () => request('/api/chapters');

// 章節化問答
export const askQuestion = (question, chapter) => request(`/api/ask?chapter=${encodeURIComponent(chapter)}`, {
    method: 'POST',
    body: JSON.stringify({ question }),
});

// 章節化測驗生成
export const generateQuiz = (topic, numQuestions, chapter) => request(`/api/quiz/generate?chapter=${encodeURIComponent(chapter)}`, {
    method: 'POST',
    body: JSON.stringify({ 
        topic,
        num_questions: numQuestions 
    }),
});

// 提交測驗答案
export const submitQuiz = (attemptId, answers) => request(`/api/quiz/submit/${attemptId}`, {
    method: 'POST',
    body: JSON.stringify({ answers }),
});

// 獲取測驗歷史
export const getQuizHistory = () => request('/api/quiz/history');

// 獲取學習建議
export const getLearningRecommendations = () => request('/api/recommendations');

// Admin chapter management APIs
export const getAdminChapters = () => request('/api/admin/chapters');
export const createChapter = (chapterData) => request('/api/admin/chapters', {
    method: 'POST',
    body: JSON.stringify(chapterData),
});
export const updateChapter = (chapterId, chapterData) => request(`/api/admin/chapters/${chapterId}`, {
    method: 'PUT',
    body: JSON.stringify(chapterData),
});
export const deleteChapter = (chapterId) => request(`/api/admin/chapters/${chapterId}`, {
    method: 'DELETE',
});
export const reindexChapter = (chapterId) => request(`/api/admin/chapters/${chapterId}/reindex`, {
    method: 'POST',
});

// Admin analytics APIs
export const getAdminResources = () => request('/api/admin/resources');
export const addAdminResource = (resourceData) => request('/api/admin/resources', {
    method: 'POST',
    body: JSON.stringify(resourceData),
});
export const deleteAdminResource = (resourceId) => request(`/api/admin/resources/${resourceId}`, {
    method: 'DELETE',
});
export const getAdminQueryLogs = () => request('/api/admin/analytics/query-logs');
export const getAdminQuizAttempts = () => request('/api/admin/analytics/quiz-attempts');

// Admin folder management
export const getAvailableFolders = () => request('/api/admin/folders');
