// ============ 元素 ============
const $ = (id) => document.getElementById(id);

const tbody = $('tbody');
const countEl = $('count');
const pager = $('pager');
const toastEl = $('toast');
const modal = $('modal');
const detailModal = $('detail-modal');
const moodsBox = $('moods');
const moodResult = $('mood-result');

// ============ 状态 ============
const PAGE_SIZE = 20;
const ALL_TAGS = ['辣', '甜', '汤', '肉', '素', '快', '清淡'];

let all = [];
let view = [];
let page = 1;
let keyword = '';
let activeTag = '';
let sortMode = 'default';
let editingId = null;
let termsData = null;

// ============ 工具 ============

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  // 登录过期：跳回登录页（桌面版要带上后端地址）
  if (res.status === 401) {
    const base = (typeof API_BASE !== 'undefined') ? API_BASE : '';
    window.location.href = base + '/login';
    throw new Error('登录已过期');
  }

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const detail = data && data.detail;
    const text = typeof detail === 'string'
      ? detail
      : (Array.isArray(detail) ? detail.map(d => d.msg).join('；') : '请求失败');
    throw new Error(text || `HTTP ${res.status}`);
  }
  return data;
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

let toastTimer;
function toast(message, type = 'ok') {
  toastEl.textContent = message;
  toastEl.className = `toast show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastEl.className = `toast ${type}`; }, 2200);
}

function tagList(str) {
  return String(str || '').split(',').map(t => t.trim()).filter(Boolean);
}

function tagHtml(str) {
  const list = tagList(str);
  if (!list.length) return '<span class="tag muted">无标签</span>';
  return list.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('');
}

// ============ 数据 ============
async function loadDishes() {
  all = await api('/query_all_menu');
  applyFilters();
}

function applyFilters() {
  const kw = keyword.trim().toLowerCase();

  view = all.filter(d => {
    const hitKeyword = !kw
      || d.name.toLowerCase().includes(kw)
      || (d.description || '').toLowerCase().includes(kw);
    const hitTag = !activeTag || tagList(d.tags).includes(activeTag);
    return hitKeyword && hitTag;
  });

  if (sortMode === 'price-asc') view.sort((a, b) => a.price - b.price);
  else if (sortMode === 'price-desc') view.sort((a, b) => b.price - a.price);
  else if (sortMode === 'name') view.sort((a, b) => a.name.localeCompare(b.name, 'zh'));
  else view.sort((a, b) => a.id - b.id);

  const maxPage = Math.max(1, Math.ceil(view.length / PAGE_SIZE));
  if (page > maxPage) page = maxPage;

  renderPage();
}

// ============ 渲染 ============
function rowHtml(d) {
  return `
    <tr>
      <td>
        <span class="dish-name">${escapeHtml(d.name)}</span><span class="dish-tags">${tagHtml(d.tags)}</span>
      </td>
      <td class="price">¥${Number(d.price).toFixed(2)}</td>
      <td class="desc">${escapeHtml(d.description || '—')}</td>
      <td class="ops">
        <button type="button" class="icon-btn detail" data-id="${d.id}">详情</button>
        <button type="button" class="icon-btn edit" data-id="${d.id}">编辑</button>
        <button type="button" class="icon-btn del" data-id="${d.id}">删除</button>
      </td>
    </tr>`;
}

function renderPage() {
  countEl.textContent = `共 ${view.length} 道`;

  const start = (page - 1) * PAGE_SIZE;
  const rows = view.slice(start, start + PAGE_SIZE);

  tbody.innerHTML = rows.length
    ? rows.map(rowHtml).join('')
    : '<tr><td colspan="4" class="empty">没有找到菜谱，换个关键词或标签试试</td></tr>';

  renderPager();
}

function renderPager() {
  const total = Math.max(1, Math.ceil(view.length / PAGE_SIZE));
  if (total <= 1) {
    pager.innerHTML = '';
    return;
  }

  const from = Math.max(1, Math.min(page - 2, total - 4));
  const to = Math.min(total, from + 4);

  const nums = [];
  for (let i = from; i <= to; i += 1) nums.push(i);

  pager.innerHTML = `
    <button type="button" class="pg" data-p="${page - 1}" ${page === 1 ? 'disabled' : ''}>上一页</button>
    ${nums.map(n => `<button type="button" class="pg ${n === page ? 'on' : ''}" data-p="${n}">${n}</button>`).join('')}
    <button type="button" class="pg" data-p="${page + 1}" ${page === total ? 'disabled' : ''}>下一页</button>
    <span class="pg-info">${page} / ${total}</span>`;
}

// ============ 搜索 / 排序 / 标签筛选 ============
let searchTimer;
const searchInput = $('search');
const searchClear = $('search-clear');

function syncSearchClear() {
  searchClear.hidden = !searchInput.value;
}

searchInput.addEventListener('input', (e) => {
  syncSearchClear();
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    keyword = e.target.value;
    page = 1;
    applyFilters();
  }, 250);
});

searchClear.addEventListener('click', () => {
  searchInput.value = '';
  keyword = '';
  page = 1;
  applyFilters();
  syncSearchClear();
  searchInput.focus();
});

syncSearchClear();

$('sort').addEventListener('change', (e) => {
  sortMode = e.target.value;
  page = 1;
  applyFilters();
});

$('tag-filter').addEventListener('click', (e) => {
  const chip = e.target.closest('.chip');
  if (!chip) return;

  document.querySelectorAll('#tag-filter .chip').forEach(c => c.classList.toggle('on', c === chip));
  activeTag = chip.dataset.tag;
  page = 1;
  applyFilters();
});

// ============ 分页 ============
pager.addEventListener('click', (e) => {
  const btn = e.target.closest('.pg');
  if (!btn || btn.disabled) return;
  page = Number(btn.dataset.p);
  renderPage();
});

// ============ 添加 / 编辑弹窗 ============
function renderTagPicker(selected) {
  $('f-tags').innerHTML = ALL_TAGS.map(t => `
    <button type="button" class="tag-chip ${selected.includes(t) ? 'on' : ''}" data-tag="${t}">${t}</button>
  `).join('');
}

function openModal(dish) {
  editingId = dish ? dish.id : null;
  $('modal-title').textContent = dish ? '编辑菜谱' : '添加菜谱';
  $('f-name').value = dish ? dish.name : '';
  $('f-price').value = dish ? dish.price : 0;
  $('f-desc').value = dish ? dish.description : '';
  $('f-intro').value = dish ? dish.intro : '';
  $('f-steps').value = dish ? dish.steps : '';
  $('f-video').value = dish ? dish.video_url : '';
  $('f-image').value = dish ? dish.image_url : '';
  renderTagPicker(dish ? tagList(dish.tags) : []);
  modal.hidden = false;
  setTimeout(() => $('f-name').focus(), 60);
}

function closeModal() {
  modal.hidden = true;
  editingId = null;
}

$('btn-add').addEventListener('click', () => openModal(null));

modal.addEventListener('click', (e) => {
  if (e.target.closest('[data-close]')) closeModal();
});

$('f-tags').addEventListener('click', (e) => {
  const chip = e.target.closest('.tag-chip');
  if (chip) chip.classList.toggle('on');
});

// ============ 详情弹窗 ============

// 把各种视频链接转成可以直接播放的嵌入代码
function buildVideoEmbed(url) {
  if (!url) return null;

  // B 站：https://www.bilibili.com/video/BVxxxxxxxxxx
  const bv = url.match(/BV[0-9A-Za-z]{10}/);
  if (bv) {
    return `<iframe src="https://player.bilibili.com/player.html?bvid=${bv[0]}&page=1&danmaku=0&autoplay=0"
      scrolling="no" frameborder="0" allowfullscreen
      allow="autoplay; fullscreen; picture-in-picture"></iframe>`;
  }

  // YouTube
  const yt = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})/);
  if (yt) {
    return `<iframe src="https://www.youtube.com/embed/${yt[1]}"
      frameborder="0" allowfullscreen
      allow="autoplay; fullscreen; picture-in-picture"></iframe>`;
  }

  // 直链视频文件
  if (/\.(mp4|webm|ogg)(\?|$)/i.test(url)) {
    return `<video src="${escapeHtml(url)}" controls playsinline preload="metadata"></video>`;
  }

  return null;
}

function openDetail(dish) {
  $('d-name').textContent = dish.name;
  $('d-price').textContent = `¥${Number(dish.price).toFixed(2)}`;
  $('d-tags').innerHTML = tagHtml(dish.tags);

  // 有填链接就用它，没填就自动去 B 站搜「菜名 + 做法」
  const customUrl = String(dish.video_url || '').trim();
  const videoLink = $('d-video');
  videoLink.href = customUrl
    || `https://search.bilibili.com/all?keyword=${encodeURIComponent(dish.name + ' 做法')}`;
  videoLink.textContent = customUrl ? '在新窗口打开' : '▶ 去 B 站搜这道菜的做法';

  // 能嵌入就直接在弹窗里播
  const box = $('d-video-box');
  const embed = buildVideoEmbed(customUrl);
  if (embed) {
    box.innerHTML = embed;
    box.hidden = false;
    videoLink.textContent = '在新窗口打开';
  } else {
    box.innerHTML = '';
    box.hidden = true;
  }

  $('d-intro').textContent = dish.intro || '这道菜还没有介绍。';
  $('d-intro').style.opacity = dish.intro ? '1' : '0.55';

  const steps = String(dish.steps || '')
    .split('\n')
    .map(s => s.replace(/^\s*\d+[.、．]\s*/, '').trim())
    .filter(Boolean);

  $('d-steps').innerHTML = steps.map(s => `<li>${escapeHtml(s)}</li>`).join('');
  $('d-steps-wrap').hidden = steps.length === 0;
  $('detail-modal').hidden = false;
}

