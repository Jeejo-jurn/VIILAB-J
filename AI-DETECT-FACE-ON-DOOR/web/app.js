// ============================================================
// Frontend Logic — NIN-FACENet Dashboard
// ============================================================

function app() {
  return {
    // --- Auth ---
    token: null,
    loginPw: '',
    loginError: '',
    loginLoading: false,

    // --- Navigation ---
    tab: 'dashboard',
    navItems: [
      {
        id: 'dashboard', label: 'Dashboard',
        icon: '<svg style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/></svg>',
      },
      {
        id: 'monitor', label: 'Live Monitor',
        icon: '<svg style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M12 18.75H4.5a2.25 2.25 0 01-2.25-2.25V9m12.841 9.091L16.5 19.5m-1.409-1.409c.407-.393.819-.786 1.409-1.409"/></svg>',
      },
      {
        id: 'log', label: 'Access Log',
        icon: '<svg style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z"/></svg>',
      },
      {
        id: 'users', label: 'Users',
        icon: '<svg style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z"/></svg>',
      },
      {
        id: 'report', label: 'Admin Report',
        icon: '<svg style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z"/></svg>',
      },
    ],

    // --- State ---
    status: { engine: false, camera: false, fps: 0, uptime_seconds: 0, last_detection: { user: null, sim: 0 } },
    stats: { total_today: 0, spoof_today: 0 },
    history: [],
    users: [],
    events: [],
    newEventCount: 0,
    logFilter: '',
    logStatusFilter: '',
    historyLoading: false,
    logPollTimer: null,
    deleteModal: { show: false, name: '', loading: false },
    enrollModal: { show: false, name: '', files: [], previews: [], loading: false, error: '' },
    report: null,
    reportLoading: false,
    reportChart: null,
    reportExpandedUser: null,
    toast: { show: false, msg: '', type: 'success' },
    ws: null,
    statusTimer: null,
    currentDateStr: '',

    // --- Computed ---
    get filteredHistory() {
      return this.history.filter(r => {
        const nameMatch = !this.logFilter || (r.name || '').toLowerCase().includes(this.logFilter.toLowerCase());
        const statusMatch = !this.logStatusFilter || r.status === this.logStatusFilter;
        return nameMatch && statusMatch;
      });
    },

    // ============================================================
    // Lifecycle
    // ============================================================
    init() {
      this.currentDateStr = new Date().toLocaleString('th-TH', { dateStyle: 'long', timeStyle: 'short' });
      const saved = sessionStorage.getItem('nin_token');
      if (saved) { this.token = saved; this.onLogin(); }
    },

    // ============================================================
    // Navigation — auto-refresh ข้อมูลเมื่อเปลี่ยนแท็บ
    // ============================================================
    switchTab(id) {
      this.tab = id;

      // หยุด poll เดิมก่อนเสมอ
      clearInterval(this.logPollTimer);
      this.logPollTimer = null;

      if (id === 'log') {
        this.newEventCount = 0;
        this.loadHistory();                          // โหลดทันที
        // poll ทุก 3 วินาที ขณะอยู่ในหน้า log
        this.logPollTimer = setInterval(() => this.loadHistory(), 10000);
      }

      if (id === 'users') {
        this.loadUsers();
      }

      if (id === 'report') {
        this.loadReport();
      }
    },

    // ============================================================
    // Auth
    // ============================================================
    async doLogin() {
      this.loginError = '';
      this.loginLoading = true;
      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password: this.loginPw }),
        });
        if (!res.ok) { this.loginError = 'Incorrect password. Try again.'; return; }
        const data = await res.json();
        this.token = data.token;
        sessionStorage.setItem('nin_token', this.token);
        this.onLogin();
      } catch {
        this.loginError = 'Connection error. Is the server running?';
      } finally {
        this.loginLoading = false;
      }
    },

    onLogin() {
      this.loadStatus();
      this.loadHistory();
      this.loadUsers();
      this.connectWS();
      this.statusTimer = setInterval(() => this.loadStatus(), 5000);
    },

    async doLogout() {
      await fetch('/api/logout', { method: 'POST', headers: { 'X-TOKEN': this.token } }).catch(() => {});
      sessionStorage.removeItem('nin_token');
      this.token = null;
      if (this.ws) this.ws.close();
      clearInterval(this.statusTimer);
      clearInterval(this.logPollTimer);
    },

    // ============================================================
    // API Calls
    // ============================================================
    async loadStatus() {
      try {
        const r = await fetch('/api/status', { headers: { 'X-TOKEN': this.token } });
        if (r.status === 401) { this.doLogout(); return; }
        this.status = await r.json();
      } catch {}
    },

    async loadHistory(showFeedback = false) {
      this.historyLoading = true;
      try {
        const r = await fetch('/api/history', { headers: { 'X-TOKEN': this.token } });
        if (!r.ok) return;
        this.history = await r.json();
        // คำนวณสถิติวันนี้
        const today = new Date().toDateString();
        this.stats.total_today = this.history.filter(
          h => h.status === 'access_granted' && h.timestamp && new Date(h.timestamp).toDateString() === today
        ).length;
        this.stats.spoof_today = this.history.filter(
          h => h.status === 'spoof_attempt' && h.timestamp && new Date(h.timestamp).toDateString() === today
        ).length;
        if (showFeedback) this.showToast('Access log refreshed', 'success');
      } catch {
        if (showFeedback) this.showToast('Failed to load history', 'error');
      } finally {
        this.historyLoading = false;
      }
    },

    async loadUsers() {
      try {
        const r = await fetch('/api/users', { headers: { 'X-TOKEN': this.token } });
        if (!r.ok) return;
        this.users = await r.json();
      } catch {}
    },

    // ============================================================
    // WebSocket — real-time events
    // ============================================================
    connectWS() {
      try {
        const proto = location.protocol === 'https:' ? 'wss' : 'ws';
        this.ws = new WebSocket(`${proto}://${location.host}/ws/admin?token=${this.token}`);
        this.ws.onmessage = (e) => {
          try {
            const ev = JSON.parse(e.data);

            // 1. Live Events feed (ทุก tab)
            this.events.unshift(ev);
            if (this.events.length > 60) this.events.pop();

            // 2. Badge แจ้งเตือนถ้าไม่ได้อยู่ใน log tab
            if (this.tab !== 'log') {
              this.newEventCount = Math.min(this.newEventCount + 1, 99);
            }

            // 3. Prepend ลง Access Log ทันที — ไม่ต้องรอ DB
            const newRow = {
              id: `ws_${Date.now()}`,
              name: ev.name,
              status: ev.event,       // 'access_granted' | 'spoof_attempt'
              timestamp: new Date().toISOString(),
            };
            this.history.unshift(newRow);
            if (this.history.length > 100) this.history.pop();
            this._recalcStats();

          } catch {}
        };
        this.ws.onclose = (ev) => {
          // code 1008 = unauthorized (token invalid) — don't reconnect
          if (this.token && ev.code !== 1008) setTimeout(() => this.connectWS(), 3000);
        };
      } catch {}
    },

    _recalcStats() {
      const today = new Date().toDateString();
      this.stats.total_today = this.history.filter(
        h => h.status === 'access_granted' && h.timestamp && new Date(h.timestamp).toDateString() === today
      ).length;
      this.stats.spoof_today = this.history.filter(
        h => h.status === 'spoof_attempt' && h.timestamp && new Date(h.timestamp).toDateString() === today
      ).length;
    },

    // ============================================================
    // User Management
    // ============================================================
    confirmDelete(name) {
      this.deleteModal = { show: true, name, loading: false };
    },

    async doDelete() {
      this.deleteModal.loading = true;
      try {
        const r = await fetch(`/api/users/${encodeURIComponent(this.deleteModal.name)}`, {
          method: 'DELETE',
          headers: { 'X-TOKEN': this.token },
        });
        if (!r.ok) throw new Error();
        this.showToast(`${this.deleteModal.name} removed successfully`, 'success');
        this.deleteModal.show = false;
        await this.loadUsers();
      } catch {
        this.showToast('Failed to remove user', 'error');
        this.deleteModal.loading = false;
      }
    },

    openEnrollModal() {
      this.enrollModal = { show: true, name: '', files: [], previews: [], loading: false, error: '' };
    },

    onEnrollFiles(event) {
      const files = Array.from(event.target.files);
      this.enrollModal.files = files;
      this.enrollModal.previews = [];
      files.forEach(f => {
        const reader = new FileReader();
        reader.onload = (e) => this.enrollModal.previews.push(e.target.result);
        reader.readAsDataURL(f);
      });
    },

    async doEnroll() {
      const { name, files } = this.enrollModal;
      if (!name.trim()) { this.enrollModal.error = 'กรุณาใส่ชื่อ'; return; }
      if (files.length === 0) { this.enrollModal.error = 'กรุณาเลือกรูปอย่างน้อย 1 รูป'; return; }

      this.enrollModal.loading = true;
      this.enrollModal.error = '';

      try {
        // แปลงรูปทั้งหมดเป็น base64
        const images_b64 = await Promise.all(files.map(f => new Promise((res, rej) => {
          const reader = new FileReader();
          reader.onload = e => res(e.target.result.split(',')[1]); // ตัด "data:image/...;base64," ออก
          reader.onerror = rej;
          reader.readAsDataURL(f);
        })));

        const r = await fetch('/api/enroll', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-TOKEN': this.token },
          body: JSON.stringify({ username: name.trim(), images_b64 }),
        });

        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || 'Enroll failed');

        this.showToast(`${name} enrolled (${data.photos_saved} photos)`, 'success');
        this.enrollModal.show = false;
        await this.loadUsers();
      } catch (e) {
        this.enrollModal.error = e.message || 'เกิดข้อผิดพลาด ลองใหม่';
      } finally {
        this.enrollModal.loading = false;
      }
    },

    // ============================================================
    // Admin Report
    // ============================================================
    async loadReport() {
      this.reportLoading = true;
      try {
        const r = await fetch('/api/admin/report', { headers: { 'X-TOKEN': this.token } });
        if (!r.ok) throw new Error();
        this.report = await r.json();
        this.$nextTick(() => this.drawReportChart());
      } catch {
        this.showToast('Failed to load report', 'error');
      } finally {
        this.reportLoading = false;
      }
    },

    drawReportChart() {
      if (!this.report) return;
      const canvas = document.getElementById('reportChart');
      if (!canvas) return;

      if (this.reportChart) { this.reportChart.destroy(); this.reportChart = null; }

      const labels = this.report.class_distribution.map(c => c.name);
      const counts = this.report.class_distribution.map(c => c.count);
      const colors = labels.map(n => this.nameColor(n));

      this.reportChart = new Chart(canvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Photos per class',
            data: counts,
            backgroundColor: colors.map(c => c + 'cc'),
            borderColor: colors,
            borderWidth: 2,
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: 'Dataset Class Distribution', color: '#e2e8f0', font: { size: 14 } },
          },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
            y: { beginAtZero: true, ticks: { color: '#94a3b8', stepSize: 1 }, grid: { color: '#334155' } },
          },
        },
      });
    },

    toggleReportUser(name) {
      this.reportExpandedUser = this.reportExpandedUser === name ? null : name;
    },

    lightingBadge(label) {
      const map = { dark: 'bg-blue-900 text-blue-300', normal: 'bg-green-900 text-green-300', bright: 'bg-yellow-900 text-yellow-300' };
      return map[label] || 'bg-slate-700 text-slate-300';
    },

    qualityBadge(label) {
      return label === 'good' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300';
    },

    simColor(sim) {
      if (sim === null || sim === undefined) return '#64748b';
      if (sim >= 0.6) return '#22c55e';
      if (sim >= 0.4) return '#eab308';
      return '#ef4444';
    },

    // ============================================================
    // Helpers
    // ============================================================
    showToast(msg, type = 'success') {
      this.toast = { show: true, msg, type };
      setTimeout(() => { this.toast.show = false; }, 3500);
    },

    formatUptime(secs) {
      if (!secs) return '0s';
      const h = Math.floor(secs / 3600);
      const m = Math.floor((secs % 3600) / 60);
      const s = Math.floor(secs % 60);
      if (h > 0) return `${h}h ${m}m`;
      if (m > 0) return `${m}m ${s}s`;
      return `${s}s`;
    },

    formatDate(iso) {
      if (!iso) return '-';
      try { return new Date(iso).toLocaleString('th-TH', { dateStyle: 'short', timeStyle: 'medium', timeZone: 'Asia/Bangkok' }); }
      catch { return iso; }
    },

    nameColor(name) {
      const palette = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6'];
      if (!name) return palette[0];
      let h = 0;
      for (const c of name) h = (h * 31 + c.charCodeAt(0)) >>> 0;
      return palette[h % palette.length];
    },
  };
}
