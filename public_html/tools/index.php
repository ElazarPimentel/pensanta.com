<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="theme-color" content="#000000">
    <title>Tools - Pensanta</title>
    <meta name="description" content="Herramientas útiles: IP Address y Password Generator">
    <meta name="author" content="Pensanta">

    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" href="/favicon.png">

    <!-- CSS -->
    <link rel="stylesheet" href="/css/styles.css">
    <link rel="preload" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'">
    <noscript>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    </noscript>

    <style>
        .tool-section {
            margin-bottom: var(--space-2xl);
            padding: var(--space-xl);
            background: var(--color-surface);
            border: 1px solid var(--color-border-primary);
            border-radius: var(--radius-lg);
        }

        .tool-section h2 {
            margin-top: 0;
            color: var(--color-accent);
        }

        .ip-display {
            font-size: var(--font-size-2xl);
            font-family: var(--font-family-mono);
            color: var(--color-text-primary);
            padding: var(--space-lg);
            background: var(--color-surface-elevated);
            border: 2px solid var(--color-border-secondary);
            border-radius: var(--radius-md);
            text-align: center;
            margin: var(--space-lg) 0;
        }

        .ip-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--space-lg);
            margin: var(--space-lg) 0;
        }

        .ip-box {
            display: flex;
            flex-direction: column;
            gap: var(--space-sm);
        }

        .ip-label {
            font-size: var(--font-size-sm);
            color: var(--color-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        .ip-value {
            font-size: var(--font-size-lg);
            font-family: var(--font-family-mono);
            color: var(--color-text-primary);
            padding: var(--space-md);
            background: var(--color-surface-elevated);
            border: 2px solid var(--color-border-secondary);
            border-radius: var(--radius-md);
            text-align: center;
            width: 100%;
            cursor: text;
            transition: all var(--transition-normal);
        }

        .ip-value:focus {
            outline: none;
            border-color: var(--color-accent);
            box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.2);
        }

        .ip-value::selection {
            background-color: var(--color-accent);
            color: var(--color-background);
        }

        .ip-value.unavailable {
            color: var(--color-text-muted);
            font-family: var(--font-family-primary);
            font-size: var(--font-size-sm);
            cursor: default;
        }

        @media (max-width: 768px) {
            .ip-grid {
                grid-template-columns: 1fr;
            }
        }

        .password-controls {
            display: flex;
            flex-direction: column;
            gap: var(--space-lg);
            margin: var(--space-lg) 0;
        }

        .control-group {
            display: flex;
            flex-direction: column;
            gap: var(--space-sm);
        }

        .control-group label {
            color: var(--color-text-secondary);
            font-weight: 500;
        }

        .control-group select {
            padding: var(--space-sm) var(--space-md);
            background: var(--color-surface-elevated);
            color: var(--color-text-primary);
            border: 2px solid var(--color-border-primary);
            border-radius: var(--radius-md);
            font-size: var(--font-size-base);
            cursor: pointer;
        }

        .control-group select:focus {
            outline: none;
            border-color: var(--color-accent);
        }

        .checkbox-group {
            display: flex;
            gap: var(--space-xl);
            flex-wrap: wrap;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: var(--space-sm);
        }

        .checkbox-item input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: var(--color-accent);
        }

        .checkbox-item label {
            color: var(--color-text-secondary);
            cursor: pointer;
        }

        .generate-btn {
            padding: var(--space-md) var(--space-xl);
            background: var(--color-accent);
            color: var(--color-text-primary);
            border: none;
            border-radius: var(--radius-lg);
            font-size: var(--font-size-lg);
            font-weight: 600;
            cursor: pointer;
            transition: all var(--transition-normal);
        }

        .generate-btn:hover {
            background: var(--color-accent-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 158, 255, 0.4);
        }

        .generate-btn:active {
            transform: translateY(0);
        }

        .password-output {
            display: flex;
            align-items: center;
            gap: var(--space-md);
            margin-top: var(--space-lg);
        }

        .password-display {
            flex: 1;
            font-size: var(--font-size-xl);
            font-family: var(--font-family-mono);
            color: var(--color-text-primary);
            padding: var(--space-lg);
            background: var(--color-surface-elevated);
            border: 2px solid var(--color-border-secondary);
            border-radius: var(--radius-md);
            word-break: break-all;
            min-height: 3rem;
        }

        .copy-btn {
            padding: var(--space-md) var(--space-lg);
            background: var(--color-surface-elevated);
            color: var(--color-text-secondary);
            border: 2px solid var(--color-border-primary);
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all var(--transition-normal);
            white-space: nowrap;
        }

        .copy-btn:hover {
            background: var(--color-hover-bg);
            border-color: var(--color-accent);
            color: var(--color-accent);
        }

        .copy-btn.copied {
            background: var(--color-success);
            border-color: var(--color-success);
            color: var(--color-background);
        }

        @media (max-width: 768px) {
            .password-output {
                flex-direction: column;
            }

            .copy-btn {
                width: 100%;
            }
        }
    </style>
