// 檔案路徑: src/App.jsx
// 說明: 應用程式的主路由器，設定所有頁面的路徑。

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Pages
import LoginPage from './pages/LoginPage';
import CallbackPage from './pages/CallbackPage';
import ChatPage from './pages/ChatPage';
import AdminChapterPage from './pages/AdminChapterPage';

// Placeholder Pages
const QuizPage = () => <div className="p-8"><h1>隨堂測驗</h1><p>此功能正在開發中...</p></div>;
const HistoryPage = () => <div className="p-8"><h1>學習歷程</h1><p>此功能正在開發中...</p></div>;
const AdminDashboard = () => <div className="p-8"><h1>管理後台</h1><p>此功能正在開發中...</p></div>;

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/auth/callback" element={<CallbackPage />} />
                    
                    {/* Protected Routes */}
                    <Route 
                        path="/" 
                        element={
                            <ProtectedRoute>
                                <Layout>
                                    <ChatPage />
                                </Layout>
                            </ProtectedRoute>
                        } 
                    />
                    <Route 
                        path="/quiz" 
                        element={
                            <ProtectedRoute>
                                <Layout>
                                    <QuizPage />
                                </Layout>
                            </ProtectedRoute>
                        } 
                    />
                     <Route 
                        path="/history" 
                        element={
                            <ProtectedRoute>
                                <Layout>
                                    <HistoryPage />
                                </Layout>
                            </ProtectedRoute>
                        } 
                    />
                    <Route 
                        path="/admin" 
                        element={
                            <ProtectedRoute adminOnly={true}>
                                <Layout>
                                    <AdminDashboard />
                                </Layout>
                            </ProtectedRoute>
                        } 
                    />
                    <Route 
                        path="/admin/chapters" 
                        element={
                            <ProtectedRoute adminOnly={true}>
                                <Layout>
                                    <AdminChapterPage />
                                </Layout>
                            </ProtectedRoute>
                        } 
                    />

                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
