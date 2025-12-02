// Theme switching functionality
document.addEventListener('DOMContentLoaded', function() {
  // Create theme toggle button
  const themeToggle = document.createElement('button');
  themeToggle.className = 'theme-toggle';
  themeToggle.innerHTML = '🌙';
  themeToggle.setAttribute('aria-label', 'Toggle dark mode');
  themeToggle.setAttribute('title', 'Toggle dark/light mode');
  document.body.appendChild(themeToggle);
  
  // Screen reader announcement function
  function announceToScreenReader(message, priority = 'polite') {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.classList.add('sr-only');
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }
  
  // Check for saved theme or prefer-color-scheme
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  const currentTheme = localStorage.getItem('theme');
  
  // Set initial theme
  if (currentTheme === 'dark' || (!currentTheme && prefersDarkScheme.matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.innerHTML = '☀️';
    themeToggle.setAttribute('aria-label', 'Switch to light mode');
    announceToScreenReader('Dark mode enabled');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
    themeToggle.innerHTML = '🌙';
    themeToggle.setAttribute('aria-label', 'Switch to dark mode');
  }
  
  // Toggle theme on button click
  themeToggle.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    
    if (currentTheme === 'light') {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
      themeToggle.innerHTML = '☀️';
      themeToggle.setAttribute('aria-label', 'Switch to light mode');
      announceToScreenReader('Dark mode enabled');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
      localStorage.setItem('theme', 'light');
      themeToggle.innerHTML = '🌙';
      themeToggle.setAttribute('aria-label', 'Switch to dark mode');
      announceToScreenReader('Light mode enabled');
    }
  });
  
  // Listen for system theme changes
  prefersDarkScheme.addEventListener('change', function(e) {
    if (!localStorage.getItem('theme')) {
      if (e.matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeToggle.innerHTML = '☀️';
        themeToggle.setAttribute('aria-label', 'Switch to light mode');
        announceToScreenReader('System dark mode detected, dark mode enabled');
      } else {
        document.documentElement.setAttribute('data-theme', 'light');
        themeToggle.innerHTML = '🌙';
        themeToggle.setAttribute('aria-label', 'Switch to dark mode');
        announceToScreenReader('System light mode detected, light mode enabled');
      }
    }
  });
  
  // Focus management for accessibility
  const mainContent = document.getElementById('main-content');
  if (mainContent) {
    // Make main content focusable for skip links
    mainContent.setAttribute('tabindex', '-1');
    
    // Auto-focus main content when it's the target of a skip link
    if (window.location.hash === '#main-content') {
      mainContent.focus();
    }
  }
  
  // Add keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    // Alt + T to toggle theme
    if (e.altKey && e.key === 't') {
      e.preventDefault();
      themeToggle.click();
    }
    
    // Alt + H to go home
    if (e.altKey && e.key === 'h') {
      const homeLink = document.querySelector('a[href="/"]');
      if (homeLink) {
        e.preventDefault();
        homeLink.focus();
        homeLink.click();
      }
    }
    
    // Alt + S to focus search (if available)
    if (e.altKey && e.key === 's') {
      const searchInput = document.querySelector('.search-input');
      if (searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    }
  });
  
  // Announce page load for screen readers
  const pageTitle = document.title || 'COVID Statistics Dashboard';
  announceToScreenReader(`${pageTitle} loaded`, 'assertive');
  
  // Add focus styles for keyboard navigation
  const allFocusableElements = document.querySelectorAll(
    'a, button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])'
  );
  
  allFocusableElements.forEach(element => {
    element.addEventListener('focus', function() {
      this.style.outline = '2px solid var(--link-color)';
      this.style.outlineOffset = '2px';
    });
    
    element.addEventListener('blur', function() {
      this.style.outline = '';
      this.style.outlineOffset = '';
    });
  });
  
  // Print functionality
  const printButtons = document.querySelectorAll('.print-btn');
  printButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      window.print();
      announceToScreenReader('Print dialog opened');
    });
  });
  
  // Auto-focus search input on search page
  const searchInput = document.querySelector('.search-input');
  if (searchInput && !searchInput.value) {
    searchInput.focus();
  }
  
  // Export confirmation
  const exportLinks = document.querySelectorAll('a[href*="/export/"]');
  exportLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const format = this.href.includes('/csv') ? 'CSV' : 'JSON';
      announceToScreenReader(`Downloading COVID data in ${format} format`);
    });
  });
});