</head>

<body>
    <!-- Skip to main content for accessibility -->
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <header class="container-main border-01" role="banner">
        <div id="header-container">
            <div id="logo-left">
                <a href="/index.html" aria-label="Ir a inicio">
                    <h2 class="logo-text">Pensanta</h2>
                </a>
            </div>
            <div id="text-right">
                <p class="title-01">Tools</p>
            </div>
            <nav class="language-switcher" role="navigation" aria-label="Selector de idioma">
                <a href="/index-eng.html" class="lang-button" lang="en" aria-label="Cambiar a inglés">EN</a>
            </nav>
        </div>
    </header>

    <main id="main-content" class="container-main border-01" role="main">
        <section class="section-top">
            <nav role="navigation" aria-label="Navegación principal">
                <a href="/index.html" class="nav-link"><span>Home</span></a>
                <a href="/es/portfolio/" class="nav-link"><span>Portfolio</span></a>
                <a href="/about.html" class="nav-link"><span>Acerca de</span></a>
                <a href="/tools/" class="nav-link active"><span>Tools</span></a>
            </nav>
        </section>

        <section class="section-middle">
            <h1>Herramientas</h1>

            <!-- IP Address Section -->
            <div class="tool-section">
                <h2>Tu Dirección IP</h2>
                <p>Tus direcciones IP públicas:</p>
                <?php
                $clientIP = trim($_SERVER['REMOTE_ADDR']);
                $isIPv6 = strpos($clientIP, ':') !== false;
                ?>
                <div class="ip-grid">
                    <div class="ip-box">
                        <div class="ip-label">IPv4</div>
                        <input type="text" class="ip-value" id="ipv4" readonly
                               value="<?php echo $isIPv6 ? 'Detectando...' : htmlspecialchars($clientIP); ?>"
                               onclick="this.select()">
                    </div>
                    <div class="ip-box">
                        <div class="ip-label">IPv6</div>
                        <input type="text" class="ip-value" id="ipv6" readonly
                               value="<?php echo $isIPv6 ? htmlspecialchars($clientIP) : 'Detectando...'; ?>"
                               onclick="this.select()">
                    </div>
                </div>
            </div>

            <!-- Password Generator Section -->
            <div class="tool-section">
                <h2>Generador de Contraseñas</h2>
                <p>Genera contraseñas seguras y personalizadas.</p>

                <div class="password-controls">
                    <div class="control-group">
                        <label for="length">Longitud de la contraseña:</label>
                        <select id="length" name="length">
                            <option value="8">8 caracteres</option>
                            <option value="12" selected>12 caracteres</option>
                            <option value="16">16 caracteres</option>
                            <option value="24">24 caracteres</option>
                            <option value="32">32 caracteres</option>
                        </select>
                    </div>

                    <div class="control-group">
                        <label>Opciones:</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="noSala" name="noSala">
                                <label for="noSala">No SALA (sin 0, o, 1, l, L)</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="symbols" name="symbols" checked>
                                <label for="symbols">Símbolos (al menos 3)</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="urlFriendly" name="urlFriendly">
                                <label for="urlFriendly">URL friendly (A-Z, a-z, 0-9, - _ . ~)</label>
                            </div>
                        </div>
                    </div>

                    <button class="generate-btn" onclick="generatePassword()">
                        Generar Contraseña
                    </button>
                </div>

                <div class="password-output">
                    <div class="password-display" id="passwordDisplay">
                        Haz clic en "Generar Contraseña"
                    </div>
                    <button class="copy-btn" id="copyBtn" onclick="copyPassword()" disabled>
                        Copiar
                    </button>
                </div>
            </div>

            <!-- Text Cleaner Section -->
            <div class="tool-section">
                <h2>Limpiador de Texto</h2>
                <p>Elimina caracteres de formato: * # ` y reemplaza — por -</p>

                <div class="password-controls">
                    <div class="control-group">
                        <label for="textInput">Texto (máx. 2000 caracteres):</label>
                        <textarea id="textInput" maxlength="2000" rows="6"
                            style="width:100%; padding:var(--space-md); background:var(--color-surface-elevated);
                            color:var(--color-text-primary); border:2px solid var(--color-border-primary);
                            border-radius:var(--radius-md); font-family:var(--font-family-primary);
                            font-size:var(--font-size-base); resize:vertical;"
                            placeholder="Pega tu texto aquí..."></textarea>
                        <small id="charCount" style="color:var(--color-text-muted);">0 / 2000</small>
                    </div>

                    <button class="generate-btn" onclick="cleanText()">
                        Limpiar Texto
                    </button>
                </div>

                <div class="password-output">
                    <div class="password-display" id="cleanedText" style="white-space:pre-wrap;">
                        El texto limpio aparecerá aquí
                    </div>
                    <button class="copy-btn" id="copyCleanBtn" onclick="copyCleanedText()" disabled>
                        Copiar
                    </button>
                </div>
            </div>
        </section>

        <section class="section-bottom" aria-labelledby="contact-heading">
            <h2 id="contact-heading" class="visually-hidden">Contacto</h2>
            <div class="contact-links">
                <a href="mailto:elazar.pimentel@pensanta.com" aria-label="Envíanos un email"
                    class="contact-link email-link">
                    <i class="fas fa-envelope" aria-hidden="true"></i>
                    <span class="contact-text">Email</span>
                </a>
                <a href="https://wa.me/5491137990312" target="_blank" rel="noopener noreferrer"
                    aria-label="Contáctanos por WhatsApp" class="contact-link whatsapp-link">
                    <i class="fab fa-whatsapp" aria-hidden="true"></i>
                    <span class="contact-text">WhatsApp</span>
                </a>
            </div>
        </section>
    </main>

    <footer class="container-main border-01" role="contentinfo">
        <p>&copy; 2024 Pensanta.com - Todos los derechos reservados.</p>
        <small>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
            <span>Digitally carved by <a href="https://elazarpimentel.com" target="_blank" aria-label="Visit Elazar Pimentel's website">ElazarPimentel.com</a></span>
        </small>
    </footer>

    <script>
        // Fetch IP addresses (enhancement - keeps PHP fallback if fails)
        async function fetchIPAddresses() {
            const ipv4El = document.getElementById('ipv4');
            const ipv6El = document.getElementById('ipv6');

            // Only fetch IPv4 if currently showing "Detectando..."
            if (ipv4El.value.trim() === 'Detectando...') {
                try {
                    const response4 = await fetch('https://api.ipify.org?format=json');
                    const data4 = await response4.json();
                    ipv4El.value = data4.ip.trim();
                } catch (error) {
                    // Keep "Detectando..." if API fails and we have no PHP value
                    ipv4El.value = 'No disponible';
                    ipv4El.classList.add('unavailable');
                }
            }

            // Only fetch IPv6 if currently showing "Detectando..."
            if (ipv6El.value.trim() === 'Detectando...') {
                try {
                    const response6 = await fetch('https://api64.ipify.org?format=json');
                    const data6 = await response6.json();

                    // Check if it's actually IPv6
                    if (data6.ip.includes(':')) {
                        ipv6El.value = data6.ip.trim();
                    } else {
                        ipv6El.value = 'No disponible';
                        ipv6El.classList.add('unavailable');
                    }
                } catch (error) {
                    // Keep "Detectando..." if API fails
                    ipv6El.value = 'No disponible';
                    ipv6El.classList.add('unavailable');
                }
            }
        }

        function generatePassword() {
            const length = parseInt(document.getElementById('length').value);
            const noSala = document.getElementById('noSala').checked;
            const useSymbols = document.getElementById('symbols').checked;
            const urlFriendly = document.getElementById('urlFriendly').checked;

            // Character sets
            let uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            let lowercase = 'abcdefghijklmnopqrstuvwxyz';
            let numbers = '0123456789';
            const safeSymbols = '!@#$%^&*-_=+';
            const urlSafeSymbols = '-_.~';

            // Remove SALA characters if requested
            if (noSala) {
                uppercase = uppercase.replace(/[OL]/g, '');
                lowercase = lowercase.replace(/[ol]/g, '');
                numbers = numbers.replace(/[01]/g, '');
            }

            let allChars = uppercase + lowercase + numbers;

            // URL friendly overrides symbols - only use URL-safe chars
            if (urlFriendly) {
                allChars += urlSafeSymbols;
            } else if (useSymbols) {
                allChars += safeSymbols;
            }

            // Generate password
            let password = '';
            const array = new Uint32Array(length);
            crypto.getRandomValues(array);

            for (let i = 0; i < length; i++) {
                password += allChars[array[i] % allChars.length];
            }

            // If symbols required and not URL friendly, ensure at least 3 symbols
            if (useSymbols && !urlFriendly) {
                let symbolCount = (password.match(/[!@#$%^&*\-_=+]/g) || []).length;

                while (symbolCount < 3) {
                    const randomPos = Math.floor(Math.random() * password.length);
                    const randomSymbol = safeSymbols[Math.floor(Math.random() * safeSymbols.length)];
                    password = password.substring(0, randomPos) + randomSymbol + password.substring(randomPos + 1);
                    symbolCount++;
                }
            }

            // Display password
            document.getElementById('passwordDisplay').textContent = password;
            document.getElementById('copyBtn').disabled = false;
            document.getElementById('copyBtn').classList.remove('copied');
            document.getElementById('copyBtn').textContent = 'Copiar';
        }

        function copyPassword() {
            const password = document.getElementById('passwordDisplay').textContent;

            if (password && password !== 'Haz clic en "Generar Contraseña"') {
                navigator.clipboard.writeText(password).then(() => {
                    const btn = document.getElementById('copyBtn');
                    btn.classList.add('copied');
                    btn.textContent = '✓ Copiado';

                    setTimeout(() => {
                        btn.classList.remove('copied');
                        btn.textContent = 'Copiar';
                    }, 2000);
                }).catch(err => {
                    alert('Error al copiar: ' + err);
                });
            }
        }

        // Text Cleaner functions
        function cleanText() {
            const input = document.getElementById('textInput').value;
            let cleaned = input
                .replace(/[*#`]/g, '')
                .replace(/—/g, '-');

            document.getElementById('cleanedText').textContent = cleaned;
            document.getElementById('copyCleanBtn').disabled = false;
            document.getElementById('copyCleanBtn').classList.remove('copied');
            document.getElementById('copyCleanBtn').textContent = 'Copiar';
        }

        function copyCleanedText() {
            const text = document.getElementById('cleanedText').textContent;

            if (text && text !== 'El texto limpio aparecerá aquí') {
                navigator.clipboard.writeText(text).then(() => {
                    const btn = document.getElementById('copyCleanBtn');
                    btn.classList.add('copied');
                    btn.textContent = '✓ Copiado';

                    setTimeout(() => {
                        btn.classList.remove('copied');
                        btn.textContent = 'Copiar';
                    }, 2000);
                }).catch(err => {
                    alert('Error al copiar: ' + err);
                });
            }
        }

        // Initialize on page load
        window.addEventListener('DOMContentLoaded', () => {
            fetchIPAddresses();
            generatePassword();

            // Character counter for text cleaner
            document.getElementById('textInput').addEventListener('input', function() {
                document.getElementById('charCount').textContent = this.value.length + ' / 2000';
            });
        });
    </script>
</body>

</html>
