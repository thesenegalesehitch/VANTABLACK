// Vantablack Browser Fingerprinting Module V5
// Collects detailed browser information for advanced bot detection and targeting

(function(root) {
    const FingerprintCollector = {
        async collect() {
            const fp = {
                // Basic Info
                user_agent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language || navigator.userLanguage,
                languages: navigator.languages || [],
                timezone_offset: new Date().getTimezoneOffset(),
                
                // Screen & Window
                screen_width: window.screen.width,
                screen_height: window.screen.height,
                avail_width: window.screen.availWidth,
                avail_height: window.screen.availHeight,
                window_width: window.innerWidth,
                window_height: window.innerHeight,
                color_depth: window.screen.colorDepth,
                pixel_ratio: window.devicePixelRatio || 1,
                
                // Hardware
                hardware_concurrency: navigator.hardwareConcurrency || 'unknown',
                device_memory: navigator.deviceMemory || 'unknown',
                touch_support: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
                max_touch_points: navigator.maxTouchPoints || 0,
                
                // Bot Signals
                is_webdriver: navigator.webdriver || !!window.navigator.webdriver || !!document.documentElement.getAttribute('webdriver'),
                has_chrome: !!window.chrome,
                has_plugins: navigator.plugins.length > 0,
                
                // Advanced Fingerprints
                webgl_vendor: null,
                webgl_renderer: null,
                canvas_hash: null,
                audio_hash: null,
                fonts_detected: [],
                
                // Interaction
                mouse_movements: 0,
                scroll_events: 0,
                time_on_page: 0
            };

            // 0. Font Detection
            fp.fonts_detected = this.detectFonts();

            // 1. WebGL Fingerprinting
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        fp.webgl_vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                        fp.webgl_renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    }
                }
            } catch (e) { console.error('WebGL error', e); }

            // 2. Canvas Fingerprinting (Complex)
            try {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 200;
                canvas.height = 50;
                
                // Text with different fonts and blending
                ctx.textBaseline = "top";
                ctx.font = "14px 'Arial'";
                ctx.textBaseline = "alphabetic";
                ctx.fillStyle = "#f60";
                ctx.fillRect(125, 1, 62, 20);
                
                ctx.fillStyle = "#069";
                ctx.fillText("Vantablack V5", 2, 15);
                ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
                ctx.fillText("Vantablack V5", 4, 17);
                
                // Drawing shapes and winding rules
                ctx.strokeStyle = "orange";
                ctx.beginPath();
                ctx.arc(50, 50, 50, 0, Math.PI * 2, true);
                ctx.stroke();
                
                // Emoji (often rendered differently across platforms)
                ctx.font = "30px Arial";
                ctx.fillText("🛡️🔒", 100, 40);
                
                fp.canvas_hash = canvas.toDataURL().hashCode();
            } catch (e) { console.error('Canvas error', e); }

            // 3. Audio Context Fingerprinting
            try {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (AudioContext) {
                    const audioCtx = new AudioContext();
                    const oscillator = audioCtx.createOscillator();
                    const analyser = audioCtx.createAnalyser();
                    const gainNode = audioCtx.createGain();
                    const scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
                    
                    oscillator.type = 'triangle';
                    oscillator.frequency.value = 10000;
                    gainNode.gain.value = 0;
                    
                    oscillator.connect(analyser);
                    analyser.connect(scriptProcessor);
                    scriptProcessor.connect(audioCtx.destination);
                    
                    oscillator.start(0);
                    
                    // We need to wait for processing, but for synchronous collection we might skip detailed audio
                    // Or use an offline context if available
                    const OfflineAudioContext = window.OfflineAudioContext || window.webkitOfflineAudioContext;
                    if (OfflineAudioContext) {
                        const offlineCtx = new OfflineAudioContext(1, 44100, 44100);
                        const osc = offlineCtx.createOscillator();
                        osc.type = 'triangle';
                        osc.frequency.value = 10000;
                        const compressor = offlineCtx.createDynamicsCompressor();
                        
                        osc.connect(compressor);
                        compressor.connect(offlineCtx.destination);
                        
                        osc.start(0);
                        const renderBuffer = await offlineCtx.startRendering();
                        // Hash the buffer data
                        let sum = 0;
                        for (let i = 0; i < renderBuffer.length; i++) {
                            sum += renderBuffer.getChannelData(0)[i];
                        }
                        fp.audio_hash = sum.toString();
                    }
                }
            } catch (e) { console.error('Audio error', e); }
            
            return fp;
        },

        send(endpoint, data) {
            // Use Beacon API if available for reliability during unload/redirect
            if (navigator.sendBeacon) {
                const blob = new Blob([JSON.stringify(data)], {type: 'application/json'});
                navigator.sendBeacon(endpoint, blob);
            } else {
                return fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                    keepalive: true
                });
            }
        }
    };

    // Helper: String HashCode
    String.prototype.hashCode = function() {
        var hash = 0, i, chr;
        if (this.length === 0) return hash;
        for (i = 0; i < this.length; i++) {
            chr = this.charCodeAt(i);
            hash = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
        }
        return hash;
    };

    FingerprintCollector.detectFonts = function() {
        // Liste de fonts courantes à tester
        const baseFonts = ['monospace', 'sans-serif', 'serif'];
        const fontList = [
            'Arial', 'Arial Black', 'Calibri', 'Cambria', 'Comic Sans MS', 'Consolas', 
            'Courier', 'Courier New', 'Georgia', 'Helvetica', 'Impact', 'Lucida Console', 
            'Lucida Sans Unicode', 'Microsoft Sans Serif', 'Segoe UI', 'Tahoma', 
            'Times', 'Times New Roman', 'Trebuchet MS', 'Verdana'
        ];
        
        const detected = [];
        
        try {
            // Création d'un élément span caché pour mesurer la largeur
            const span = document.createElement("span");
            span.innerHTML = "mmmmmmmmmmlli";
            span.style.fontSize = "72px";
            span.style.position = "absolute";
            span.style.left = "-9999px";
            span.style.visibility = "hidden";
            document.body.appendChild(span);
            
            // Largeurs de base pour les familles génériques
            const baseWidths = {};
            for (const base of baseFonts) {
                span.style.fontFamily = base;
                baseWidths[base] = span.offsetWidth;
            }
            
            // Test de chaque font
            for (const font of fontList) {
                let detectedCount = 0;
                for (const base of baseFonts) {
                    span.style.fontFamily = `'${font}', ${base}`;
                    if (span.offsetWidth !== baseWidths[base]) {
                        detectedCount++;
                    }
                }
                // Si la largeur diffère d'au moins une base, la font est probablement présente
                if (detectedCount > 0) {
                    detected.push(font);
                }
            }
            
            document.body.removeChild(span);
        } catch (e) {
            console.error("Font detection error", e);
        }
        
        return detected;
    };

    // Expose to window
    root.FingerprintCollector = FingerprintCollector;

})(window);
