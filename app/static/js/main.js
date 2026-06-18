// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255,255,255,0.12)';
        navbar.style.boxShadow = '0 20px 60px rgba(0,0,0,0.4)';
    } else {
        navbar.style.background = 'rgba(255,255,255,0.08)';
        navbar.style.boxShadow = '0 20px 60px rgba(0,0,0,0.3)';
    }
});

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe workshop cards
document.querySelectorAll('.workshop-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.animationDelay = `${index * 0.1}s`;
    observer.observe(card);
});

// Observe registrant cards
document.querySelectorAll('.registrant-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.animationDelay = `${index * 0.05}s`;
    observer.observe(card);
});

// Parallax effect for hero banner
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const heroBanner = document.querySelector('.hero-banner');
    if (heroBanner) {
        heroBanner.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Add loading animation to buttons (excluding submit buttons)
document.querySelectorAll('.btn:not([type="submit"])').forEach(btn => {
    btn.addEventListener('click', function(e) {
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        this.disabled = true;
        
        setTimeout(() => {
            this.innerHTML = originalText;
            this.disabled = false;
        }, 2000);
    });
});

// Typing effect for hero title (optional enhancement)
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.textContent = '';
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Counter animation for stats
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start);
        }
    }, 16);
}

// Trigger counter animation when stats are visible
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.num');
            statNumbers.forEach(stat => {
                const text = stat.textContent;
                if (!isNaN(text)) {
                    animateCounter(stat, parseInt(text));
                }
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const heroStats = document.querySelector('.hero-stats');
if (heroStats) {
    statsObserver.observe(heroStats);
}

// Add ripple effect to buttons
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;
        
        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Cookie/Notification dismiss
document.querySelectorAll('.flash-message').forEach(msg => {
    msg.addEventListener('click', function() {
        this.style.opacity = '0';
        this.style.transform = 'translateX(100%)';
        setTimeout(() => this.remove(), 300);
    });
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (msg.parentNode) {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            setTimeout(() => msg.remove(), 300);
        }
    }, 5000);
});

// Form validation enhancements
document.querySelectorAll('input[required]').forEach(input => {
    input.addEventListener('blur', function() {
        if (this.value.trim() === '') {
            this.style.borderColor = '#ef4444';
            this.style.boxShadow = '0 0 0 6px rgba(239, 68, 68, 0.15)';
        } else {
            this.style.borderColor = '#667eea';
            this.style.boxShadow = '0 0 0 6px rgba(102, 126, 234, 0.15)';
        }
    });
});

// Email validation
document.querySelectorAll('input[type="email"]').forEach(input => {
    input.addEventListener('blur', function() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (this.value && !emailRegex.test(this.value)) {
            this.style.borderColor = '#ef4444';
            this.style.boxShadow = '0 0 0 6px rgba(239, 68, 68, 0.15)';
        } else if (this.value) {
            this.style.borderColor = '#667eea';
            this.style.boxShadow = '0 0 0 6px rgba(102, 126, 234, 0.15)';
        }
    });
});

// Language persistence check
document.addEventListener('DOMContentLoaded', function() {
    const currentLang = document.documentElement.lang;
    console.log('Current language:', currentLang);
    
    // Ensure RTL styles are applied
    if (currentLang === 'ar') {
        document.body.style.direction = 'rtl';
        document.body.style.textAlign = 'right';
    }
});

// Keyboard navigation for modals
document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        const modal = document.querySelector('.modal-overlay.active');
        if (modal) {
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
});

// Performance optimization: Debounce scroll events
function debounce(func, wait = 20, immediate = true) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Apply debounce to scroll handlers
window.addEventListener('scroll', debounce(() => {
    // Scroll-based animations can be added here
}, 20));

// Add subtle tilt effect to workshop cards
document.querySelectorAll('.workshop-card').forEach(card => {
    card.addEventListener('mousemove', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-15px) scale(1.04)`;
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)';
    });
});

// Magnetic effect for buttons
document.querySelectorAll('.btn-primary, .register-btn').forEach(btn => {
    btn.addEventListener('mousemove', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        this.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
    });
    
    btn.addEventListener('mouseleave', function() {
        this.style.transform = 'translate(0, 0)';
    });
});

// Initialize animations on page load
window.addEventListener('load', () => {
    document.body.style.opacity = '1';
});

// Prevent flash of unstyled content
document.documentElement.style.visibility = 'visible';