detailModal.addEventListener('click', (e) => {
  if (e.target.closest('[data-close]')) detailModal.hidden = true;
});

document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  if (!modal.hidden) closeModal();
  if (!detailModal.hidden) detailModal.hidden = true;
});

// ============ 提交新增 / 编辑 ============
$('dish-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const body = {
    name: $('f-name').value.trim(),
    price: Number($('f-price').value || 0),
    description: $('f-desc').value.trim(),
    tags: [...$('f-tags').querySelectorAll('.tag-chip.on')].map(b => b.dataset.tag).join(','),
    intro: $('f-intro').value.trim(),
    steps: $('f-steps').value.trim(),
    video_url: $('f-video').value.trim(),
    image_url: $('f-image').value.trim(),
  };

  if (!body.name) {
    toast('菜名不能为空', 'err');
    return;
  }

  try {
    if (editingId) {
      await api(`/update_menu?menu_id=${editingId}`, { method: 'PUT', body: JSON.stringify(body) });
      toast('已保存');
    } else {
      await api('/add_menu', { method: 'POST', body: JSON.stringify(body) });
      toast(`「${body.name}」已添加`);
    }
    closeModal();
    await loadDishes();
  } catch (err) {
    toast(err.message, 'err');
  }
});

// ============ 表格操作 ============
tbody.addEventListener('click', async (e) => {
  const detailBtn = e.target.closest('.detail');
  const editBtn = e.target.closest('.edit');
  const delBtn = e.target.closest('.del');

  if (detailBtn) {
    const dish = all.find(d => String(d.id) === detailBtn.dataset.id);
    if (dish) openDetail(dish);
    return;
  }

  if (editBtn) {
    const dish = all.find(d => String(d.id) === editBtn.dataset.id);
    if (dish) openModal(dish);
    return;
  }

  if (delBtn) {
    const id = delBtn.dataset.id;
    const dish = all.find(d => String(d.id) === id);
    if (!confirm(`删除「${dish ? dish.name : id}」？`)) return;

    try {
      await api(`/delete_menu?menu_id=${id}`, { method: 'DELETE' });
      toast('已删除');
      await loadDishes();
    } catch (err) {
      toast(err.message, 'err');
    }
  }
});

