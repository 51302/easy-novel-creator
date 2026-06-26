/**
 * 创作页面 - 交互逻辑
 * 处理Tab切换、角色管理、标签管理、章节编辑等
 */

// ====================== Tab 切换 ======================

function switchCreateTab(tabName) {
    document.querySelectorAll('.create-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    document.querySelectorAll('.create-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`panel-${tabName}`).classList.add('active');

    // 切换到章节更新Tab时刷新作品列表
    if (tabName === 'chapter-update') {
        renderChapterWorkList();
    }
}

// ====================== 角色管理 ======================

function addCharacter() {
    const list = document.getElementById('characterList');
    const rows = list.querySelectorAll('.character-row');
    rows.forEach(row => {
        row.querySelector('.btn-char-remove').classList.remove('hidden');
    });

    const newRow = document.createElement('div');
    newRow.className = 'character-row';
    newRow.innerHTML = `
        <input type="text" class="char-name" placeholder="角色名称" maxlength="30">
        <input type="text" class="char-desc" placeholder="角色描述（身份、性格、特征等）" maxlength="200">
        <input type="text" class="char-relation" placeholder="与其他角色的关系" maxlength="200">
        <button type="button" class="btn-char-remove" onclick="removeCharacter(this)" title="移除">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
    `;
    list.appendChild(newRow);
    newRow.querySelector('.char-name').focus();
}

function removeCharacter(btn) {
    const list = document.getElementById('characterList');
    const rows = list.querySelectorAll('.character-row');
    if (rows.length <= 1) {
        const row = rows[0];
        row.querySelector('.char-name').value = '';
        row.querySelector('.char-desc').value = '';
        row.querySelector('.char-relation').value = '';
        btn.classList.add('hidden');
        return;
    }
    btn.closest('.character-row').remove();
    const remainingRows = list.querySelectorAll('.character-row');
    if (remainingRows.length === 1) {
        remainingRows[0].querySelector('.btn-char-remove').classList.add('hidden');
    }
}

// ====================== 标签管理 ======================

const MAX_TAGS = 10;
let currentTags = [];

function addTag(tagText) {
    tagText = tagText.trim();
    if (!tagText) return;
    if (currentTags.length >= MAX_TAGS) { showToast(`最多添加 ${MAX_TAGS} 个标签`, 'warning'); return; }
    if (currentTags.includes(tagText)) { showToast('标签已存在', 'warning'); return; }
    currentTags.push(tagText);
    renderTags();
}

function removeTag(tagText) {
    currentTags = currentTags.filter(t => t !== tagText);
    renderTags();
}

function addSuggestedTag(btn) { addTag(btn.textContent); }

function renderTags() {
    const container = document.getElementById('tagContainer');
    container.innerHTML = '';
    currentTags.forEach(tag => {
        const el = document.createElement('span');
        el.className = 'tag-item';
        el.innerHTML = `${escapeHtml(tag)}<button type="button" class="tag-remove" onclick="removeTag('${escapeHtml(tag)}')" title="移除">&times;</button>`;
        container.appendChild(el);
    });
}

// ====================== 表单逻辑 ======================

