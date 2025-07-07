/**
 * Enhanced WC Control System - Main JavaScript
 * Version 2.0 - Modern UI with real-time features
 */

// Global configuration
const CONFIG = {
    UPDATE_INTERVAL: 30000, // 30 seconds
    NOTIFICATION_DURATION: 5000, // 5 seconds
    RECONNECT_INTERVAL: 3000, // 3 seconds
    CHART_UPDATE_INTERVAL: 60000, // 1 minute
};

// Global state
let globalState = {
    isConnected: false,
    lastUpdateTime: Date.now(),
    notifications: [],
    theme: 'light'
};

// Utility Functions
const utils = {
    /**
     * Format timestamp to human readable format
     * @param {number} timestamp - Unix timestamp
     * @returns {string} Formatted date string
     */
    formatTimestamp(timestamp) {
        if (!timestamp) return 'Never';
        const date = new Date(timestamp * 1000);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },

    /**
     * Get relative time string
     * @param {number} timestamp - Unix timestamp
     * @returns {string} Relative time string
     */
    getRelativeTime(timestamp) {
        if (!timestamp) return 'Never';
        const now = Date.now();
        const diff = now - (timestamp * 1000);
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return `${Math.floor(diff / 86400000)} days ago`;
    },

    /**
     * Debounce function calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Generate unique ID
     * @returns {string} Unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    /**
     * Safe JSON parse
     * @param {string} str - JSON string
     * @returns {object|null} Parsed object or null
     */
    safeJsonParse(str) {
        try {
            return JSON.parse(str);
        } catch (e) {
            return null;
        }
    }
};

