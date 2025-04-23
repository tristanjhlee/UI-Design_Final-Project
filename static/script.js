document.addEventListener('DOMContentLoaded', function() {
    console.log("Page Loaded");

    fetch('/log-page-enter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ page: window.location.pathname, timestamp: new Date().toISOString() })
    }).catch(error => console.error('Error logging page:', error));
});
