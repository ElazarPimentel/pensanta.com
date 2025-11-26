<?php
/**
 * Emoji Grid - Public Interface
 * Frontend pagination with keyword search
 */

$config = require __DIR__ . '/config.php';

// Rate limiting for searches
function checkRateLimit($conn) {
    $ip = $_SERVER['REMOTE_ADDR'];
    $limit = 40; // searches per hour
    $window = 3600; // 1 hour in seconds

    // Clean old entries
    $conn->query("DELETE FROM rateLimit WHERE TIMESTAMPDIFF(SECOND, windowStart, NOW()) > $window");

    // Check current count
    $stmt = $conn->prepare("SELECT searchCount, windowStart FROM rateLimit WHERE ip = ?");
    $stmt->bind_param("s", $ip);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($row = $result->fetch_assoc()) {
        if ($row['searchCount'] >= $limit) {
            return false;
        }
        // Increment count
        $conn->query("UPDATE rateLimit SET searchCount = searchCount + 1 WHERE ip = '$ip'");
    } else {
        // First search from this IP
        $stmt = $conn->prepare("INSERT INTO rateLimit (ip, searchCount) VALUES (?, 1)");
        $stmt->bind_param("s", $ip);
        $stmt->execute();
    }

    return true;
}

// Load emojis data
$conn = new mysqli($config['dbHost'], $config['dbUser'], $config['dbPass'], $config['dbName']);
$conn->set_charset("utf8mb4");

// Get all visible emojis with their keywords
$query = "
    SELECT
        e.id,
        e.unicode,
        e.emojiChar,
        e.category,
        e.name,
        GROUP_CONCAT(k.keyword SEPARATOR '|') as keywords
    FROM vEmojis e
    LEFT JOIN keywords k ON e.id = k.emojiId
    GROUP BY e.id
    ORDER BY e.category, e.name
";

$result = $conn->query($query);
$emojis = [];
while ($row = $result->fetch_assoc()) {
    $emojis[] = [
        'id' => $row['id'],
        'char' => $row['emojiChar'],
        'name' => $row['name'],
        'category' => $row['category'],
        'keywords' => $row['keywords'] ? explode('|', $row['keywords']) : []
    ];
}

$conn->close();