// Notification System
const NotificationManager = {
    notifications: new Map(),

    /**
     * Show notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds
     */
    show(message, type = 'info', duration = CONFIG.NOTIFICATION_DURATION) {
        const id = utils.generateId();
        const notification = this.create(id, message, type);
        
        document.body.appendChild(notification);
        this.notifications.set(id, notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(id);
            }, duration);
        }
        
        return id;
    },

    /**
     * Create notification element
     */
    create(id, message, type) {
        const notification = document.createElement('div');
        notification.id = `notification-${id}`;
        notification.className = `alert alert-${type} alert-dismissible fade position-fixed notification-toast`;
        notification.style.cssText = `
            top: 20px; 
            right: 20px; 
            z-index: 9999; 
            min-width: 320px; 
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
            border-radius: 8px;
        `;
        
        const icon = this.getIcon(type);
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${icon} me-2"></i>
                <span class="flex-grow-1">${message}</span>
                <button type="button" class="btn-close" onclick="NotificationManager.dismiss('${id}')"></button>
            </div>
        `;
        
        return notification;
    },

    /**
     * Get icon for notification type
     */
    getIcon(type) {
        const icons = {
            success: 'bi bi-check-circle-fill text-success',
            error: 'bi bi-x-circle-fill text-danger',
            warning: 'bi bi-exclamation-triangle-fill text-warning',
            info: 'bi bi-info-circle-fill text-info'
        };
        return icons[type] || icons.info;
    },

    /**
     * Dismiss notification
     */
    dismiss(id) {
        const notification = this.notifications.get(id);
        if (notification) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.notifications.delete(id);
            }, 150);
        }
    },

    /**
     * Clear all notifications
     */
    clearAll() {
        this.notifications.forEach((notification, id) => {
            this.dismiss(id);
        });
    }
};

// Theme Manager
const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('wc-theme') || 'light';
        this.setTheme(savedTheme);
        this.bindEvents();
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('wc-theme', theme);
        globalState.theme = theme;
        this.updateThemeIcon(theme);
    },

    updateThemeIcon(theme) {
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
        }
    },

    toggle() {
        const currentTheme = globalState.theme;
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        
        NotificationManager.show(
            `Switched to ${newTheme} theme`, 
            'info', 
            2000
        );
    },

    bindEvents() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggle());
        }
    }
};

// Connection Manager
const ConnectionManager = {
    status: 'disconnected',
    
    updateStatus(status) {
        this.status = status;
        const statusDot = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');
        
        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }
        
        if (statusText) {
            const statusMap = {
                online: 'Connected',
                offline: 'Disconnected', 
                connecting: 'Connecting...',
                error: 'Connection Error'
            };
            statusText.textContent = statusMap[status] || 'Unknown';
        }
        
        globalState.isConnected = status === 'online';
    }
};

// Time Manager
const TimeManager = {
    init() {
        this.updateCurrentTime();
        this.updateRelativeTimes();
        
        // Update current time every second
        setInterval(() => this.updateCurrentTime(), 1000);
        
        // Update relative times every 30 seconds
        setInterval(() => this.updateRelativeTimes(), 30000);
    },

    updateCurrentTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleTimeString();
        }
    },

    updateRelativeTimes() {
        document.querySelectorAll('[data-timestamp]').forEach(el => {
            const timestamp = parseFloat(el.dataset.timestamp);
            if (timestamp) {
                if (el.classList.contains('relative-time')) {
                    el.textContent = utils.getRelativeTime(timestamp);
                } else {
                    el.textContent = utils.formatTimestamp(timestamp);
                }
            }
        });
    }
};

// Performance Monitor
const PerformanceMonitor = {
    metrics: {
        pageLoadTime: 0,
        wsConnectTime: 0,
        lastUpdateTime: 0
    },

    init() {
        this.metrics.pageLoadTime = performance.now();
        console.log(`📊 Page loaded in ${this.metrics.pageLoadTime.toFixed(2)}ms`);
    },

    recordWSConnect() {
        this.metrics.wsConnectTime = performance.now() - this.metrics.pageLoadTime;
        console.log(`🔌 WebSocket connected in ${this.metrics.wsConnectTime.toFixed(2)}ms`);
    },

    recordUpdate() {
        this.metrics.lastUpdateTime = performance.now();
    }
};

// Enhanced Tooltip Manager
const TooltipManager = {
    init() {
        this.initializeTooltips();
        
        // Reinitialize tooltips when new content is added
        const observer = new MutationObserver(() => {
            this.initializeTooltips();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]:not([data-tooltip-initialized])')
        );
        
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
            tooltipTriggerEl.setAttribute('data-tooltip-initialized', 'true');
        });
    }
};

// Main Application Initialization
const App = {
    init() {
        console.log('🚀 WC Control System v2.0 Initializing...');
        PerformanceMonitor.init();
        
        // Initialize managers
        ThemeManager.init();
        TimeManager.init();
        TooltipManager.init();
        
        // Initialize features
        this.initializeFeatures();
        
        console.log('✅ WC Control System initialized successfully');
    },

    initializeFeatures() {
        // Add smooth scrolling
        document.documentElement.style.scrollBehavior = 'smooth';
        
        // Add loading states to forms
        this.enhanceForms();
        
        // Add keyboard shortcuts
        this.addKeyboardShortcuts();
        
        // Initialize progress indicators
        this.initializeProgressIndicators();
    },

    enhanceForms() {
        // Handle node control form with AJAX
        const nodeControlForm = document.getElementById('nodeControlForm');
        if (nodeControlForm) {
            nodeControlForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const submitBtn = e.submitter || e.target.querySelector('button[type="submit"]:focus');
                const nodeId = submitBtn?.value;
                const action = e.target.querySelector('input[name="action"]')?.value || 'flush';
                
                if (!nodeId) {
                    NotificationManager.show('error', 'No node selected');
                    return;
                }
                
                // Show loading state
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.disabled = true;
                    const originalHtml = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading-spinner"></span>';
                }
                
                try {
                    // Send AJAX request
                    const response = await fetch('/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: new URLSearchParams({
                            node_id: nodeId,
                            action: action
                        })
                    });
                    
                    if (response.ok) {
                        NotificationManager.show('success', `${action.toUpperCase()} command sent to ${nodeId}`);
                        
                        // Refresh dashboard data after 2 seconds
                        setTimeout(() => {
                            if (typeof refreshDashboard === 'function') {
                                refreshDashboard();
                            }
                        }, 2000);
                    } else {
                        NotificationManager.show('error', 'Failed to send command');
                    }
                } catch (error) {
                    console.error('Command error:', error);
                    NotificationManager.show('error', 'Network error occurred');
                } finally {
                    // Reset button state
                    if (submitBtn) {
                        submitBtn.classList.remove('loading');
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = '<img src="/static/button.png" alt="FLUSH">';
                    }
                }
            });
        }
        
        // Handle other forms with generic loading state
        document.querySelectorAll('form:not(#nodeControlForm)').forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.classList.add('loading');
                    submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
                }
            });
        });
    },

    addKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + R: Refresh dashboard
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                if (typeof refreshDashboard === 'function') {
                    e.preventDefault();
                    refreshDashboard();
                }
            }
            
            // Ctrl/Cmd + D: Toggle theme
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                ThemeManager.toggle();
            }
        });
    },

    initializeProgressIndicators() {
        // Add loading states for async operations
        window.showLoading = function(element) {
            if (element) {
                element.classList.add('loading');
            }
        };
        
        window.hideLoading = function(element) {
            if (element) {
                element.classList.remove('loading');
            }
        };
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    App.init();
});

// Export globals for use in other scripts
window.WCSystem = {
    utils,
    NotificationManager,
    ThemeManager,
    ConnectionManager,
    TimeManager,
    PerformanceMonitor,
    globalState
};

// Add global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    NotificationManager.show(
        'An unexpected error occurred. Please refresh the page.', 
        'error'
    );
});

// Add unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    NotificationManager.show(
        'A network error occurred. Please check your connection.', 
        'warning'
    );
});

console.log('📱 WC Control System - Main JavaScript loaded successfully');