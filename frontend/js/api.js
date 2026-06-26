/**
 * API 通信模块
 * 封装所有与后端 API 的交互
 */
const API = (() => {
    // 后端地址（开发环境）
    const BASE_URL = 'http://127.0.0.1:8000/api/v1';

    // Token 管理
    const TOKEN_KEY = 'auth_token';
    const USER_KEY  = 'auth_user';

    /**
     * 获取存储的 Token
     */
    function getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    /**
     * 保存 Token 和用户信息
     */
    function saveAuth(token, user) {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }

    /**
     * 获取存储的用户信息
     */
    function getUser() {
        const data = localStorage.getItem(USER_KEY);
        return data ? JSON.parse(data) : null;
    }

    /**
     * 清除认证信息
     */
    function clearAuth() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    }

    /**
     * 检查是否已登录
     */
    function isLoggedIn() {
        return !!getToken();
    }

    /**
     * 通用请求方法
     */
    async function request(method, path, body = null) {
        const url = `${BASE_URL}${path}`;
        const headers = { 'Content-Type': 'application/json' };

        const token = getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = { method, headers };
        if (body && method !== 'GET') {
            config.body = JSON.stringify(body);
        }

        const response = await fetch(url, config);
        const data = await response.json();

        if (!response.ok) {
            // 如果是401未授权错误，清除认证信息并跳转到登录页面
            if (response.status === 401) {
                clearAuth();
                window.location.href = 'index.html';
            }
            throw new Error(data.detail || data.message || '请求失败');
        }

        return data;
    }

    // ====================== 认证 API ======================

    return {
        /** 用户登录 */
        async login(username, password) {
            const res = await request('POST', '/auth/login', { username, password });
            if (res.code === 200 && res.data) {
                saveAuth(res.data.access_token, res.data.user);
            }
            return res;
        },

        /** 用户注册 */
        async register(username, password, email, phone) {
            const res = await request('POST', '/auth/register', {
                username, password, email, phone
            });
            return res;
        },

        /** 用户登出 */
        async logout() {
            try {
                await request('POST', '/auth/logout');
            } catch (e) { /* ignore */ }
            clearAuth();
        },

        /** 获取当前用户信息 */
        async getMe() {
            return await request('GET', '/auth/me');
        },

        /** 修改密码 */
        async changePassword(oldPassword, newPassword) {
            return await request('PUT', '/auth/password', {
                old_password: oldPassword,
                new_password: newPassword,
            });
        },

        // ====================== 用户管理 API ======================

        /** 获取用户列表 */
        async listUsers(page = 1, size = 20, status = null) {
            let path = `/users?page=${page}&size=${size}`;
            if (status !== null && status !== undefined) {
                path += `&status=${status}`;
            }
            return await request('GET', path);
        },

        /** 获取单个用户 */
        async getUser(userId) {
            return await request('GET', `/users/${userId}`);
        },

        /** 更新用户 */
        async updateUser(userId, data) {
            return await request('PUT', `/users/${userId}`, data);
        },

        /** 删除用户 */
        async deleteUser(userId) {
            return await request('DELETE', `/users/${userId}`);
        },

        // ====================== 作品 API ======================

        /** 创建作品 */
        async createNovel(data) {
            return await request('POST', '/novels/create', data);
        },

        /** 获取我的作品列表 */
        async listMyNovels() {
            return await request('GET', '/novels/');
        },

        /** 获取作品详情（编辑用） */
        async getNovelForEdit(novelUuid) {
            return await request('GET', `/novels/${novelUuid}/edit`);
        },

        /** 修改作品 */
        async updateNovel(novelUuid, data) {
            return await request('PUT', `/novels/${novelUuid}`, data);
        },

        /** 删除作品 */
        async deleteNovel(novelUuid) {
            return await request('DELETE', `/novels/${novelUuid}`);
        },

        // 工具方法
        getToken,
        getUser,
        clearAuth,
        isLoggedIn,
    };
})();
