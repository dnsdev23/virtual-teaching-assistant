// 檔案路徑: src/components/ProtectedRoute.jsx
// 說明: 一個保護路由的元件，如果使用者未登入，會被導向到登入頁。

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, adminOnly = false }) => {
    const { isAuthenticated, user, isLoading } = useAuth();
    const location = useLocation();

    console.log("🛡️ ProtectedRoute 檢查:", {
        isLoading,
        isAuthenticated,
        user: user?.email || "無使用者",
        currentPath: location.pathname
    });

    if (isLoading) {
        console.log("⏳ 認證狀態載入中...");
        return (
            <div className="flex justify-center items-center h-screen bg-gray-100">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">載入中...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        console.log("❌ 使用者未認證，導向登入頁面");
        return <Navigate to="/login" state={{ from: location }} replace />;
    }
    
    if (adminOnly && user?.role !== 'admin') {
        console.log("⛔ 非管理員使用者嘗試存取管理員頁面");
        return <Navigate to="/" replace />;
    }

    console.log("✅ 認證通過，顯示受保護內容");
    return children;
};

export default ProtectedRoute;
