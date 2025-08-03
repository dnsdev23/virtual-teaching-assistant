// 檔案路徑: src/components/Layout.jsx
// 說明: 應用程式的主要版面佈局，包含共用的頁首和側邊欄。

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Layout = ({ children }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100 font-sans">
            {/* Sidebar */}
            <aside className="w-64 bg-gray-800 text-white flex flex-col">
                <div className="p-4 border-b border-gray-700">
                    <h1 className="text-xl font-bold">虛擬助教</h1>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    <Link to="/" className="block px-4 py-2 rounded hover:bg-gray-700">聊天室</Link>
                    <Link to="/quiz" className="block px-4 py-2 rounded hover:bg-gray-700">隨堂測驗</Link>
                    <Link to="/history" className="block px-4 py-2 rounded hover:bg-gray-700">學習歷程</Link>
                    {user?.role === 'admin' && (
                        <>
                            <Link to="/admin" className="block px-4 py-2 rounded bg-yellow-500 text-black font-bold hover:bg-yellow-600">管理後台</Link>
                            <Link to="/admin/chapters" className="block px-4 py-2 rounded bg-purple-500 text-white font-bold hover:bg-purple-600">章節管理</Link>
                        </>
                    )}
                </nav>
                <div className="p-4 border-t border-gray-700">
                    <div className="flex items-center space-x-3">
                        {user?.picture ? (
                            <img src={user.picture} alt={user.name} className="w-10 h-10 rounded-full" />
                        ) : (
                            <div className="w-10 h-10 rounded-full bg-gray-600"></div>
                        )}
                        <div>
                            <p className="font-semibold">{user?.name}</p>
                            <p className="text-sm text-gray-400">{user?.email}</p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="w-full mt-4 px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700"
                    >
                        登出
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {children}
            </div>
        </div>
    );
};

export default Layout;