// ============ 随机推荐 ============
$('btn-random').addEventListener('click', async () => {
  try {
    const list = await api('/recommend/simple?limit=3');
    toast('随机推荐：' + list.map(d => d.name).join(' · '));
  } catch (err) {
    toast(err.message, 'err');
  }
});

// ============ 心情推荐 ============
async function loadMoods() {
  try {
    const moods = await api('/recommend/moods');
    moodsBox.innerHTML = moods.map(m => `
      <button type="button" class="mood" data-mood="${escapeHtml(m.mood)}">${escapeHtml(m.mood)}</button>
    `).join('');
  } catch (err) {
    moodsBox.innerHTML = `<span class="hint">心情加载失败：${escapeHtml(err.message)}</span>`;
  }
}

async function pickByMood(mood, btn) {
  document.querySelectorAll('.mood').forEach(b => b.classList.toggle('active', b === btn));

  moodResult.hidden = false;
  moodResult.className = 'result';
  moodResult.innerHTML = '<span class="hint">正在挑菜…</span>';

  try {
    const [dish] = await api(`/recommend/mood?mood=${encodeURIComponent(mood)}&limit=1`);
    moodResult.innerHTML = `
      <span class="r-name">${escapeHtml(dish.name)}</span>
      <span class="r-price">¥${Number(dish.price).toFixed(2)}</span>
      <span class="r-desc">${escapeHtml(dish.description || '这道菜还没有描述')}</span>
      <span class="r-tags">${tagHtml(dish.tags)}</span>
      <button type="button" class="ghost again" data-mood="${escapeHtml(mood)}">换一道</button>
    `;
  } catch (err) {
    moodResult.className = 'result err';
    moodResult.innerHTML = `<span class="hint">${escapeHtml(err.message)}</span>`;
  }
}

