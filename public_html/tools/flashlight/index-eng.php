<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="robots" content="index, follow">
    <meta name="theme-color" content="#ffffff">
    <title>White Screen Flashlight | Pensanta Tools</title>
    <meta name="description" content="White screen flashlight. Use your screen as a light source. Fullscreen available.">
    <meta name="keywords" content="flashlight, white screen, light, screen light, torch">
    <link rel="canonical" href="https://pensanta.com/tools/flashlight/index-eng.php">
    <link rel="alternate" hreflang="en" href="https://pensanta.com/tools/flashlight/index-eng.php">
    <link rel="alternate" hreflang="es" href="https://pensanta.com/tools/flashlight/">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        html, body {
            height: 100%;
            width: 100%;
            overflow: hidden;
        }
        body {
            background: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            font-family: system-ui, -apple-system, sans-serif;
        }
        .controls {
            display: flex;
            gap: 1rem;
            padding: 1.5rem;
            transition: opacity 0.3s;
        }
        .controls.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .btn {
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border: 2px solid #333;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            background: #fff;
            color: #333;
        }
        .btn:hover {
            background: #333;
            color: #fff;
        }
        .fullscreen-btn {
            background: #333;
            color: #fff;
        }
        .fullscreen-btn:hover {
            background: #000;
        }
        .tap-hint {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #ccc;
            font-size: 0.875rem;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }
        .tap-hint.visible {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="tap-hint" id="tapHint">Tap to show controls</div>

    <div class="controls" id="controls">
        <button class="btn fullscreen-btn" id="fullscreenBtn" onclick="toggleFullscreen()">
            Fullscreen
        </button>
        <a href="/tools/index-eng.php" class="btn">Back</a>
    </div>

    <script>
        const controls = document.getElementById('controls');
        const tapHint = document.getElementById('tapHint');
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        let hideTimeout;
        let isFullscreen = false;

        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().then(() => {
                    isFullscreen = true;
                    fullscreenBtn.textContent = 'Exit Fullscreen';
                    startHideTimer();
                }).catch(err => {
                    console.log('Fullscreen error:', err);
                });
            } else {
                document.exitFullscreen().then(() => {
                    isFullscreen = false;
                    fullscreenBtn.textContent = 'Fullscreen';
                    showControls();
                });
            }
        }

        function showControls() {
            controls.classList.remove('hidden');
            tapHint.classList.remove('visible');
            if (isFullscreen) {
                startHideTimer();
            }
        }

        function hideControls() {
            if (isFullscreen) {
                controls.classList.add('hidden');
                tapHint.classList.add('visible');
                setTimeout(() => {
                    tapHint.classList.remove('visible');
                }, 2000);
            }
        }

        function startHideTimer() {
            clearTimeout(hideTimeout);
            hideTimeout = setTimeout(hideControls, 3000);
        }

        document.body.addEventListener('click', (e) => {
            if (e.target === document.body || e.target === tapHint) {
                if (controls.classList.contains('hidden')) {
                    showControls();
                }
            }
        });

        document.addEventListener('fullscreenchange', () => {
            if (!document.fullscreenElement) {
                isFullscreen = false;
                fullscreenBtn.textContent = 'Fullscreen';
                showControls();
                clearTimeout(hideTimeout);
            }
        });

        // Prevent sleep on mobile
        let wakeLock = null;
        async function requestWakeLock() {
            try {
                if ('wakeLock' in navigator) {
                    wakeLock = await navigator.wakeLock.request('screen');
                }
            } catch (err) {
                console.log('Wake Lock error:', err);
            }
        }
        requestWakeLock();
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                requestWakeLock();
            }
        });
    </script>
</body>
</html>