document.addEventListener('DOMContentLoaded', () => {
    // 标签输入
    const tagInput = document.getElementById('tagInput');
    const tagWrapper = tagInput?.closest('.tag-input-wrapper');
    if (tagWrapper) {
        tagWrapper.addEventListener('click', () => tagInput.focus());
        tagInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); addTag(tagInput.value); tagInput.value = ''; }
            if (e.key === 'Backspace' && !tagInput.value && currentTags.length > 0) { removeTag(currentTags[currentTags.length - 1]); }
        });
    }

    // 字数统计
    const workName = document.getElementById('workName');
    const workSynopsis = document.getElementById('workSynopsis');
    if (workName) workName.addEventListener('input', () => { workName.nextElementSibling.textContent = `${workName.value.length}/100`; });
    if (workSynopsis) workSynopsis.addEventListener('input', () => { workSynopsis.nextElementSibling.textContent = `${workSynopsis.value.length}/2000`; });

    // 新建作品表单 - 调用后端 API
    const newWorkForm = document.getElementById('newWorkForm');
    if (newWorkForm) {
        newWorkForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const nameVal = document.getElementById('workName').value.trim();
            const synopsisVal = document.getElementById('workSynopsis').value.trim();
            if (!nameVal) { showToast('请输入作品名称', 'warning'); document.getElementById('workName').focus(); return; }
            if (!synopsisVal) { showToast('请输入作品简介', 'warning'); document.getElementById('workSynopsis').focus(); return; }

            // 收集角色数据
            const characters = [];
            document.querySelectorAll('.character-row').forEach(row => {
                const n = row.querySelector('.char-name').value.trim();
                const d = row.querySelector('.char-desc').value.trim();
                if (n) characters.push({ name: n, description: d });
            });

            // 构建请求数据
            const payload = {
                title: nameVal,
                synopsis: synopsisVal,
                novel_type: document.getElementById('targetReaders').value || null,
                tags: [...currentTags],
                story_background: document.getElementById('storyBackground').value.trim() || null,
                world_building: document.getElementById('worldBuilding').value.trim() || null,
                characters: characters,
            };

            const btn = document.getElementById('createWorkBtn');
            const btnText = document.getElementById('createWorkBtnText');
            const spinner = document.getElementById('createWorkSpinner');
            btn.disabled = true; btnText.textContent = '创建中...'; spinner.classList.remove('hidden');

            try {
                const res = await API.createNovel(payload);
                if (res.code === 201) {
                    showToast('作品创建成功！', 'success');
                    // 将后端返回的作品加入本地列表
                    addWorkToChapterList({
                        id: res.data.id,
                        name: res.data.title,
                        novel_uuid: res.data.novel_uuid,
                        tags: payload.tags,
                        createdAt: res.data.created_at,
                        chapters: []
                    });
                    resetCreateForm();
                    switchCreateTab('chapter-update');
                } else {
                    showToast(res.message || '创建失败', 'warning');
                }
            } catch (err) {
                showToast('创建失败: ' + (err.message || '网络错误'), 'error');
                console.error(err);
            } finally {
                btn.disabled = false; btnText.textContent = '创建作品'; spinner.classList.add('hidden');
            }
        });
    }

    // 作品搜索
    const searchInput = document.getElementById('chapterSearchInput');
    if (searchInput) searchInput.addEventListener('input', () => renderChapterWorkList(searchInput.value));
});

// ====================== 章节更新 ======================

let createdWorks = [];

function addWorkToChapterList(work) {
    createdWorks.push({
        id: work.id || Date.now(),
        novel_uuid: work.novel_uuid || '',
        name: work.name || work.title,
        tags: work.tags || [],
        createdAt: work.createdAt || new Date().toLocaleString('zh-CN'),
        chapters: []
    });
    renderChapterWorkList();
}

function renderChapterWorkList(filter = '') {
    const listEl = document.getElementById('chapterWorkList');
    let filtered = filter ? createdWorks.filter(w => w.name.toLowerCase().includes(filter.toLowerCase())) : createdWorks;
    if (filtered.length === 0) {
        listEl.innerHTML = `<div class="chapter-empty-works">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
            <p>${filter ? '未找到匹配作品' : '暂无作品'}</p>
            <span>${filter ? '请尝试其他关键词' : '请先在「新建作品」中创建作品'}</span>
            ${!filter ? '<button type="button" class="btn btn-sm btn-primary" style="margin-top:16px;" onclick="switchCreateTab('new-work')">去新建作品</button>' : ''}
        </div>`;
        return;
    }
    listEl.innerHTML = filtered.map(w => `<div class="chapter-work-item" onclick="selectWork(${w.id})"><div class="chapter-work-item-name">${escapeHtml(w.name)}</div><div class="chapter-work-item-meta"><span>${w.chapters.length} 个章节</span>${w.tags.length ? `<span>${w.tags.slice(0,3).join(' / ')}</span>` : ''}</div></div>`).join('');
}

