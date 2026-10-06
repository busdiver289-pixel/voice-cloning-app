:root {
  --primary: #7c9cff;
  --primary-dark: #5a7dff;
  --accent: #57d5c5;
  --danger: #ff7a90;
  --bg: #0b1020;
  --surface: #121a2d;
  --surface-alt: #1c2740;
  --text: #edf3ff;
  --muted: #a9b6d3;
  --border: rgba(255, 255, 255, 0.08);
  --shadow: 0 24px 60px rgba(9, 14, 29, 0.5);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  background: linear-gradient(135deg, #15213d 0%, var(--bg) 50%);
  color: var(--text);
  min-height: 100vh;
}

.app-container {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 240px;
  background: rgba(18, 26, 45, 0.95);
  border-right: 1px solid var(--border);
  padding: 24px 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.logo h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--primary);
}

.logo .tagline {
  margin: 4px 0 0 0;
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  padding: 12px 16px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
}

.nav-item.active {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
}

.page {
  display: none;
}

.page.active {
  display: block;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
}

.page-header p {
  margin: 0;
  color: var(--muted);
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.studio-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.studio-panel {
  background: rgba(18, 26, 45, 0.9);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.studio-panel h2 {
  margin: 0;
  font-size: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  color: var(--muted);
  font-weight: 500;
}

input[type="text"],
input[type="range"],
textarea {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text);
  font-family: inherit;
}

input[type="text"]:focus,
textarea:focus {
  outline: none;
  border-color: var(--primary);
  background: rgba(124, 156, 255, 0.1);
}

textarea {
  resize: vertical;
  min-height: 100px;
}

input[type="range"] {
  height: 6px;
  cursor: pointer;
}

.button-group {
  display: flex;
  gap: 12px;
}

.button-group.full-width {
  flex-direction: column;
}

.btn {
  padding: 12px 18px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
}

.btn-danger {
  background: rgba(255, 122, 144, 0.1);
  color: var(--danger);
  border: 1px solid rgba(255, 122, 144, 0.3);
}

.btn-danger:hover {
  background: rgba(255, 122, 144, 0.2);
}

.btn-upload {
  background: rgba(255, 255, 255, 0.04);
  color: var(--accent);
  border: 2px dashed var(--border);
  cursor: pointer;
}

.btn.full {
  flex: 1;
}

.btn.full-width {
  width: 100%;
}

.btn.hidden {
  display: none;
}

.audio-preview-box,
.profile-summary,
.status-panel,
.backend-info {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 12px;
}

#audioPreview {
  width: 100%;
  margin-top: 12px;
}

#audioPreview.hidden {
  display: none;
}

.profile-summary h3 {
  margin: 0 0 12px 0;
  font-size: 1rem;
}

.tag-list {
  list-style: none;
  padding: 0;
  margin: 0 0 12px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-list li {
  padding: 6px 12px;
  background: rgba(87, 213, 197, 0.12);
  color: var(--accent);
  border: 1px solid rgba(87, 213, 197, 0.25);
  border-radius: 20px;
  font-size: 0.85rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(255, 255, 255, 0.03);
  padding: 10px;
  border-radius: 8px;
}

.metric span {
  font-size: 0.8rem;
  color: var(--muted);
}

.metric strong {
  font-size: 1.1rem;
}

.controls-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.status-label {
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.status-panel p:last-child {
  margin: 0;
}

.backend-info small {
  display: block;
  color: var(--muted);
  margin-top: 8px;
}

.library-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.profile-card {
  background: rgba(18, 26, 45, 0.9);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-card h4 {
  margin: 0;
  font-size: 1.1rem;
}

.profile-card-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--muted);
}

.profile-card-actions {
  display: flex;
  gap: 8px;
}

.profile-card-actions .btn {
  flex: 1;
  padding: 8px 12px;
  font-size: 0.85rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: rgba(18, 26, 45, 0.9);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-item-content {
  flex: 1;
}

.history-item-text {
  margin: 0 0 8px 0;
  font-size: 0.95rem;
}

.history-item-meta {
  margin: 0;
  font-size: 0.85rem;
  color: var(--muted);
}

.history-item-actions {
  display: flex;
  gap: 8px;
}

.history-item-actions .btn {
  padding: 8px 12px;
  font-size: 0.85rem;
}

.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.setting-item {
  background: rgba(18, 26, 45, 0.9);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
}

.setting-item h3 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
}

.setting-item p {
  margin: 0;
  color: var(--muted);
}

.setting-item small {
  display: block;
  color: var(--muted);
  margin-top: 8px;
}

.hidden {
  display: none !important;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 200px;
  }

  .studio-grid {
    grid-template-columns: 1fr;
  }

  .controls-grid {
    grid-template-columns: 1fr;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border);
    flex-direction: row;
    gap: 16px;
    padding: 16px;
  }

  .nav-menu {
    flex-direction: row;
    flex: 1;
  }

  .main-content {
    padding: 20px;
  }

  .library-grid {
    grid-template-columns: 1fr;
  }
}