moodsBox.addEventListener('click', (e) => {
  const btn = e.target.closest('.mood');
  if (btn) pickByMood(btn.dataset.mood, btn);
});

moodResult.addEventListener('click', (e) => {
  const again = e.target.closest('.again');
  if (!again) return;
  const btn = moodsBox.querySelector(`.mood[data-mood="${again.dataset.mood}"]`);
  if (btn) pickByMood(again.dataset.mood, btn);
});

// ============ 节气推荐 ============
async function loadTerms() {
  try {
    termsData = await api('/recommend/solar-terms');
    const sel = $('term-select');
    sel.innerHTML = termsData.items.map(t => `
      <option value="${escapeHtml(t.name)}" ${t.name === termsData.current ? 'selected' : ''}>
        ${escapeHtml(t.name)} ${t.date}
      </option>`).join('');
    updateTermInfo();
  } catch (err) {
    $('term-foods').textContent = '节气加载失败';
  }
}

function updateTermInfo() {
  const sel = $('term-select');
  const item = termsData && termsData.items.find(t => t.name === sel.value);
  $('term-foods').innerHTML = item
    ? `宜：<strong>${item.foods.map(escapeHtml).join('、')}</strong>`
    : '';
  $('term-result').hidden = true;
}

$('term-select').addEventListener('change', updateTermInfo);

$('btn-term').addEventListener('click', async () => {
  const term = $('term-select').value;
  const box = $('term-result');

  box.hidden = false;
  box.className = 'result';
  box.innerHTML = '<span class="hint">正在挑菜…</span>';

  try {
    const data = await api(`/recommend/solar-term?term=${encodeURIComponent(term)}&limit=5`);
    box.innerHTML = `
      <span class="r-name">${escapeHtml(data.name)}</span>
      <span class="r-desc">${escapeHtml(data.season)}季 · 宜 ${escapeHtml(data.foods.join('、'))}</span>
      <span class="r-tags">${data.dishes.map(d => `<span class="tag">${escapeHtml(d.name)}</span>`).join('')}</span>
    `;
  } catch (err) {
    box.className = 'result err';
    box.innerHTML = `<span class="hint">${escapeHtml(err.message)}</span>`;
  }
});

// ============ 控制区折叠 ============
const controls = $('controls');
const btnCollapse = $('btn-collapse');

function setCollapsed(collapsed) {
  controls.classList.toggle('collapsed', collapsed);
  btnCollapse.textContent = collapsed ? '展开 ▾' : '收起 ▴';
  try {
    localStorage.setItem('controls-collapsed', collapsed ? '1' : '0');
  } catch (e) {
    /* file:// 下可能被禁用，忽略 */
  }
}

btnCollapse.addEventListener('click', () => {
  setCollapsed(!controls.classList.contains('collapsed'));
});

try {
  if (localStorage.getItem('controls-collapsed') === '1') setCollapsed(true);
} catch (e) {
  /* 忽略 */
}

// ============ 退出登录 ============
$('btn-logout').addEventListener('click', async () => {
  const base = (typeof API_BASE !== 'undefined') ? API_BASE : '';
  try {
    await fetch(base + '/logout', { method: 'POST', credentials: 'include' });
  } catch (e) {
    /* 忽略 */
  }
  window.location.href = base + '/login';
});

