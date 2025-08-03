// 檔案路徑: src/pages/CallbackPage.jsx
// 說明: 處理 Google 登入後的回調，取得 token 並導向主頁。

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getUserProfile } from '../services/api';

const CallbackPage = () => {
    const navigate = useNavigate();
    const { login } = useAuth();

    useEffect(() => {
        const handleAuth = async () => {
            try {
                console.log("🔄 開始處理 OAuth 回調...");
                console.log("當前 URL:", window.location.href);
                
                const urlParams = new URLSearchParams(window.location.search);
                const token = urlParams.get('token');
                
                console.log("📥 取得的 token:", token ? `存在 (${token.substring(0, 20)}...)` : "❌ 不存在");
                
                if (token) {
                    console.log("💾 儲存 token 到 localStorage...");
                    localStorage.setItem('authToken', token);
                    
                    console.log("👤 呼叫 getUserProfile API...");
                    const userData = await getUserProfile();
                    console.log("✅ 取得使用者資料:", userData);
                    
                    console.log("🔐 更新認證狀態...");
                    login(token, userData);
                    
                    console.log("🏠 準備導向到首頁...");
                    
                    // 確保狀態更新後再導向
                    setTimeout(() => {
                        console.log("➡️ 執行導向...");
                        navigate('/', { replace: true });
                    }, 100);
                } else {
                    console.error("❌ 在 URL 中未找到 token 參數");
                    throw new Error("在回調中未找到 token");
                }
            } catch (error) {
                console.error("💥 處理回調時發生錯誤:", error);
                console.error("錯誤詳細資訊:", error.message);
                
                // 清除可能的無效 token
                localStorage.removeItem('authToken');
                
                // 延遲後導向到登入頁面
                setTimeout(() => {
                    console.log("🔄 導向到登入頁面...");
                    navigate('/login', { replace: true });
                }, 1000);
            }
        };

        // 確保頁面完全載入後執行
        const timer = setTimeout(handleAuth, 200);
        return () => clearTimeout(timer);
    }, [navigate, login]);

    return (
        <div className="flex justify-center items-center h-screen bg-gray-100">
            <div className="text-center p-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600 text-lg mb-2">正在驗證您的身分</p>
                <p className="text-gray-500 text-sm">請稍候，即將進入系統...</p>
            </div>
        </div>
    );
};

export default CallbackPage;
