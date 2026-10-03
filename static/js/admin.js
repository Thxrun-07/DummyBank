document.addEventListener('DOMContentLoaded', () => {
  const tabSheetUsers = document.getElementById('tabSheetUsers');
  const tabSheetLogs = document.getElementById('tabSheetLogs');
  const usersSheetContainer = document.getElementById('usersSheetContainer');
  const logsSheetContainer = document.getElementById('logsSheetContainer');
  const refreshDataBtn = document.getElementById('refreshDataBtn');
  const adminSearchInput = document.getElementById('adminSearchInput');

  let currentSheet = 'users';
  let cachedData = { users: [], logs: [] };

  // Tab switching
  tabSheetUsers.addEventListener('click', () => {
    currentSheet = 'users';
    tabSheetUsers.className = 'px-4 py-2 text-xs font-bold rounded-lg text-white bg-emerald-600 shadow-md transition-all flex items-center gap-2';
    tabSheetLogs.className = 'px-4 py-2 text-xs font-bold rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-2';
    usersSheetContainer.classList.remove('hidden');
    logsSheetContainer.classList.add('hidden');
    filterTables();
  });

  tabSheetLogs.addEventListener('click', () => {
    currentSheet = 'logs';
    tabSheetLogs.className = 'px-4 py-2 text-xs font-bold rounded-lg text-white bg-emerald-600 shadow-md transition-all flex items-center gap-2';
    tabSheetUsers.className = 'px-4 py-2 text-xs font-bold rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-2';
    logsSheetContainer.classList.remove('hidden');
    usersSheetContainer.classList.add('hidden');
    filterTables();
  });

  refreshDataBtn.addEventListener('click', () => {
    refreshDataBtn.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i><span>Refreshing...</span>';
    fetchExcelData().finally(() => {
      refreshDataBtn.innerHTML = '<i class="fa-solid fa-rotate"></i><span>Refresh</span>';
    });
  });

  adminSearchInput.addEventListener('input', () => {
    filterTables();
  });

  async function fetchExcelData() {
    try {
      const res = await fetch('/api/excel-data');
      if (res.status === 403 || res.status === 401) {
        window.location.href = '/';
        return;
      }
      const data = await res.json();
      if (data.success) {
        cachedData = data;
        document.getElementById('totalUsersCount').textContent = data.total_users || 0;
        document.getElementById('totalLogsCount').textContent = data.total_logs || 0;
        renderUsers(data.users);
        renderLogs(data.logs);
      } else {
        window.location.href = '/';
      }
    } catch (err) {
      console.error('Error fetching Excel data:', err);
    }
  }

  function renderUsers(users) {
    const tbody = document.getElementById('adminUsersTableBody');
    if (!users || users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="px-4 py-8 text-center text-slate-500 font-sans">No users registered yet in Excel.</td></tr>';
      return;
    }

    tbody.innerHTML = users.map(u => `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="px-4 py-3 font-bold text-emerald-400">#${u.id}</td>
        <td class="px-4 py-3 text-slate-200 font-sans font-medium">${escapeHtml(u.full_name)}</td>
        <td class="px-4 py-3 text-slate-300">@${escapeHtml(u.username)}</td>
        <td class="px-4 py-3 text-slate-400 font-sans">${escapeHtml(u.email)}</td>
        <td class="px-4 py-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${u.role === 'Admin' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'}">
            ${u.role || 'User'}
          </span>
        </td>
        <td class="px-4 py-3 text-slate-300 font-mono text-[11px]">${escapeHtml(u.password || '')}</td>
        <td class="px-4 py-3 text-slate-400">${u.registered_at}</td>
        <td class="px-4 py-3 text-slate-400">${u.last_login}</td>
        <td class="px-4 py-3 text-center font-bold text-emerald-400">${u.login_count}</td>
      </tr>
    `).join('');
  }

  function renderLogs(logs) {
    const tbody = document.getElementById('adminLogsTableBody');
    if (!logs || logs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="px-4 py-8 text-center text-slate-500 font-sans">No login logs recorded yet in Excel.</td></tr>';
      return;
    }

    tbody.innerHTML = logs.map(l => {
      const isSuccess = l.status === 'SUCCESS';
      const badgeClass = isSuccess 
        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
        : 'bg-rose-500/10 text-rose-400 border-rose-500/20';

      return `
        <tr class="hover:bg-slate-800/40 transition-colors">
          <td class="px-4 py-3 font-bold text-slate-400">#${l.log_id}</td>
          <td class="px-4 py-3 text-slate-200">${escapeHtml(l.identifier)}</td>
          <td class="px-4 py-3 text-slate-400">${l.timestamp}</td>
          <td class="px-4 py-3 text-center">
            <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeClass}">
              ${l.status}
            </span>
          </td>
          <td class="px-4 py-3 text-center text-slate-400">${escapeHtml(l.ip)}</td>
          <td class="px-4 py-3 text-slate-500 truncate max-w-xs" title="${escapeHtml(l.user_agent)}">${escapeHtml(l.user_agent)}</td>
        </tr>
      `;
    }).join('');
  }

  function filterTables() {
    const query = adminSearchInput.value.toLowerCase().trim();
    if (currentSheet === 'users') {
      const filtered = cachedData.users.filter(u => 
        String(u.id).includes(query) ||
        (u.full_name && u.full_name.toLowerCase().includes(query)) ||
        (u.username && u.username.toLowerCase().includes(query)) ||
        (u.email && u.email.toLowerCase().includes(query))
      );
      renderUsers(filtered);
    } else {
      const filtered = cachedData.logs.filter(l => 
        String(l.log_id).includes(query) ||
        (l.identifier && l.identifier.toLowerCase().includes(query)) ||
        (l.status && l.status.toLowerCase().includes(query)) ||
        (l.ip && l.ip.toLowerCase().includes(query))
      );
      renderLogs(filtered);
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, function(m) {
      return ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      })[m];
    });
  }

  fetchExcelData();
});
