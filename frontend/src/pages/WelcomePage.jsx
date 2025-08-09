// 檔案路徑: src/pages/WelcomePage.jsx
// 說明: 一個簡單的歡迎頁面，引導使用者從側邊欄選擇章節。

import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const WelcomePage = () => {
    const { user } = useAuth();

    return (
        <div className="flex-1 flex items-center justify-center bg-gray-50 p-8">
            <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-800 mb-4">
                    歡迎回來，{user?.name}！
                </h1>
                <p className="text-lg text-gray-600">
                    請從左側的側邊欄選擇一個課程章節來開始學習或提問。
                </p>
            </div>
        </div>
    );
};

export default WelcomePage;