// ============ 左上角「今日」卡片 ============
let todayDish = null;

async function loadTodayCard() {
  const card = $('today-card');
  const imgWrap = $('today-img-wrap');

  try {
    const data = await api('/recommend/solar-term?limit=1');
    todayDish = data.dishes[0] || null;
    if (!todayDish) return;

    const date = new Date();
    $('today-term').textContent = `${data.name} · ${date.getMonth() + 1}月${date.getDate()}日`;
    $('today-dish').textContent = `今日推荐 ${todayDish.name}`;

    imgWrap.innerHTML = todayDish.image_url
      ? `<img src="${escapeHtml(todayDish.image_url)}" alt="">`
      : escapeHtml(todayDish.name.slice(0, 1));

    card.hidden = false;
  } catch (err) {
    card.hidden = true;
  }
}

$('today-card').addEventListener('click', () => {
  if (todayDish) openDetail(todayDish);
});

// ============ 跟随鼠标的菜品预览 ============
const preview = $('dish-preview');
let pvRow = null;
let pvOn = false;
let pvX = 0, pvY = 0, pvTargetX = 0, pvTargetY = 0, pvRaf = null;

function pvLoop() {
  pvX += (pvTargetX - pvX) * 0.25;
  pvY += (pvTargetY - pvY) * 0.25;
  preview.style.transform = `translate(${pvX}px, ${pvY}px) translate(-50%, -50%) scale(${pvOn ? 1 : 0.8})`;
  pvRaf = requestAnimationFrame(pvLoop);
}

function pvStart() {
  if (!pvRaf) pvRaf = requestAnimationFrame(pvLoop);
}

function showPreview(dish) {
  if (!dish) return hidePreview();

  const img = String(dish.image_url || '').trim();
  preview.innerHTML = img
    ? `<img src="${escapeHtml(img)}" alt="${escapeHtml(dish.name)}" loading="lazy">`
    : `<div class="pv-fallback">${escapeHtml(dish.name.slice(0, 2))}</div>`;

  pvOn = true;
  preview.classList.add('show');
  pvStart();
}

function hidePreview() {
  pvOn = false;
  pvRow = null;
  preview.classList.remove('show');
}

function dishFromRow(tr) {
  const el = tr.querySelector('.dish-name');
  if (!el) return null;
  return all.find(d => d.name === el.textContent.trim()) || null;
}

tbody.addEventListener('mousemove', (e) => {
  const tr = e.target.closest('tbody tr');
  if (!tr || tr.querySelector('.empty')) return hidePreview();

  // 圆点出现在光标右下方，避免挡住指针
  pvTargetX = e.clientX + 108;
  pvTargetY = e.clientY + 26;

  if (tr !== pvRow) {
    pvRow = tr;
    showPreview(dishFromRow(tr));
  }
});

tbody.addEventListener('mouseleave', hidePreview);
window.addEventListener('scroll', hidePreview, { passive: true });

// ============ 背景视频 ============
const bgVideo = $('bg-video');

if (bgVideo) {
  // 慢放：0.55 倍速，像慢镜头里的炒菜
  bgVideo.playbackRate = 0.55;

  const markReady = () => {
    bgVideo.classList.add('ready');
    document.body.classList.remove('no-video');
  };

  // 脚本可能在视频已经开始播放之后才执行，先检查一次当前状态
  if (bgVideo.readyState >= 2) markReady();

  ['loadeddata', 'canplay', 'playing'].forEach((evt) => {
    bgVideo.addEventListener(evt, markReady);
  });

  bgVideo.addEventListener('error', () => {
    document.body.classList.add('no-video');
  });

  // 主动请求播放一次（部分浏览器会拦截自动播放）
  const playing = bgVideo.play();
  if (playing && typeof playing.catch === 'function') {
    playing.catch(() => {
      // 被拦截时，等用户第一次点击页面再试
      document.addEventListener(
        'click',
        () => { bgVideo.play().catch(() => {}); },
        { once: true },
      );
    });
  }

  // 只有真的没有视频源时才降级成热气背景
  setTimeout(() => {
    if (bgVideo.networkState === 3) {
      document.body.classList.add('no-video');
    }
  }, 6000);
}

// ============ 启动 ============
loadDishes().catch(err => toast('加载失败：' + err.message, 'err'));
loadMoods();
loadTerms();
loadTodayCard();
