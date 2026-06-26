/**
 * Auth System - 前端应用逻辑
 * 处理登录/注册表单、仪表盘交互、用户管理等
 */

// ====================== 工具函数 ======================

/** 显示 Toast 消息 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/** 格式化日期 */
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// ====================== 登录页面逻辑 ======================

(function initLoginPage() {
    const loginForm    = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (!loginForm && !registerForm) return;  // 不在登录页

    const loginCard = document.getElementById('loginCard');
    const registerCard = document.getElementById('registerCard');

    // 切换登录/注册卡片
    document.getElementById('goRegister').addEventListener('click', (e) => {
        e.preventDefault();
        loginCard.classList.add('hidden');
        registerCard.classList.remove('hidden');
    });
    document.getElementById('goLogin').addEventListener('click', (e) => {
        e.preventDefault();
        registerCard.classList.add('hidden');
        loginCard.classList.remove('hidden');
    });

    // 登录表单提交
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btnText = document.getElementById('loginBtnText');
        const spinner = document.getElementById('loginSpinner');
        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        try {
            const res = await API.login(username, password);
            if (res.code === 200) {
                showToast('登录成功，正在跳转...', 'success');
                setTimeout(() => { window.location.href = 'dashboard.html'; }, 800);
            } else {
                showToast(res.message || '登录失败', 'error');
            }
        } catch (err) {
            showToast(err.message || '网络错误，请检查后端服务', 'error');
        } finally {
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    });

    // 注册表单提交
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btnText = document.getElementById('registerBtnText');
        const spinner = document.getElementById('registerSpinner');

        const username = document.getElementById('regUsername').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirm  = document.getElementById('regPasswordConfirm').value;
        const email    = document.getElementById('regEmail').value.trim() || undefined;
        const phone    = document.getElementById('regPhone').value.trim() || undefined;

        if (password !== confirm) {
            showToast('两次输入的密码不一致', 'error');
            return;
        }

        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');

        try {
            const res = await API.register(username, password, email, phone);
            if (res.code === 201) {
                showToast('注册成功！请登录', 'success');
                registerCard.classList.add('hidden');
                loginCard.classList.remove('hidden');
                document.getElementById('username').value = username;
            } else {
                showToast(res.message || '注册失败', 'error');
            }
        } catch (err) {
            showToast(err.message || '网络错误', 'error');
        } finally {
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    });

    // 忘记密码
    document.getElementById('forgotPassword').addEventListener('click', (e) => {
        e.preventDefault();
        showToast('请联系管理员重置密码', 'warning');
    });
})();

// ====================== 仪表盘页面逻辑 ======================