function selectWork(workId) {
    const work = createdWorks.find(w => w.id === workId);
    if (!work) return;
    document.querySelectorAll('.chapter-work-item').forEach(i => i.classList.remove('active'));
    event.currentTarget.classList.add('active');
    document.getElementById('chapterEditorPlaceholder').classList.add('hidden');
    document.getElementById('chapterEditorContent').classList.remove('hidden');
    document.getElementById('editingWorkName').textContent = work.name;
    document.getElementById('chapterCount').textContent = `${work.chapters.length} 个章节`;
    renderChapterList(work);
}

function renderChapterList(work) {
    const area = document.getElementById('chapterListArea');
    if (!work.chapters.length) {
        area.innerHTML = `<div class="chapter-empty-works" style="padding:40px"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:48px;height:48px;margin-bottom:12px;opacity:0.3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg><p>暂无章节</p><span>点击右上角「新建章节」开始创作</span></div>`;
        return;
    }
    area.innerHTML = work.chapters.map((ch, idx) => buildChapterCard(work, ch, idx)).join('');
}

function buildChapterCard(work, ch, idx) {
    const isExpanded = ch._expanded || false;
    return `<div class="chapter-card ${isExpanded ? 'expanded' : ''}" data-chapter-id="${ch.id}">
        <div class="chapter-card-header" onclick="toggleChapterCard(${ch.id})">
            <div class="chapter-card-left">
                <span class="chapter-number">${idx+1}</span>
                <div class="chapter-card-info">
                    <span class="chapter-card-title">${escapeHtml(ch.title || '未命名章节')}</span>
                    <span class="chapter-card-meta">${ch.event ? escapeHtml(ch.event.substring(0,30)) + '...' : '暂无事件描述'}</span>
                </div>
            </div>
            <div class="chapter-card-right">
                <span class="chapter-card-status ${ch._saved ? 'saved' : 'unsaved'}">${ch._saved ? '已保存' : '未保存'}</span>
                <button type="button" class="chapter-card-toggle" title="${isExpanded ? '收起' : '展开'}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="${isExpanded ? '18 15 12 9 6 15' : '6 9 12 15 18 9'}"></polyline></svg>
                </button>
                <button type="button" class="btn-icon delete chapter-card-delete" title="删除章节" onclick="event.stopPropagation();deleteChapter(${work.id},${ch.id})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            </div>
        </div>
        <div class="chapter-card-body" style="display:${isExpanded ? 'block' : 'none'}">
            ${buildChapterDetailForm(work.id, ch)}
        </div>
    </div>`;
}

function buildChapterDetailForm(workId, ch) {
    const tmpl = document.getElementById('chapterDetailTemplate');
    if (!tmpl) return '';
    let html = tmpl.innerHTML;
    html = html.replace(/{id}/g, ch.id);

    const container = document.createElement('div');
    container.innerHTML = html;
    const inner = container.querySelector('.chapter-detail-inner');
    inner.dataset.workId = workId;
    inner.dataset.chapterId = ch.id;

    // 填充数据
    inner.querySelector('[data-field="title"]').value = ch.title || '';
    inner.querySelector('[data-field="storyline"]').value = ch.storyline || '';
    inner.querySelector('[data-field="event"]').value = ch.event || '';
    inner.querySelector('[data-field="content"]').value = ch.content || '';

    // 填充动态行数据
    fillMultiRows(inner, 'characters', ch.characters || []);
    fillMultiRows(inner, 'organizations', ch.organizations || []);
    fillMultiRows(inner, 'locations', ch.locations || []);
    fillMultiRows(inner, 'skills', ch.skills || []);

    return inner.outerHTML;
}

