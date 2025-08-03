import React, { useState, useEffect } from 'react';
import { getAvailableFolders } from '../services/api';

const FolderSelector = ({ value, onChange, placeholder = "選擇資料夾路徑" }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [folders, setFolders] = useState([]);
    const [loading, setLoading] = useState(false);

    // Common folder suggestions for materials
    const commonFolders = [
        'materials/chapter1',
        'materials/chapter2',
        'materials/chapter3',
        'materials/chapter4',
        'materials/chapter5',
        'materials/introduction',
        'materials/basics',
        'materials/intermediate', 
        'materials/advanced',
        'materials/exercises',
        'materials/projects',
        'materials/labs',
        'content/basics',
        'content/intermediate',
        'content/advanced',
        'data/legacy_chapter1',
        'data/legacy_chapter2'
    ];

    // Fetch available folders from backend (if endpoint exists)
    const fetchFolders = async () => {
        setLoading(true);
        try {
            const backendFolders = await getAvailableFolders();
            setFolders([...commonFolders, ...backendFolders]);
        } catch (error) {
            // Fallback to common folders if API fails
            console.log('Using fallback folders:', error.message);
            setFolders(commonFolders);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isOpen) {
            fetchFolders();
        }
    }, [isOpen]);

    const handleSelectFolder = (folderPath) => {
        onChange({ target: { name: 'folder_path', value: folderPath } });
        setIsOpen(false);
    };

    const handleManualInput = (e) => {
        onChange(e);
    };

    const createNewFolder = () => {
        const newPath = prompt('輸入新的資料夾路徑:', 'materials/new_chapter');
        if (newPath && newPath.trim()) {
            const cleanPath = newPath.trim().replace(/\\/g, '/');
            handleSelectFolder(cleanPath);
        }
    };

    // Filter folders based on current input
    const filteredFolders = folders.filter(folder => 
        folder.toLowerCase().includes(value.toLowerCase()) || 
        value === '' || 
        folder.startsWith(value)
    );

    return (
        <div className="relative">
            <div className="flex space-x-2">
                <input
                    type="text"
                    name="folder_path"
                    value={value}
                    onChange={handleManualInput}
                    onFocus={() => setIsOpen(true)}
                    className="input-field flex-1"
                    placeholder={placeholder}
                    required
                />
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    className="px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                    title="選擇資料夾"
                >
                    📁
                </button>
            </div>
            
            {isOpen && (
                <>
                    {/* Overlay to close dropdown when clicking outside */}
                    <div 
                        className="fixed inset-0 z-40" 
                        onClick={() => setIsOpen(false)}
                    ></div>
                    
                    <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        <div className="p-2 border-b border-gray-200">
                            <button
                                type="button"
                                onClick={createNewFolder}
                                className="w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors flex items-center space-x-2"
                            >
                                <span>➕</span>
                                <span>建立新資料夾...</span>
                            </button>
                        </div>
                        
                        <div className="p-1">
                            {loading ? (
                                <div className="px-3 py-2 text-sm text-gray-500 text-center">
                                    載入中...
                                </div>
                            ) : (
                                <>
                                    <div className="text-xs text-gray-500 px-3 py-1 font-medium">
                                        {value ? '符合的資料夾:' : '建議的資料夾:'}
                                    </div>
                                    {filteredFolders.length > 0 ? (
                                        filteredFolders.map((folder, index) => (
                                            <button
                                                key={index}
                                                type="button"
                                                onClick={() => handleSelectFolder(folder)}
                                                className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-50 rounded flex items-center space-x-2 transition-colors ${
                                                    value === folder ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                                                }`}
                                            >
                                                <span>📂</span>
                                                <span className="flex-1">{folder}</span>
                                                {value === folder && <span className="text-blue-500">✓</span>}
                                            </button>
                                        ))
                                    ) : (
                                        <div className="px-3 py-2 text-sm text-gray-500 text-center">
                                            沒有找到符合的資料夾
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </>
            )}
            
            <p className="text-xs text-gray-500 mt-1">
                系統會自動創建 materials 和 question_bank 子資料夾
            </p>
        </div>
    );
};

export default FolderSelector;
