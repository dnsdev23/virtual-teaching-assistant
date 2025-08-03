// 檔案路徑: src/pages/AdminChapterPage.jsx
// 說明: 管理員章節管理頁面

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import FolderSelector from '../components/FolderSelector';

// API 函數
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

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'API 請求失敗');
    }
    if (response.status === 204) return null;
    return response.json();
};

const chapterAPI = {
    getAll: (includeInactive = false) => request(`/api/admin/chapters?include_inactive=${includeInactive}`),
    create: (chapter) => request('/api/admin/chapters', { method: 'POST', body: JSON.stringify(chapter) }),
    update: (id, chapter) => request(`/api/admin/chapters/${id}`, { method: 'PUT', body: JSON.stringify(chapter) }),
    delete: (id) => request(`/api/admin/chapters/${id}`, { method: 'DELETE' }),
    toggle: (id) => request(`/api/admin/chapters/${id}/toggle`, { method: 'PATCH' }),
    reindex: (id) => request(`/api/admin/chapters/${id}/reindex`, { method: 'POST' })
};

const AdminChapterPage = () => {
    const { user } = useAuth();
    const [chapters, setChapters] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingChapter, setEditingChapter] = useState(null);
    const [includeInactive, setIncludeInactive] = useState(false);
    const [toast, setToast] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        display_name: '',
        description: '',
        folder_path: ''
    });

    // 載入章節列表
    const loadChapters = async () => {
        try {
            setLoading(true);
            const data = await chapterAPI.getAll(includeInactive);
            setChapters(data);
        } catch (error) {
            setToast({ type: 'error', message: `載入章節失敗: ${error.message}` });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user?.role === 'admin') {
            loadChapters();
        }
    }, [user, includeInactive]);

    // 表單處理
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingChapter) {
                await chapterAPI.update(editingChapter.id, formData);
                setToast({ type: 'success', message: '章節更新成功' });
            } else {
                await chapterAPI.create(formData);
                setToast({ type: 'success', message: '章節創建成功' });
            }
            setShowModal(false);
            setEditingChapter(null);
            setFormData({ name: '', display_name: '', description: '', folder_path: '' });
            loadChapters();
        } catch (error) {
            setToast({ type: 'error', message: error.message });
        }
    };

    const handleEdit = (chapter) => {
        setEditingChapter(chapter);
        setFormData({
            name: chapter.name,
            display_name: chapter.display_name,
            description: chapter.description || '',
            folder_path: chapter.folder_path
        });
        setShowModal(true);
    };

    const handleDelete = async (chapter) => {
        if (window.confirm(`確定要刪除章節「${chapter.display_name}」嗎？`)) {
            try {
                await chapterAPI.delete(chapter.id);
                setToast({ type: 'success', message: '章節刪除成功' });
                loadChapters();
            } catch (error) {
                setToast({ type: 'error', message: error.message });
            }
        }
    };

    const handleToggle = async (chapter) => {
        try {
            await chapterAPI.toggle(chapter.id);
            setToast({ 
                type: 'success', 
                message: `章節已${chapter.is_active ? '停用' : '啟用'}` 
            });
            loadChapters();
        } catch (error) {
            setToast({ type: 'error', message: error.message });
        }
    };

    const handleReindex = async (chapter) => {
        if (window.confirm(`確定要重新索引章節「${chapter.display_name}」嗎？`)) {
            try {
                await chapterAPI.reindex(chapter.id);
                setToast({ type: 'success', message: '重新索引請求已提交' });
            } catch (error) {
                setToast({ type: 'error', message: error.message });
            }
        }
    };

    if (user?.role !== 'admin') {
        return (
            <div className="p-8 text-center">
                <p className="text-red-600">您沒有權限訪問此頁面</p>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">章節管理</h1>
                <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                        <input
                            type="checkbox"
                            checked={includeInactive}
                            onChange={(e) => setIncludeInactive(e.target.checked)}
                            className="mr-2"
                        />
                        <span className="text-sm text-gray-600">顯示停用章節</span>
                    </label>
                    <button
                        onClick={() => {
                            setEditingChapter(null);
                            setFormData({ name: '', display_name: '', description: '', folder_path: '' });
                            setShowModal(true);
                        }}
                        className="btn-primary"
                    >
                        新增章節
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <LoadingSpinner size="large" />
                </div>
            ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    章節名稱
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    顯示名稱
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    資料夾路徑
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    狀態
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    操作
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {chapters.map((chapter) => (
                                <tr key={chapter.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {chapter.name}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {chapter.display_name}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {chapter.folder_path}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                            chapter.is_active 
                                                ? 'bg-green-100 text-green-800' 
                                                : 'bg-red-100 text-red-800'
                                        }`}>
                                            {chapter.is_active ? '啟用' : '停用'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                                        <button
                                            onClick={() => handleEdit(chapter)}
                                            className="text-blue-600 hover:text-blue-900"
                                        >
                                            編輯
                                        </button>
                                        <button
                                            onClick={() => handleToggle(chapter)}
                                            className="text-yellow-600 hover:text-yellow-900"
                                        >
                                            {chapter.is_active ? '停用' : '啟用'}
                                        </button>
                                        <button
                                            onClick={() => handleReindex(chapter)}
                                            className="text-green-600 hover:text-green-900"
                                        >
                                            重新索引
                                        </button>
                                        <button
                                            onClick={() => handleDelete(chapter)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            刪除
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {chapters.length === 0 && (
                        <div className="text-center py-8 text-gray-500">
                            尚無章節資料
                        </div>
                    )}
                </div>
            )}

            {/* 新增/編輯模態框 */}
            <Modal
                isOpen={showModal}
                onClose={() => {
                    setShowModal(false);
                    setEditingChapter(null);
                }}
                title={editingChapter ? '編輯章節' : '新增章節'}
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            章節名稱 (英文)
                        </label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            className="input-field"
                            placeholder="例: chapter1"
                            required
                            disabled={editingChapter} // 編輯時不允許修改名稱
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            章節名稱用於文件夾和 API 識別，創建後不可修改
                        </p>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            顯示名稱
                        </label>
                        <input
                            type="text"
                            name="display_name"
                            value={formData.display_name}
                            onChange={handleInputChange}
                            className="input-field"
                            placeholder="例: 第一章：機器學習導論"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            資料夾路徑
                        </label>
                        <FolderSelector
                            value={formData.folder_path}
                            onChange={handleInputChange}
                            placeholder="例: materials/chapter1"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            描述 (選填)
                        </label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleInputChange}
                            className="input-field"
                            rows="3"
                            placeholder="章節內容描述..."
                        />
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={() => {
                                setShowModal(false);
                                setEditingChapter(null);
                            }}
                            className="btn-secondary"
                        >
                            取消
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                        >
                            {editingChapter ? '更新' : '創建'}
                        </button>
                    </div>
                </form>
            </Modal>

            {/* Toast 通知 */}
            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}
        </div>
    );
};

export default AdminChapterPage;