function fillMultiRows(container, fieldName, items) {
    const wrapper = container.querySelector(`[data-field="${fieldName}"]`);
    if (!wrapper) return;
    const firstRow = wrapper.querySelector('.chapter-multi-row');
    if (!firstRow) return;

    if (items.length === 0) {
        firstRow.querySelector('.chapter-multi-name').value = '';
        firstRow.querySelector('.chapter-multi-desc').value = '';
        firstRow.querySelector('.chapter-multi-remove').classList.add('hidden');
        return;
    }

    firstRow.querySelector('.chapter-multi-name').value = items[0].name || '';
    firstRow.querySelector('.chapter-multi-desc').value = items[0].desc || '';
    firstRow.querySelector('.chapter-multi-remove').classList.remove('hidden');

    for (let i = 1; i < items.length; i++) {
        const clone = firstRow.cloneNode(true);
        clone.querySelector('.chapter-multi-name').value = items[i].name || '';
        clone.querySelector('.chapter-multi-desc').value = items[i].desc || '';
        clone.querySelector('.chapter-multi-remove').classList.remove('hidden');
        clone.querySelector('.chapter-multi-remove').setAttribute('onclick', 'removeChapterFieldRow(this)');
        wrapper.appendChild(clone);
    }
}

function toggleChapterCard(chapterId) {
    const card = document.querySelector(`.chapter-card[data-chapter-id="${chapterId}"]`);
    if (!card) return;
    const isExpanded = card.classList.toggle('expanded');
    const body = card.querySelector('.chapter-card-body');
    body.style.display = isExpanded ? 'block' : 'none';
    const arrow = card.querySelector('.chapter-card-toggle svg polyline');
    if (arrow) {
        arrow.setAttribute('points', isExpanded ? '18 15 12 9 6 15' : '6 9 12 15 18 9');
    }
    const btn = card.querySelector('.chapter-card-toggle');
    if (btn) btn.title = isExpanded ? '收起' : '展开';
}

function toggleChapterDetail(btn) {
    const inner = btn.closest('.chapter-detail-inner');
    const card = inner.closest('.chapter-card');
    const chId = inner.dataset.chapterId;
    toggleChapterCard(chId);
}

function addChapterFieldRow(btn, fieldName) {
    const section = btn.closest('.chapter-detail-section');
    const wrapper = section.querySelector('.chapter-multi-input');
    const rows = wrapper.querySelectorAll('.chapter-multi-row');
    rows.forEach(r => r.querySelector('.chapter-multi-remove').classList.remove('hidden'));

    const first = rows[0];
    const clone = first.cloneNode(true);
    clone.querySelector('.chapter-multi-name').value = '';
    clone.querySelector('.chapter-multi-desc').value = '';
    clone.querySelector('.chapter-multi-remove').classList.remove('hidden');
    clone.querySelector('.chapter-multi-remove').setAttribute('onclick', 'removeChapterFieldRow(this)');
    wrapper.appendChild(clone);
    clone.querySelector('.chapter-multi-name').focus();
}

function removeChapterFieldRow(btn) {
    const row = btn.closest('.chapter-multi-row');
    const wrapper = row.parentElement;
    const rows = wrapper.querySelectorAll('.chapter-multi-row');
    if (rows.length <= 1) {
        row.querySelector('.chapter-multi-name').value = '';
        row.querySelector('.chapter-multi-desc').value = '';
        btn.classList.add('hidden');
        return;
    }
    row.remove();
    const remaining = wrapper.querySelectorAll('.chapter-multi-row');
    if (remaining.length === 1) {
        remaining[0].querySelector('.chapter-multi-remove').classList.add('hidden');
    }
}

