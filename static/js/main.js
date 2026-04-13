/**
 * Pierre Hubertin Portfolio — Main JavaScript
 * Navbar, scroll animations, skill bars, contact form AJAX
 */

'use strict';

// ── Navbar scroll ────────────────────────────────────────────────────────────
const navbar = document.querySelector('.navbar');
const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.navbar-links');

if (navbar) {
  const handleScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
}

if (menuToggle && navLinks) {
  menuToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    menuToggle.classList.toggle('open', isOpen);
    menuToggle.setAttribute('aria-expanded', String(isOpen));
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close on link click
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      menuToggle.classList.remove('open');
      menuToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && navLinks.classList.contains('open')) {
      navLinks.classList.remove('open');
      menuToggle.classList.remove('open');
      document.body.style.overflow = '';
    }
  });
}

// ── Active nav link on scroll ────────────────────────────────────────────────
const sections = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.navbar-links a[href^="#"]');

const sectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      navAnchors.forEach(a => {
        a.classList.toggle('active', a.getAttribute('href') === `#${id}`);
      });
    }
  });
}, { rootMargin: '-40% 0px -55% 0px' });

sections.forEach(s => sectionObserver.observe(s));

// ── Scroll reveal ────────────────────────────────────────────────────────────
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ── Skill bars animate on scroll ─────────────────────────────────────────────
const skillObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const bars = entry.target.querySelectorAll('.skill-bar-fill');
      bars.forEach(bar => {
        const pct = bar.dataset.pct || '0';
        setTimeout(() => { bar.style.width = pct + '%'; }, 200);
      });
      skillObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });

document.querySelectorAll('.skill-category-card').forEach(card => {
  skillObserver.observe(card);
});

// ── Contact form AJAX ────────────────────────────────────────────────────────
const contactForm = document.getElementById('contact-form');

if (contactForm) {
  const submitBtn = contactForm.querySelector('[type="submit"]');
  const statusEl  = document.getElementById('form-status');

  const setStatus = (type, msg) => {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.className = `form-status ${type}`;
    statusEl.style.display = 'block';
    if (type === 'success') {
      setTimeout(() => { statusEl.style.display = 'none'; }, 6000);
    }
  };

  const clearErrors = () => {
    contactForm.querySelectorAll('.form-control').forEach(el => {
      el.classList.remove('is-invalid');
    });
    contactForm.querySelectorAll('.invalid-feedback').forEach(el => {
      el.textContent = '';
      el.style.display = 'none';
    });
  };

  const showErrors = (errors) => {
    Object.entries(errors).forEach(([field, msgs]) => {
      const input = contactForm.querySelector(`[name="${field}"]`);
      if (input) {
        input.classList.add('is-invalid');
        const feedback = input.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
          feedback.textContent = Array.isArray(msgs) ? msgs.join(' ') : msgs;
          feedback.style.display = 'block';
        }
      }
    });
  };

  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();

    if (statusEl) statusEl.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Envoi…';

    try {
      const formData = new FormData(contactForm);
      const response = await fetch('/contact/ajax/', {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });

      const data = await response.json();

      if (data.success) {
        setStatus('success', '✓ ' + data.message);
        contactForm.reset();
      } else {
        if (data.errors) showErrors(data.errors);
        setStatus('error', data.message || 'Veuillez corriger les erreurs ci-dessus.');
      }
    } catch (err) {
      console.error('Contact form error:', err);
      setStatus('error', 'Erreur réseau. Veuillez réessayer.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Envoyer le message';
    }
  });
}

// ── Auto-dismiss Django messages ──────────────────────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    alert.style.transition = 'opacity 0.5s';
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 500);
  }, 5000);
});

// ── Typing animation for hero (optional) ────────────────────────────────────
const typeTarget = document.querySelector('.hero-typed');
if (typeTarget) {
  const words = ['Data Analyst', 'Power BI Expert', 'SQL Architect', 'BI Consultant'];
  let wi = 0, ci = 0, deleting = false;
  const typeSpeed = 80, deleteSpeed = 50, pauseDelay = 2200;

  const type = () => {
    const word = words[wi];
    if (!deleting) {
      typeTarget.textContent = word.substring(0, ci + 1);
      ci++;
      if (ci === word.length) {
        deleting = true;
        setTimeout(type, pauseDelay);
        return;
      }
    } else {
      typeTarget.textContent = word.substring(0, ci - 1);
      ci--;
      if (ci === 0) {
        deleting = false;
        wi = (wi + 1) % words.length;
      }
    }
    setTimeout(type, deleting ? deleteSpeed : typeSpeed);
  };
  type();
}

// ── Smooth scroll for in-page anchors ────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
