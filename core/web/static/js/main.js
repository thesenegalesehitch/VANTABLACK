// Vantablack Core - Interface JavaScript

class VantablackUI {
    constructor() {
        this.currentPage = 'dashboard';
        this.systemInfo = null;
        this.init();
    }

    async init() {
        this.setupNavigation();
        this.loadSystemInfo();
        this.setupEventListeners();
        this.updateStatusIndicator();
        
        // Auto-refresh system info every 30 seconds
        setInterval(() => this.loadSystemInfo(), 30000);
    }

    setupNavigation() {
        // Highlight current page in navigation
        const links = document.querySelectorAll('.nav-link');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const page = link.getAttribute('data-page');
                this.setActivePage(page);
            });
        });

        // Handle browser navigation
        window.addEventListener('popstate', (e) => {
            this.handleRouteChange();
        });

        // Initial route handling
        this.handleRouteChange();
    }

    handleRouteChange() {
        const path = window.location.pathname;
        let page = 'dashboard';

        if (path.includes('/guides')) page = 'guides';
        else if (path.includes('/status')) page = 'status';
        else if (path.includes('/qr')) page = 'qr';
        else if (path.includes('/docs')) page = 'docs';

        this.setActivePage(page);
        const contentElement = document.getElementById('content');
        // If server already rendered the page, avoid reloading via AJAX
        if (!(contentElement && contentElement.dataset && contentElement.dataset.serverRendered === '1')) {
            this.loadPageContent(page);
        }
    }

    setActivePage(page) {
        this.currentPage = page;
        
        // Update navigation highlights
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === page) {
                link.classList.add('active');
            }
        });

        // Update browser history
        const url = page === 'dashboard' ? '/ui' : `/ui/${page}`;
        window.history.pushState({ page }, '', url);

        document.title = `${this.getPageTitle(page)} - Vantablack Core`;
    }

    getPageTitle(page) {
        const titles = {
            dashboard: 'Dashboard',
            guides: 'Guides d\'Installation',
            status: 'Statut Système',
            qr: 'Outils QR',
            docs: 'Documentation'
        };
        return titles[page] || 'Vantablack Core';
    }

    async loadPageContent(page) {
        const contentElement = document.getElementById('content');
        
        try {
            const response = await fetch(`/ui/api/content/${page}`);
            if (response.ok) {
                const html = await response.text();
                contentElement.innerHTML = html;
                this.initializePageComponents(page);
            } else {
                contentElement.innerHTML = this.getFallbackContent(page);
            }
        } catch (error) {
            console.error('Failed to load page content:', error);
            contentElement.innerHTML = this.getFallbackContent(page);
        }
    }

    initializePageComponents(page) {
        switch (page) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'guides':
                this.initGuides();
                break;
            case 'status':
                this.initStatus();
                break;
            case 'qr':
                this.initQRTools();
                break;
            case 'docs':
                this.initDocs();
                break;
        }
    }

    async loadSystemInfo() {
        try {
            const response = await fetch('/v5/config');
            if (response.ok) {
                this.systemInfo = await response.json();
                this.updateSystemInfoDisplay();
            }
        } catch (error) {
            console.error('Failed to load system info:', error);
        }

        try {
            const metricsResponse = await fetch('/v5/metrics');
            if (metricsResponse.ok) {
                const metricsText = await metricsResponse.text();
                this.updateMetricsDisplay(metricsText);
            }
        } catch (error) {
            console.error('Failed to load metrics:', error);
        }
    }

    updateSystemInfoDisplay() {
        const sysInfoElement = document.getElementById('sys-info');
        if (sysInfoElement && this.systemInfo) {
            sysInfoElement.textContent = 
                `v5.0 | ${navigator.platform} | ${new Date().toLocaleTimeString()}`;
        }
    }

    updateMetricsDisplay(metricsText) {
        // Parse and display Prometheus metrics
        const lines = metricsText.split('\n');
        const statusLines = lines.filter(line => 
            line.includes('vantablack_status') || line.includes('vantablack_requests_total')
        );

        // Update status indicator based on metrics
        const statusIndicator = document.getElementById('status-indicator');
        if (statusIndicator && statusLines.length > 0) {
            statusIndicator.textContent = 'Operational';
            statusIndicator.parentElement.className = 'bg-green-900 text-green-300 px-2 py-1 rounded text-sm';
        }
    }

    updateStatusIndicator() {
        // Check various system statuses and update indicator
        this.checkHealth().then(healthy => {
            const indicator = document.getElementById('status-indicator');
            if (indicator) {
                if (healthy) {
                    indicator.textContent = 'Operational';
                    indicator.parentElement.className = 'bg-green-900 text-green-300 px-2 py-1 rounded text-sm';
                } else {
                    indicator.textContent = 'Degraded';
                    indicator.parentElement.className = 'bg-yellow-900 text-yellow-300 px-2 py-1 rounded text-sm';
                }
            }
        });
    }

    async checkHealth() {
        try {
            const response = await fetch('/v5/health');
            return response.ok;
        } catch {
            return false;
        }
    }

    setupEventListeners() {
        // Global event listeners for interactive elements
        document.addEventListener('click', (e) => {
            // Handle copy-to-clipboard buttons
            if (e.target.classList.contains('copy-btn')) {
                this.copyToClipboard(e.target.getAttribute('data-copy'));
            }

            // Handle QR generation forms
            if (e.target.classList.contains('generate-qr-btn')) {
                this.handleQRGeneration(e);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.setActivePage('dashboard');
                        break;
                    case '2':
                        e.preventDefault();
                        this.setActivePage('guides');
                        break;
                    case '3':
                        e.preventDefault();
                        this.setActivePage('status');
                        break;
                    case '4':
                        e.preventDefault();
                        this.setActivePage('qr');
                        break;
                    case '5':
                        e.preventDefault();
                        this.setActivePage('docs');
                        break;
                }
            }
        });
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copié dans le presse-papiers!', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showToast('Échec de la copie', 'error');
        }
    }

    showToast(message, type = 'info') {
        // Create and show a toast notification
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-green-600' : 
            type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        } text-white z-50`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Page-specific initialization methods
    initDashboard() {
        // Initialize dashboard components
        this.loadRealTimeMetrics();
        this.setupDashboardCharts();
    }

    initGuides() {
        // Initialize guides page
        this.setupOSSelector();
    }

    initStatus() {
        // Initialize status page
        this.startStatusPolling();
    }

    initQRTools() {
        // Initialize QR tools page
        this.setupQRPreview();
    }

    initDocs() {
        // Initialize documentation page
        this.loadDocumentation();
    }

    // Fallback content for when API is unavailable
    getFallbackContent(page) {
        const contents = {
            dashboard: `
                <div class="text-center py-12">
                    <i class="fas fa-tachometer-alt text-6xl text-accent mb-4"></i>
                    <h2 class="text-2xl font-bold mb-4">Dashboard</h2>
                    <p class="text-gray-400">Interface de contrôle principal</p>
                </div>
            `,
            guides: `
                <div class="text-center py-12">
                    <i class="fas fa-book text-6xl text-accent mb-4"></i>
                    <h2 class="text-2xl font-bold mb-4">Guides d'Installation</h2>
                    <p class="text-gray-400">Guides multi-OS détaillés</p>
                </div>
            `,
            status: `
                <div class="text-center py-12">
                    <i class="fas fa-chart-bar text-6xl text-accent mb-4"></i>
                    <h2 class="text-2xl font-bold mb-4">Statut Système</h2>
                    <p class="text-gray-400">Monitoring en temps réel</p>
                </div>
            `,
            qr: `
                <div class="text-center py-12">
                    <i class="fas fa-qrcode text-6xl text-accent mb-4"></i>
                    <h2 class="text-2xl font-bold mb-4">Outils QR</h2>
                    <p class="text-gray-400">Génération et validation de QR codes</p>
                </div>
            `,
            docs: `
                <div class="text-center py-12">
                    <i class="fas fa-file-alt text-6xl text-accent mb-4"></i>
                    <h2 class="text-2xl font-bold mb-4">Documentation</h2>
                    <p class="text-gray-400">Documentation complète</p>
                </div>
            `
        };
        return contents[page] || '<div>Page non trouvée</div>';
    }

    // Additional utility methods
    async loadRealTimeMetrics() {
        // Load and display real-time metrics
    }

    setupDashboardCharts() {
        // Initialize charts for dashboard
    }

    setupOSSelector() {
        // Setup OS selection for guides
    }

    startStatusPolling() {
        // Start polling for system status
    }

    setupQRPreview() {
        // Setup QR code preview functionality
    }

    async loadDocumentation() {
        // Load documentation content
    }

    async handleQRGeneration(event) {
        // Handle QR code generation
        event.preventDefault();
        const form = event.target.closest('form');
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/ui/api/generate-qr', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showToast('QR code généré avec succès!', 'success');
                this.displayQRResult(result);
            } else {
                this.showToast('Erreur lors de la génération', 'error');
            }
        } catch (error) {
            console.error('QR generation failed:', error);
            this.showToast('Erreur de connexion', 'error');
        }
    }

    displayQRResult(result) {
        // Display generated QR code result
    }
}

// Initialize the UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VantablackUI();
});

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatTime(seconds) {
    if (seconds < 60) return seconds + 's';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm' + (seconds % 60) + 's';
    return Math.floor(seconds / 3600) + 'h' + Math.floor((seconds % 3600) / 60) + 'm';
}

// Export for global access
window.VantablackUI = VantablackUI;
