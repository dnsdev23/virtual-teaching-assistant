// 檔案路徑: src/pages/LoginPage.jsx
// 說明: 登入頁面。

import React from 'react';

const LoginPage = () => {
    const API_BASE_URL = "http://127.0.0.1:8000";

    const handleLogin = () => {
        window.location.href = `${API_BASE_URL}/auth/login`;
    };

    return (
        <div className="flex items-center justify-center h-screen bg-gray-100">
            <div className="text-center p-8 bg-white rounded-lg shadow-xl max-w-sm w-full">
                <h1 className="text-3xl font-bold text-gray-800 mb-4">虛擬課程助教</h1>
                <p className="text-gray-600 mb-8">請登入以開始與您的 AI 助教互動。</p>
                <button
                    onClick={handleLogin}
                    className="w-full px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 transition duration-300 flex items-center justify-center"
                >
                    <svg className="w-6 h-6 mr-2" viewBox="0 0 48 48">
                        <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"></path>
                        <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"></path>
                        <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"></path>
                        <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.574l6.19,5.238C39.912,35.622,44,28.718,44,20C44,22.659,43.862,21.35,43.611,20.083z"></path>
                    </svg>
                    使用 Google 登入
                </button>
            </div>
        </div>
    );
};

export default LoginPage;
