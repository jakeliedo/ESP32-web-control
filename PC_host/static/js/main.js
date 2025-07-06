// Main JavaScript file for the WC Control System

// Helper function to format timestamps
function formatTimestamp(timestamp) {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

// Helper function to update timestamps periodically
function updateRelativeTimes() {
    document.querySelectorAll('[data-timestamp]').forEach(el => {
        const timestamp = parseFloat(el.dataset.timestamp);
        el.textContent = formatTimestamp(timestamp);
    });
}

// Update timestamps every minute
setInterval(updateRelativeTimes, 60000);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Format timestamps on load
    updateRelativeTimes();
    
    // Add tooltip initialization if using Bootstrap tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
});