// Output as JSON for JavaScript
$emojisJson = json_encode($emojis);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="theme-color" content="#000000">
    <title>Emoji Picker - Pensanta Tools</title>
    <meta name="description" content="Emoji picker with search and categorization">
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
        .emoji-tool-container {
            width: 100%;
        }

        .emoji-tool-container h1 {
            margin-bottom: var(--space-lg);
        }

        .search-container {
            margin-bottom: var(--space-lg);
        }

        #searchInput {
            width: 100%;
            padding: var(--space-md);
            font-size: var(--font-size-base);
            background: var(--color-surface);
            border: 1px solid var(--color-border-primary);
            border-radius: var(--radius-md);
            color: var(--color-text-primary);
        }

        #searchInput:focus {
            outline: none;
            border-color: var(--color-accent);
        }

        .hashtags {
            display: flex;
            flex-wrap: wrap;
            gap: var(--space-sm);
            margin-top: var(--space-md);
            min-height: 2rem;
        }

        .hashtag {
            background: var(--color-accent);
            color: var(--color-background);
            padding: var(--space-xs) var(--space-md);
            border-radius: var(--radius-full);
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            font-size: var(--font-size-sm);
            font-weight: 500;
        }

        .hashtag button {
            background: none;
            border: none;
            color: var(--color-background);
            cursor: pointer;
            font-size: 1.1rem;
            padding: 0;
            line-height: 1;
            font-weight: bold;
        }

        .hashtag button:hover {
            color: var(--color-text-primary);
        }

        .emoji-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: var(--space-sm);
            margin-bottom: var(--space-xl);
        }

        .emoji-btn {
            aspect-ratio: 1;
            background: var(--color-surface);
            border: 1px solid var(--color-border-primary);
            border-radius: var(--radius-md);
            font-size: 2rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .emoji-btn:hover {
            background: var(--color-surface-elevated);
            border-color: var(--color-accent);
            transform: scale(1.1);
        }

        .emoji-btn:active {
            transform: scale(0.95);
        }

        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: var(--space-lg);
            margin-top: var(--space-xl);
        }

        .pagination button {
            background: var(--color-surface);
            border: 1px solid var(--color-border-primary);
            color: var(--color-text-primary);
            padding: var(--space-sm) var(--space-lg);
            border-radius: var(--radius-md);
            cursor: pointer;
            font-size: var(--font-size-base);
        }

        .pagination button:hover:not(:disabled) {
            background: var(--color-surface-elevated);
            border-color: var(--color-accent);
        }

        .pagination button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }

        .page-info {
            font-size: var(--font-size-sm);
            color: var(--color-text-muted);
        }

        .toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: var(--color-success);
            color: var(--color-background);
            padding: var(--space-md) var(--space-xl);
            border-radius: var(--radius-md);
            font-weight: 500;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
            z-index: 1000;
        }

        .toast.show {
            opacity: 1;
        }

        .no-results {
            text-align: center;
            color: var(--color-text-muted);
            padding: var(--space-3xl) var(--space-lg);
            font-size: var(--font-size-lg);
        }

        @media (max-width: 768px) {
            .emoji-grid {
                grid-template-columns: repeat(4, 1fr);
            }

            .emoji-btn {
                font-size: 1.5rem;
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
                <p class="title-01">Emoji Picker</p>
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
            <div class="emoji-tool-container">
                <h1>Emoji Picker</h1>

                <div class="search-container">
                    <input
                        type="text"
                        id="searchInput"
                        placeholder="Type to search by keyword..."
                        autocomplete="off"
                    >
                    <div class="hashtags" id="hashtags"></div>
                </div>

                <div class="emoji-grid" id="emojiGrid"></div>

                <div class="pagination">
                    <button id="prevBtn" onclick="changePage(-1)">← Previous</button>
                    <span class="page-info" id="pageInfo"></span>
                    <button id="nextBtn" onclick="changePage(1)">Next →</button>
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

    <div class="toast" id="toast"></div>

    <script>
        const allEmojis = <?= $emojisJson ?>;
        const EMOJIS_PER_PAGE = 36; // 6x6 grid

        let currentPage = 1;
        let filteredEmojis = allEmojis;
        let activeKeywords = [];

        function renderEmojis() {
            const grid = document.getElementById('emojiGrid');
            const start = (currentPage - 1) * EMOJIS_PER_PAGE;
            const end = start + EMOJIS_PER_PAGE;
            const pageEmojis = filteredEmojis.slice(start, end);

            if (pageEmojis.length === 0) {
                grid.innerHTML = '<div class="no-results">No emojis found. Try different keywords.</div>';
            } else {
                grid.innerHTML = pageEmojis.map(emoji =>
                    `<button class="emoji-btn" onclick="copyEmoji('${emoji.char}')" title="${emoji.name}">
                        ${emoji.char}
                    </button>`
                ).join('');
            }

            updatePagination();
        }

        function updatePagination() {
            const totalPages = Math.ceil(filteredEmojis.length / EMOJIS_PER_PAGE);

            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = currentPage === totalPages || totalPages === 0;
            document.getElementById('pageInfo').textContent =
                totalPages === 0 ? '0 emojis' : `Page ${currentPage} of ${totalPages} (${filteredEmojis.length} emojis)`;
        }

        function changePage(delta) {
            const totalPages = Math.ceil(filteredEmojis.length / EMOJIS_PER_PAGE);
            const newPage = currentPage + delta;

            if (newPage >= 1 && newPage <= totalPages) {
                currentPage = newPage;
                renderEmojis();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }

        function addKeyword(keyword) {
            keyword = keyword.toLowerCase().trim();
            if (!keyword || activeKeywords.includes(keyword)) return;

            activeKeywords.push(keyword);
            renderHashtags();
            filterEmojis();
        }

        function removeKeyword(keyword) {
            activeKeywords = activeKeywords.filter(k => k !== keyword);
            renderHashtags();
            filterEmojis();
        }

        function renderHashtags() {
            const container = document.getElementById('hashtags');
            container.innerHTML = activeKeywords.map(keyword =>
                `<div class="hashtag">
                    #${keyword}
                    <button onclick="removeKeyword('${keyword}')">×</button>
                </div>`
            ).join('');
        }

        function filterEmojis() {
            if (activeKeywords.length === 0) {
                filteredEmojis = allEmojis;
            } else {
                // AND search: emoji must have ALL active keywords
                filteredEmojis = allEmojis.filter(emoji => {
                    return activeKeywords.every(keyword =>
                        emoji.keywords.some(k => k.toLowerCase().includes(keyword)) ||
                        emoji.name.toLowerCase().includes(keyword) ||
                        emoji.category.toLowerCase().includes(keyword)
                    );
                });
            }

            currentPage = 1;
            renderEmojis();
        }

        function copyEmoji(char) {
            navigator.clipboard.writeText(char).then(() => {
                showToast(`Copied ${char}`);
            }).catch(err => {
                showToast('Failed to copy');
            });
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');

            setTimeout(() => {
                toast.classList.remove('show');
            }, 2000);
        }

        // Search input handler
        let searchTimeout;
        document.getElementById('searchInput').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const value = e.target.value.trim();
                if (value) {
                    addKeyword(value);
                    e.target.value = '';
                }
            }, 500);
        });

        // Also add on Enter
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                clearTimeout(searchTimeout);
                const value = e.target.value.trim();
                if (value) {
                    addKeyword(value);
                    e.target.value = '';
                }
            }
        });

        // Initial render
        renderEmojis();
    </script>
</body>
</html>