(function initDashboard() {
    const btnLogout = document.getElementById('btnLogout');
    if (!btnLogout) return;  // 不在仪表盘页

    // 检查登录状态
    if (!API.isLoggedIn()) {
        window.location.href = 'index.html';
        return;
    }

    // 当前页面状态
    let currentPage = 'dashboard';
    let usersPage = 1;
    let usersTotal = 0;
    let allUsers = [];    // 用于仪表盘统计
    let currentUser = API.getUser();

    // 初始化用户信息
    function initUserInfo() {
        if (currentUser) {
            document.getElementById('displayName').textContent = currentUser.username;
            document.getElementById('displayRole').textContent = currentUser.superuser ? '超级管理员' : '普通用户';
            document.getElementById('avatarInitial').textContent = currentUser.username.charAt(0).toUpperCase();
        }
    }

    // 退出登录
    btnLogout.addEventListener('click', async () => {
        await API.logout();
        window.location.href = 'index.html';
    });

    // 页面切换
    window.switchPage = function(page) {
        currentPage = page;

        // 更新导航激活状态
        document.querySelectorAll('.sidebar-nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.page === page);
        });

        // 显示/隐藏页面
        document.querySelectorAll('[id^="page-"]').forEach(sec => sec.classList.add('hidden'));
        document.getElementById(`page-${page}`).classList.remove('hidden');

        // 加载对应数据
        if (page === 'dashboard') loadDashboard();
        if (page === 'users') loadUsers(1);
    };

    // ==================== 仪表盘 ====================

    async function loadDashboard() {
        try {
            // 获取全部用户用于统计
            const res = await API.listUsers(1, 1000);
            if (res.code === 200 && res.data) {
                allUsers = res.data.items || [];
                updateStats(allUsers);
                renderRecentUsers(allUsers.slice(0, 5));
            }
        } catch (err) {
            showToast('加载仪表盘数据失败', 'error');
        }
    }

    function updateStats(users) {
        const total    = users.length;
        const active   = users.filter(u => u.status === 1).length;
        const admin    = users.filter(u => u.superuser === 1).length;
        const disabled = users.filter(u => u.status === 0).length;

        document.getElementById('statTotal').textContent = total;
        document.getElementById('statActive').textContent = active;
        document.getElementById('statAdmin').textContent = admin;
        document.getElementById('statDisabled').textContent = disabled;
    }

    function renderRecentUsers(users) {
        const tbody = document.getElementById('recentUsersTable');
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>暂无用户数据</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = users.map(u => `
            <tr>
                <td><strong>#${u.id}</strong></td>
                <td>${escapeHtml(u.username)}</td>
                <td>${u.email || '-'}</td>
                <td>${u.superuser ? '<span class="role-badge admin">管理员</span>' : '<span class="role-badge user">普通用户</span>'}</td>
                <td>${u.status === 1
                    ? '<span class="status-badge active"><span class="status-dot active"></span>正常</span>'
                    : '<span class="status-badge disabled"><span class="status-dot disabled"></span>禁用</span>'}</td>
                <td>${formatDate(u.created_at)}</td>
            </tr>
        `).join('');
    }

    // ==================== 用户管理 ====================

    window.loadUsers = async function(page = usersPage) {
        const searchTerm  = (document.getElementById('searchUser')?.value || '').trim().toLowerCase();
        const statusFilter = document.getElementById('filterStatus')?.value;
        const status = statusFilter === '' ? null : parseInt(statusFilter);

        try {
            // 一次性获取大量数据用于前端搜索
            const res = await API.listUsers(1, 1000, status);
            if (res.code === 200 && res.data) {
                allUsers = res.data.items || [];

                // 前端搜索过滤
                let filtered = allUsers;
                if (searchTerm) {
                    filtered = allUsers.filter(u =>
                        u.username.toLowerCase().includes(searchTerm) ||
                        (u.email && u.email.toLowerCase().includes(searchTerm))
                    );
                }

                const pageSize = 20;
                usersTotal = filtered.length;
                const totalPages = Math.ceil(usersTotal / pageSize);
                const start = (page - 1) * pageSize;
                const pageUsers = filtered.slice(start, start + pageSize);

                renderUsersTable(pageUsers);
                renderPagination(page, totalPages);
            }
        } catch (err) {
            showToast('加载用户列表失败', 'error');
        }
    };

    function renderUsersTable(users) {
        const tbody = document.getElementById('usersTable');
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                <p>暂无用户数据</p>
            </div></td></tr>`;
            return;
        }
        tbody.innerHTML = users.map(u => `
            <tr>
                <td><strong>#${u.id}</strong></td>
                <td>${escapeHtml(u.username)}</td>
                <td>${u.email || '-'}</td>
                <td>${u.phone || '-'}</td>
                <td>${u.superuser ? '<span class="role-badge admin">管理员</span>' : '<span class="role-badge user">普通用户</span>'}</td>
                <td>${u.status === 1
                    ? '<span class="status-badge active"><span class="status-dot active"></span>正常</span>'
                    : '<span class="status-badge disabled"><span class="status-dot disabled"></span>禁用</span>'}</td>
                <td>${formatDate(u.created_at)}</td>
                <td>
                    <div class="action-btns">
                        <button class="btn-icon edit" title="编辑" onclick="editUser(${u.id})">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                        </button>
                        <button class="btn-icon delete" title="删除" onclick="deleteUser(${u.id}, '${escapeHtml(u.username)}')">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    function renderPagination(currentPage, totalPages) {
        document.getElementById('paginationInfo').textContent = `共 ${usersTotal} 条记录`;
        const container = document.getElementById('paginationBtns');

        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '';
        html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="loadUsers(${currentPage - 1})">◀</button>`;

        const maxButtons = 7;
        let start, end;
        if (totalPages <= maxButtons) {
            start = 1; end = totalPages;
        } else {
            const half = Math.floor(maxButtons / 2);
            if (currentPage <= half + 1) {
                start = 1; end = maxButtons;
            } else if (currentPage >= totalPages - half) {
                start = totalPages - maxButtons + 1; end = totalPages;
            } else {
                start = currentPage - half; end = currentPage + half;
            }
        }

        for (let i = start; i <= end; i++) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadUsers(${i})">${i}</button>`;
        }

        html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="loadUsers(${currentPage + 1})">▶</button>`;
        container.innerHTML = html;
    }

    // 编辑用户
    window.editUser = async function(userId) {
        try {
            const res = await API.getUser(userId);
            if (res.code === 200 && res.data) {
                showEditModal(res.data);
            }
        } catch (err) {
            showToast('获取用户信息失败', 'error');
        }
    };

    function showEditModal(user) {
        const isMe = currentUser && currentUser.id === user.id;

        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>编辑用户 #${user.id}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>用户名</label>
                        <input type="text" value="${escapeHtml(user.username)}" disabled style="padding-left:16px; background:#F7FAFC;">
                    </div>
                    <div class="form-group">
                        <label>邮箱</label>
                        <input type="email" id="editEmail" value="${user.email || ''}" style="padding-left:16px;">
                    </div>
                    <div class="form-group">
                        <label>手机号</label>
                        <input type="text" id="editPhone" value="${user.phone || ''}" style="padding-left:16px;">
                    </div>
                    <div class="form-group">
                        <label>状态</label>
                        <select id="editStatus" style="padding-left:16px; width:100%; height:48px; border:2px solid var(--border); border-radius:var(--radius-md); font-size:0.95rem;">
                            <option value="1" ${user.status === 1 ? 'selected' : ''}>正常</option>
                            <option value="0" ${user.status === 0 ? 'selected' : ''}>禁用</option>
                        </select>
                    </div>
                    ${currentUser && currentUser.superuser && !isMe ? `
                    <div class="form-group">
                        <label>角色</label>
                        <select id="editSuperuser" style="padding-left:16px; width:100%; height:48px; border:2px solid var(--border); border-radius:var(--radius-md); font-size:0.95rem;">
                            <option value="0" ${user.superuser === 0 ? 'selected' : ''}>普通用户</option>
                            <option value="1" ${user.superuser === 1 ? 'selected' : ''}>超级管理员</option>
                        </select>
                    </div>` : ''}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline btn-sm" onclick="this.closest('.modal-overlay').remove()">取消</button>
                    <button class="btn btn-primary btn-sm" id="btnSaveEdit">保存</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // 点击蒙层关闭
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });

        // 保存编辑
        overlay.querySelector('#btnSaveEdit').addEventListener('click', async () => {
            const data = {
                email: document.getElementById('editEmail').value.trim() || null,
                phone: document.getElementById('editPhone').value.trim() || null,
                status: parseInt(document.getElementById('editStatus').value),
            };
            if (!isMe && document.getElementById('editSuperuser')) {
                data.superuser = parseInt(document.getElementById('editSuperuser').value);
            }

            try {
                const res = await API.updateUser(user.id, data);
                if (res.code === 200) {
                    showToast('更新成功', 'success');
                    overlay.remove();
                    loadUsers();
                    if (isMe) {
                        // 更新本地缓存
                        const meRes = await API.getMe();
                        if (meRes.code === 200) {
                            localStorage.setItem('auth_user', JSON.stringify(meRes.data));
                            currentUser = meRes.data;
                            initUserInfo();
                        }
                    }
                } else {
                    showToast(res.message || '更新失败', 'error');
                }
            } catch (err) {
                showToast(err.message || '更新失败', 'error');
            }
        });
    }

    // 删除用户
    window.deleteUser = async function(userId, username) {
        if (!confirm(`确定要删除用户 "${username}" (ID: ${userId}) 吗？此操作不可撤销！`)) {
            return;
        }
        try {
            const res = await API.deleteUser(userId);
            if (res.code === 200) {
                showToast('删除成功', 'success');
                loadUsers();
            } else {
                showToast(res.message || '删除失败', 'error');
            }
        } catch (err) {
            showToast(err.message || '删除失败', 'error');
        }
    };

    // 修改密码表单
    document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const oldPwd = document.getElementById('oldPwd').value;
        const newPwd = document.getElementById('newPwd').value;
        const confirmPwd = document.getElementById('confirmPwd').value;

        if (newPwd !== confirmPwd) {
            showToast('两次输入的新密码不一致', 'error');
            return;
        }

        try {
            const res = await API.changePassword(oldPwd, newPwd);
            if (res.code === 200) {
                showToast('密码修改成功', 'success');
                document.getElementById('changePasswordForm').reset();
            } else {
                showToast(res.message || '密码修改失败', 'error');
            }
        } catch (err) {
            showToast(err.message || '密码修改失败', 'error');
        }
    });

    /** HTML 转义 */
    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // 初始化
    initUserInfo();
    loadDashboard();

})();