function saveChapterDetail(btn) {
    const inner = btn.closest('.chapter-detail-inner');
    const workId = parseInt(inner.dataset.workId);
    const chapterId = parseInt(inner.dataset.chapterId);
    const work = createdWorks.find(w => w.id === workId);
    if (!work) return;
    const ch = work.chapters.find(c => c.id === chapterId);
    if (!ch) return;

    ch.title = inner.querySelector('[data-field="title"]').value.trim();
    ch.storyline = inner.querySelector('[data-field="storyline"]').value.trim();
    ch.event = inner.querySelector('[data-field="event"]').value.trim();
    ch.wordCount = parseInt(inner.querySelector('[data-field="wordCount"]').value) || 0;
    ch.content = inner.querySelector('[data-field="content"]').value.trim();

    ch.characters = collectMultiRows(inner, 'characters');
    ch.organizations = collectMultiRows(inner, 'organizations');
    ch.locations = collectMultiRows(inner, 'locations');
    ch.skills = collectMultiRows(inner, 'skills');
    ch._saved = true;

    // 更新卡片头部信息
    const card = inner.closest('.chapter-card');
    const titleEl = card.querySelector('.chapter-card-title');
    const metaEl = card.querySelector('.chapter-card-meta');
    const statusEl = card.querySelector('.chapter-card-status');
    if (titleEl) titleEl.textContent = ch.title || '未命名章节';
    if (metaEl) metaEl.textContent = ch.event ? ch.event.substring(0, 30) + '...' : '暂无事件描述';
    if (statusEl) { statusEl.textContent = '已保存'; statusEl.className = 'chapter-card-status saved'; }

    showToast('章节已保存', 'success');
}

function collectMultiRows(container, fieldName) {
    const wrapper = container.querySelector(`[data-field="${fieldName}"]`);
    if (!wrapper) return [];
    const rows = wrapper.querySelectorAll('.chapter-multi-row');
    const result = [];
    rows.forEach(row => {
        const name = row.querySelector('.chapter-multi-name').value.trim();
        const desc = row.querySelector('.chapter-multi-desc').value.trim();
        if (name) result.push({ name, desc });
    });
    return result;
}

function updateChapterTitle(wid, cid, val) { const w = createdWorks.find(x=>x.id===wid); if(w){ const c=w.chapters.find(x=>x.id===cid); if(c) c.title=val.trim(); } }
function updateChapterContent(wid, cid, val) { const w = createdWorks.find(x=>x.id===wid); if(w){ const c=w.chapters.find(x=>x.id===cid); if(c) c.content=val; } }

// ====================== 一键生成章节 ======================

let _previewWorkId = null;
let _previewChapterId = null;
let _previewGeneratedText = '';

function generateChapter(btn) {
    const inner = btn.closest('.chapter-detail-inner');
    const workId = parseInt(inner.dataset.workId);
    const chapterId = parseInt(inner.dataset.chapterId);
    const work = createdWorks.find(w => w.id === workId);
    const ch = work ? work.chapters.find(c => c.id === chapterId) : null;
    if (!ch) return;

    // 读取当前表单数据
    const title = inner.querySelector('[data-field="title"]').value.trim();
    const storyline = inner.querySelector('[data-field="storyline"]').value.trim();
    const event = inner.querySelector('[data-field="event"]').value.trim();
    const wordCount = parseInt(inner.querySelector('[data-field="wordCount"]').value) || 3000;
    const characters = collectMultiRows(inner, 'characters');
    const organizations = collectMultiRows(inner, 'organizations');
    const locations = collectMultiRows(inner, 'locations');
    const skills = collectMultiRows(inner, 'skills');

    if (!title) { showToast('请先填写章节名称', 'warning'); return; }
    if (!storyline && !event) { showToast('请至少填写章节剧情线或核心事件', 'warning'); return; }

    // 按钮加载态
    const btnText = btn.querySelector('.btn-ai-text');
    const spinner = btn.querySelector('.spinner');
    btn.disabled = true;
    btnText.textContent = '生成中...';
    spinner.classList.remove('hidden');

    // 模拟AI生成（实际应调用后端API）
    setTimeout(() => {
        _previewGeneratedText = mockAIGenerate({
            title, storyline, event, wordCount,
            characters, organizations, locations, skills,
            workName: work.name
        });

        btn.disabled = false;
        btnText.textContent = '一键生成';
        spinner.classList.add('hidden');

        // 打开预览弹窗
        _previewWorkId = workId;
        _previewChapterId = chapterId;
        openChapterPreview(title, wordCount, event, _previewGeneratedText);
    }, 2000);
}

