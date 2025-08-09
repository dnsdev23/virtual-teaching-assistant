// 檔案路徑: src/pages/AdminDashboard.jsx
// 說明: (新增檔案) 管理員儀表板頁面。

import React, { useState, useEffect } from 'react';
import { getAdminResources, addAdminResource, deleteAdminResource, getAdminQueryLogs, getAdminQuizAttempts } from '../services/api';

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState('resources'); // resources, queries, quizzes

    const renderTabContent = () => {
        switch (activeTab) {
            case 'queries': return <QueryLogsTab />;
            case 'quizzes': return <QuizAttemptsTab />;
            case 'resources':
            default:
                return <ResourcesTab />;
        }
    };

    return (
        <div className="p-8 h-full flex flex-col">
            <h1 className="text-3xl font-bold mb-6">管理員儀表板</h1>
            <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8">
                    <button onClick={() => setActiveTab('resources')} className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'resources' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>外部資源</button>
                    <button onClick={() => setActiveTab('queries')} className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'queries' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>學生提問紀錄</button>
                    <button onClick={() => setActiveTab('quizzes')} className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'quizzes' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>測驗數據</button>
                </nav>
            </div>
            <div className="flex-1 overflow-y-auto">
                {renderTabContent()}
            </div>
        </div>
    );
};

// --- Sub-components for tabs ---

const ResourcesTab = () => {
    const [resources, setResources] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [formData, setFormData] = useState({ url: '', title: '', description: '', tags: '' });

    const fetchResources = () => {
        getAdminResources().then(setResources).finally(() => setIsLoading(false));
    };

    useEffect(fetchResources, []);

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        await addAdminResource(formData);
        setFormData({ url: '', title: '', description: '', tags: '' });
        fetchResources();
    };

    const handleDelete = async (id) => {
        if (window.confirm('確定要刪除這個資源嗎？')) {
            await deleteAdminResource(id);
            fetchResources();
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow mb-8 space-y-4">
                <h2 className="text-xl font-bold">新增資源</h2>
                <input name="title" value={formData.title} onChange={handleChange} placeholder="標題" className="w-full p-2 border rounded" required />
                <input name="url" value={formData.url} onChange={handleChange} placeholder="URL" className="w-full p-2 border rounded" required />
                <textarea name="description" value={formData.description} onChange={handleChange} placeholder="描述" className="w-full p-2 border rounded" />
                <input name="tags" value={formData.tags} onChange={handleChange} placeholder="標籤 (用逗號分隔)" className="w-full p-2 border rounded" required />
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">新增</button>
            </form>
            <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-bold mb-4">資源列表</h2>
                {isLoading ? <p>載入中...</p> : (
                    <ul className="space-y-2">
                        {resources.map(res => (
                            <li key={res.id} className="flex justify-between items-center p-2 hover:bg-gray-50">
                                <div>
                                    <a href={res.url} target="_blank" rel="noopener noreferrer" className="font-semibold text-blue-600">{res.title}</a>
                                    <p className="text-sm text-gray-500">{res.tags}</p>
                                </div>
                                <button onClick={() => handleDelete(res.id)} className="px-3 py-1 bg-red-500 text-white text-xs rounded">刪除</button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

const QueryLogsTab = () => {
    const [logs, setLogs] = useState([]);
    useEffect(() => { getAdminQueryLogs().then(setLogs); }, []);
    return (
        <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">學生提問紀錄</h2>
            <div className="space-y-4">
                {logs.map(log => (
                    <div key={log.id} className="p-3 border-b">
                        <p className="text-sm text-gray-500">{log.user.email} 在 {new Date(log.created_at).toLocaleString()} 問：</p>
                        <p className="font-semibold mt-1">{log.question}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

const QuizAttemptsTab = () => {
    const [attempts, setAttempts] = useState([]);
    useEffect(() => { getAdminQuizAttempts().then(setAttempts); }, []);
    return (
        <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">測驗數據</h2>
            <div className="space-y-4">
                {attempts.map(att => (
                    <div key={att.id} className="p-3 border-b flex justify-between">
                        <div>
                            <p className="font-semibold">{att.user.email}</p>
                            <p className="text-sm text-gray-600">{att.topic}</p>
                        </div>
                        <p className={`font-bold text-lg ${att.score >= 60 ? 'text-green-600' : 'text-red-600'}`}>{att.score.toFixed(1)}%</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AdminDashboard;
