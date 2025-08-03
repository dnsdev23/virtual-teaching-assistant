// 檔案路徑: src/contexts/AuthContext.jsx
// 說明: 使用 React Context 來全域管理使用者登入狀態。

import React, { createContext, useState, useEffect, useContext } from 'react';
import { getUserProfile } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (token) {
            getUserProfile()
                .then(userData => {
                    setUser(userData);
                })
                .catch(() => {
                    // Token 無效或過期
                    localStorage.removeItem('authToken');
                    setUser(null);
                })
                .finally(() => {
                    setIsLoading(false);
                });
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = (token, userData) => {
        console.log("🔐 AuthContext.login 被呼叫");
        console.log("Token:", token ? "存在" : "不存在");
        console.log("UserData:", userData);
        
        localStorage.setItem('authToken', token);
        setUser(userData);
        
        console.log("✅ 使用者狀態已更新，isAuthenticated:", !!userData);
    };

    const logout = () => {
        localStorage.removeItem('authToken');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
