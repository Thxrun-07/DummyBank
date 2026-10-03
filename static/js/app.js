document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const tabLogin = document.getElementById('tabLogin');
  const tabRegister = document.getElementById('tabRegister');
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const authSection = document.getElementById('authSection');
  const dashboardSection = document.getElementById('dashboardSection');
  const authAlert = document.getElementById('authAlert');
  const alertIcon = document.getElementById('alertIcon');
  const alertMessage = document.getElementById('alertMessage');
  const logoutBtn = document.getElementById('logoutBtn');

  // Admin and Navigation elements
  const adminHeaderActions = document.getElementById('adminHeaderActions');
  const userHeaderBadge = document.getElementById('userHeaderBadge');
  const navUsername = document.getElementById('navUsername');
  const dashAdminDownload = document.getElementById('dashAdminDownload');
  const adminRecordsSection = document.getElementById('adminRecordsSection');
  const userNoticeSection = document.getElementById('userNoticeSection');
  const footerAdminContainer = document.getElementById('footerAdminContainer');
  const dashRoleBadge = document.getElementById('dashRoleBadge');

  // Password visibility toggle
  document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', () => {
      const input = button.parentElement.querySelector('input');
      const icon = button.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      }
    });
  });

  // Tab switching
  tabLogin.addEventListener('click', () => {
    tabLogin.className = 'flex-1 py-2 text-sm font-semibold rounded-lg text-white bg-emerald-600 transition-all duration-200 shadow-md';
    tabRegister.className = 'flex-1 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white transition-all duration-200';
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
    hideAlert();
  });

  tabRegister.addEventListener('click', () => {
    tabRegister.className = 'flex-1 py-2 text-sm font-semibold rounded-lg text-white bg-emerald-600 transition-all duration-200 shadow-md';
    tabLogin.className = 'flex-1 py-2 text-sm font-semibold rounded-lg text-slate-400 hover:text-white transition-all duration-200';
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    hideAlert();
  });

  function showAlert(message, type = 'error') {
    authAlert.classList.remove('hidden', 'bg-rose-950/60', 'border-rose-800/60', 'text-rose-300', 'bg-emerald-950/60', 'border-emerald-800/60', 'text-emerald-300');
    if (type === 'error') {
      authAlert.classList.add('bg-rose-950/60', 'border-rose-800/60', 'text-rose-300');
      alertIcon.className = 'fa-solid fa-circle-exclamation text-rose-400';
    } else {
      authAlert.classList.add('bg-emerald-950/60', 'border-emerald-800/60', 'text-emerald-300');
      alertIcon.className = 'fa-solid fa-circle-check text-emerald-400';
    }
    alertMessage.textContent = message;
  }

  function hideAlert() {
    authAlert.classList.add('hidden');
  }

  // Handle Login
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    const identifier = document.getElementById('loginIdentifier').value.trim();
    const password = document.getElementById('loginPassword').value;
    const submitBtn = document.getElementById('loginSubmitBtn');

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Verifying...';

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        showDashboard(data.user);
      } else {
        showAlert(data.message || 'Login failed. Please check your credentials.', 'error');
      }
    } catch (err) {
      showAlert('Unable to connect to the server. Please check your connection.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Sign In</span><i class="fa-solid fa-arrow-right text-xs"></i>';
    }
  });

  // Handle Registration
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    const fullName = document.getElementById('regFullName').value.trim();
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    const submitBtn = document.getElementById('registerSubmitBtn');

    if (password !== confirmPassword) {
      showAlert('Passwords do not match. Please verify.', 'error');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Saving to Excel...';

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName, username, email, password })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        showDashboard(data.user);
      } else {
        showAlert(data.message || 'Registration failed.', 'error');
      }
    } catch (err) {
      showAlert('Server error. Could not save to Excel.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>Create Account in Excel</span><i class="fa-solid fa-check text-xs"></i>';
    }
  });

  // Handle Logout
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await fetch('/api/logout', { method: 'POST' });
        showAuth();
      } catch (err) {
        console.error(err);
      }
    });
  }

  function showDashboard(user) {
    authSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');

    document.getElementById('dashFullName').textContent = user.full_name || user.username;
    document.getElementById('dashUserId').textContent = '#' + (user.id || 1);
    document.getElementById('dashUsername').textContent = user.username;
    document.getElementById('dashEmail').textContent = user.email;
    document.getElementById('dashRegisteredAt').textContent = user.registered_at || 'Just now';
    document.getElementById('dashLoginCount').textContent = user.login_count || 1;
    document.getElementById('dashLastLogin').textContent = 'Last: ' + (user.last_login || 'Just now');

    // Initials for avatar
    const initials = (user.full_name || user.username || 'U')
      .split(' ')
      .map(n => n[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
    document.getElementById('userAvatar').textContent = initials;

    // Header badge
    userHeaderBadge.classList.remove('hidden');
    navUsername.textContent = user.username;

    // STRICT ROLE CONTROL:
    // Only admin@123 gets download button and admin sheet viewer
    if (user.is_admin) {
      dashRoleBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Administrator (Download Access)';
      adminHeaderActions.classList.remove('hidden');
      dashAdminDownload.classList.remove('hidden');
      adminRecordsSection.classList.remove('hidden');
      footerAdminContainer.classList.remove('hidden');
      userNoticeSection.classList.add('hidden');
      loadDashboardUsers();
    } else {
      dashRoleBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span> Standard User';
      adminHeaderActions.classList.add('hidden');
      dashAdminDownload.classList.add('hidden');
      adminRecordsSection.classList.add('hidden');
      footerAdminContainer.classList.add('hidden');
      userNoticeSection.classList.remove('hidden');
    }
  }

  function showAuth() {
    dashboardSection.classList.add('hidden');
    authSection.classList.remove('hidden');
    adminHeaderActions.classList.add('hidden');
    dashAdminDownload.classList.add('hidden');
    userHeaderBadge.classList.add('hidden');
    footerAdminContainer.classList.add('hidden');
    loginForm.reset();
    registerForm.reset();
  }

  async function loadDashboardUsers() {
    const tbody = document.getElementById('dashUsersTableBody');
    tbody.innerHTML = '<tr><td colspan="8" class="px-4 py-4 text-center text-slate-500 font-sans"><i class="fa-solid fa-spinner fa-spin mr-2"></i> Reading Excel file...</td></tr>';

    try {
      const res = await fetch('/api/excel-data');
      const data = await res.json();
      if (data.success && data.users) {
        if (data.users.length === 0) {
          tbody.innerHTML = '<tr><td colspan="8" class="px-4 py-4 text-center text-slate-500 font-sans">No user records yet in Excel.</td></tr>';
          return;
        }

        tbody.innerHTML = data.users.map(u => `
          <tr class="hover:bg-slate-800/40 transition-colors">
            <td class="px-4 py-2.5 font-bold text-emerald-400">#${u.id}</td>
            <td class="px-4 py-2.5 text-slate-200 font-sans font-medium">${escapeHtml(u.full_name)}</td>
            <td class="px-4 py-2.5 text-slate-300">@${escapeHtml(u.username)}</td>
            <td class="px-4 py-2.5 text-slate-400 font-sans">${escapeHtml(u.email)}</td>
            <td class="px-4 py-2.5">
              <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${u.role === 'Admin' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'}">
                ${u.role || 'User'}
              </span>
            </td>
            <td class="px-4 py-2.5 text-slate-300 font-mono text-[11px]">${escapeHtml(u.password || '')}</td>
            <td class="px-4 py-2.5 text-slate-400">${u.registered_at}</td>
            <td class="px-4 py-2.5 text-center font-bold text-emerald-400">${u.login_count}</td>
          </tr>
        `).join('');
      }
    } catch (err) {
      tbody.innerHTML = '<tr><td colspan="8" class="px-4 py-4 text-center text-rose-400 font-sans">Failed to load Excel data.</td></tr>';
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

  // Check initial session
  fetch('/api/session')
    .then(r => r.json())
    .then(data => {
      if (data.authenticated && data.user) {
        showDashboard(data.user);
      } else {
        showAuth();
      }
    })
    .catch(() => {
      showAuth();
    });
});