function mockAIGenerate(ctx) {
    const { title, storyline, event, wordCount, characters, locations, skills, workName } = ctx;
    const chars = characters.map(c => c.name).join('、') || '主角';
    const locs = locations.map(l => l.name).join('、') || '故事发生地';
    const sks = skills.map(s => s.name).join('、') || '相关能力';

    // 生成模拟正文（实际应由AI后端生成）
    const paraCount = Math.max(3, Math.floor(wordCount / 400));
    let text = `${title}

`;
    text += `${storyline || event}

`;

    for (let i = 1; i <= paraCount; i++) {
        text += `　　${locs}的风吹过，${chars}站在那里，目光深邃。${sks}在指尖流转，空气中弥漫着紧张的气息。`;
        if (event) text += `这一章，正是${event.substring(0, 20)}的关键时刻。`;
        text += `周围的景物在${sks}的映照下显得格外不同，仿佛整个世界都在等待这一刻的到来。

`;
    }

    text += `　　故事还在继续，下一章将更加精彩……

`;
    text += `【本章节为AI一键生成预览，字数约 ${wordCount} 字。确认发布后正式写入作品。】`;
    return text;
}

// ====================== 预览弹窗 ======================

function openChapterPreview(title, wordCount, event, content) {
    document.getElementById('previewTitle').textContent = title || '-';
    document.getElementById('previewWordCount').textContent = (wordCount || '-') + ' 字';
    document.getElementById('previewEvent').textContent = event || '-';
    document.getElementById('previewContent').textContent = content;
    document.getElementById('chapterPreviewModal').classList.remove('hidden');
}

function closeChapterPreview() {
    document.getElementById('chapterPreviewModal').classList.add('hidden');
    _previewWorkId = null;
    _previewChapterId = null;
    _previewGeneratedText = '';
}

function confirmPublishFromPreview() {
    if (!_previewWorkId || !_previewChapterId) return;

    const work = createdWorks.find(w => w.id === _previewWorkId);
    const ch = work ? work.chapters.find(c => c.id === _previewChapterId) : null;
    if (!ch) return;

    // 将预览内容写入章节
    const card = document.querySelector(`.chapter-card[data-chapter-id="${_previewChapterId}"]`);
    if (card) {
        const contentArea = card.querySelector('[data-field="content"]');
        if (contentArea) contentArea.value = _previewGeneratedText;
    }

    ch.content = _previewGeneratedText;
    ch._saved = true;
    ch._published = true;

    // 更新卡片状态
    if (card) {
        const statusEl = card.querySelector('.chapter-card-status');
        if (statusEl) { statusEl.textContent = '已发布'; statusEl.className = 'chapter-card-status saved'; }
    }

    closeChapterPreview();
    showToast('章节已发布！', 'success');
    renderChapterWorkList();
}

// ====================== 发布章节（直接发布） ======================

function publishChapter(btn) {
    const inner = btn.closest('.chapter-detail-inner');
    const workId = parseInt(inner.dataset.workId);
    const chapterId = parseInt(inner.dataset.chapterId);
    const work = createdWorks.find(w => w.id === workId);
    const ch = work ? work.chapters.find(c => c.id === chapterId) : null;
    if (!ch) return;

    const title = inner.querySelector('[data-field="title"]').value.trim();
    const content = inner.querySelector('[data-field="content"]').value.trim();

    if (!title) { showToast('请先填写章节名称', 'warning'); return; }

    // 收集所有数据
    ch.title = title;
    ch.storyline = inner.querySelector('[data-field="storyline"]').value.trim();
    ch.event = inner.querySelector('[data-field="event"]').value.trim();
    ch.wordCount = parseInt(inner.querySelector('[data-field="wordCount"]').value) || 0;
    ch.content = content;
    ch.characters = collectMultiRows(inner, 'characters');
    ch.organizations = collectMultiRows(inner, 'organizations');
    ch.locations = collectMultiRows(inner, 'locations');
    ch.skills = collectMultiRows(inner, 'skills');
    ch._saved = true;
    ch._published = true;

    // 更新卡片头部
    const card = inner.closest('.chapter-card');
    const titleEl = card.querySelector('.chapter-card-title');
    const metaEl = card.querySelector('.chapter-card-meta');
    const statusEl = card.querySelector('.chapter-card-status');
    if (titleEl) titleEl.textContent = ch.title || '未命名章节';
    if (metaEl) metaEl.textContent = ch.event ? ch.event.substring(0, 30) + '...' : '暂无事件描述';
    if (statusEl) { statusEl.textContent = '已发布'; statusEl.className = 'chapter-card-status saved'; }

    showToast('章节已发布！', 'success');
    renderChapterWorkList();
}

// 点击弹窗遮罩关闭
document.addEventListener('click', (e) => {
    const modal = document.getElementById('chapterPreviewModal');
    if (e.target === modal) closeChapterPreview();
});

// ESC 关闭弹窗
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeChapterPreview();
});

function addNewChapter() {
    const activeItem = document.querySelector('.chapter-work-item.active');
    if (!activeItem) { showToast('请先选择一部作品', 'warning'); return; }
    const match = activeItem.getAttribute('onclick').match(/selectWork\((\d+)\)/);
    if (!match) return;
    const work = createdWorks.find(w => w.id === parseInt(match[1]));
    if (!work) return;
    work.chapters.push({
        id: Date.now(),
        title: `第${work.chapters.length+1}章`,
        storyline: '',
        characters: [],
        organizations: [],
        locations: [],
        skills: [],
        wordCount: 3000,
        event: '',
        content: '',
        _expanded: true,
        _saved: false,
        _published: false
    });
    document.getElementById('chapterCount').textContent = `${work.chapters.length} 个章节`;
    renderChapterList(work); renderChapterWorkList();
    showToast('新章节已添加', 'success');
    const area = document.getElementById('chapterListArea');
    setTimeout(() => area.scrollTop = area.scrollHeight, 100);
}

function updateChapterTitle(wid, cid, val) { const w = createdWorks.find(x=>x.id===wid); if(w){ const c=w.chapters.find(x=>x.id===cid); if(c) c.title=val.trim(); } }
function updateChapterContent(wid, cid, val) { const w = createdWorks.find(x=>x.id===wid); if(w){ const c=w.chapters.find(x=>x.id===cid); if(c) c.content=val; } }

function deleteChapter(workId, chapterId) {
    const work = createdWorks.find(w => w.id === workId);
    if (!work) return;
    work.chapters = work.chapters.filter(c => c.id !== chapterId);
    document.getElementById('chapterCount').textContent = `${work.chapters.length} 个章节`;
    renderChapterList(work); renderChapterWorkList();
    showToast('章节已删除', 'success');
}

function resetCreateForm() {
    document.getElementById('newWorkForm').reset();
    currentTags = []; renderTags();
    const n1 = document.querySelector('#workName + .char-count');
    const n2 = document.querySelector('#workSynopsis + .char-count');
    if(n1) n1.textContent='0/100'; if(n2) n2.textContent='0/2000';
    const list = document.getElementById('characterList');
    const rows = list.querySelectorAll('.character-row');
    rows.forEach((r,i) => { if(i>0) r.remove(); });
    if(rows[0]) {
        rows[0].querySelector('.char-name').value='';
        rows[0].querySelector('.char-desc').value='';
        rows[0].querySelector('.char-relation').value='';
        rows[0].querySelector('.btn-char-remove').classList.add('hidden');
    }
}

function escapeHtml(str) { if(!str) return ''; const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }
