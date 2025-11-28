<?php
/**
 * Emoji Admin Interface
 * Manage keywords and emoji visibility
 */

session_start();

$config = require __DIR__ . '/config.php';

// Handle login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['password'])) {
    if ($_POST['password'] === $config['adminPassword']) {
        $_SESSION['emoji_admin'] = true;
        header('Location: admincocalola.php');
        exit;
    } else {
        $loginError = 'Invalid password';
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: admincocalola.php');
    exit;
}

// Check if logged in
$isLoggedIn = isset($_SESSION['emoji_admin']) && $_SESSION['emoji_admin'] === true;

// Load emojis if logged in
$emojis = [];
if ($isLoggedIn) {
    $conn = new mysqli($config['dbHost'], $config['dbUser'], $config['dbPass'], $config['dbName']);
    $conn->set_charset("utf8mb4");

    $result = $conn->query("
        SELECT id, unicode, emojiChar, category, name, dontShow
        FROM emojis
        ORDER BY category, name
    ");

    while ($row = $result->fetch_assoc()) {
        $emojis[] = $row;
    }

    $conn->close();
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="theme-color" content="#000000">
    <title>Emoji Admin - Pensanta</title>
    <meta name="description" content="Emoji management admin panel">
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

        body {
            min-height: 100vh;
        }

        .login-container {
            max-width: 400px;
            margin: 4rem auto;
            padding: var(--space-2xl);
            background: var(--color-surface);
            border: 1px solid var(--color-border-primary);
            border-radius: var(--radius-lg);
        }

        .login-container h1 {
            margin-bottom: var(--space-xl);
            font-size: var(--font-size-2xl);
        }

        .login-container input {
            width: 100%;
            padding: var(--space-md);
            margin-bottom: var(--space-lg);
            background: var(--color-surface-elevated);
            border: 1px solid var(--color-border-primary);
            border-radius: var(--radius-md);
            color: var(--color-text-primary);
            font-size: var(--font-size-base);
        }

        .login-container button {
            width: 100%;
            padding: var(--space-md);
            background: var(--color-accent);
            border: none;
            border-radius: var(--radius-md);
            color: var(--color-background);
            font-size: var(--font-size-base);
            font-weight: 600;
            cursor: pointer;
        }

        .login-container button:hover {
            background: var(--color-accent-hover);
        }

        .error {
            color: var(--color-error);
            margin-bottom: var(--space-lg);
            font-size: var(--font-size-sm);
        }

        .admin-header {
            max-width: 1200px;
            margin: 0 auto 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .admin-header h1 {
            font-size: 1.5rem;
        }

        .logout-btn {
            background: #222;
            border: 1px solid #404040;
            color: #fff;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.875rem;
        }

        .logout-btn:hover {
            background: #333;
        }

        .search-box {
            max-width: 1200px;
            margin: 0 auto 1.5rem;
        }

        .search-box input {
            width: 100%;
            padding: 0.75rem;
            background: #222;
            border: 1px solid #404040;
            border-radius: 0.5rem;
            color: #fff;
            font-size: 1rem;
        }

        .emoji-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 0.5rem;
        }

        .emoji-item {
            aspect-ratio: 1;
            background: #222;
            border: 2px solid #404040;
            border-radius: 0.5rem;
            font-size: 2.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            transition: all 0.2s;
        }

        .emoji-item:hover {
            background: #333;
            border-color: #4a9eff;
            transform: scale(1.05);
        }

        .emoji-item.hidden {
            opacity: 0.3;
            border-color: #ff5722;
        }

        .emoji-item.has-keywords::after {
            content: '';
            position: absolute;
            top: 4px;
            right: 4px;
            width: 6px;
            height: 6px;
            background: #00d084;
            border-radius: 50%;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            overflow-y: auto;
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: #111;
            border: 1px solid #404040;
            border-radius: 0.5rem;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .modal-header h2 {
            font-size: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .modal-header .emoji-large {
            font-size: 3rem;
        }

        .close-btn {
            background: none;
            border: none;
            color: #fff;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            width: 2rem;
            height: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .close-btn:hover {
            color: #ff5722;
        }

        .keyword-input-container {
            position: relative;
            margin-bottom: 1.5rem;
        }

        .keyword-input {
            width: 100%;
            padding: 0.75rem;
            background: #222;
            border: 1px solid #404040;
            border-radius: 0.5rem;
            color: #fff;
            font-size: 1rem;
        }

        .keyword-input:focus {
            outline: none;
            border-color: #4a9eff;
        }

        .autocomplete-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #222;
            border: 1px solid #404040;
            border-radius: 0.5rem;
            margin-top: 0.25rem;
            max-height: 200px;
            overflow-y: auto;
            z-index: 10;
            display: none;
        }

        .autocomplete-dropdown.show {
            display: block;
        }

        .autocomplete-item {
            padding: 0.75rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .autocomplete-item:hover {
            background: #333;
        }

        .autocomplete-count {
            color: #a0a0a0;
            font-size: 0.875rem;
        }

        .keywords-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }

        .keyword-tag {
            background: #4a9eff;
            color: #000;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
        }

        .keyword-tag button {
            background: none;
            border: none;
            color: #000;
            cursor: pointer;
            font-size: 1.1rem;
            padding: 0;
            line-height: 1;
            font-weight: bold;
        }

        .keyword-tag button:hover {
            color: #fff;
        }

        .visibility-toggle {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem;
            background: #222;
            border-radius: 0.5rem;
        }

        .visibility-toggle input[type="checkbox"] {
            width: 1.25rem;
            height: 1.25rem;
            cursor: pointer;
        }

        .toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: #00d084;
            color: #000;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 500;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
            z-index: 2000;
        }

        .toast.show {
            opacity: 1;
        }

        .toast.error {
            background: #ff5722;
            color: #fff;
        }
    </style>
</head>
<body>
    <?php if (!$isLoggedIn): ?>
        <div class="login-container">
            <h1>Emoji Admin</h1>
            <?php if (isset($loginError)): ?>
                <div class="error"><?= htmlspecialchars($loginError) ?></div>
            <?php endif; ?>
            <form method="POST">
                <input
                    type="password"
                    name="password"
                    placeholder="Enter admin password"
                    required
                    autofocus
                >
                <button type="submit">Login</button>
            </form>
        </div>
    <?php else: ?>
        <div class="admin-header">
            <h1>Emoji Admin</h1>
            <a href="?logout" class="logout-btn">Logout</a>
        </div>

        <div class="search-box">
            <input
                type="text"
                id="filterInput"
                placeholder="Filter emojis by name or category..."
            >
        </div>

        <div class="emoji-grid" id="emojiGrid">
            <?php foreach ($emojis as $emoji): ?>
                <div
                    class="emoji-item <?= $emoji['dontShow'] ? 'hidden' : '' ?>"
                    onclick="openModal(<?= $emoji['id'] ?>, '<?= htmlspecialchars($emoji['emojiChar']) ?>', '<?= htmlspecialchars($emoji['name']) ?>', <?= $emoji['dontShow'] ? 'true' : 'false' ?>)"
                    data-name="<?= strtolower($emoji['name']) ?>"
                    data-category="<?= strtolower($emoji['category']) ?>"
                    title="<?= htmlspecialchars($emoji['name']) ?>"
                >
                    <?= $emoji['emojiChar'] ?>
                </div>
            <?php endforeach; ?>
        </div>

        <div class="modal" id="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>
                        <span class="emoji-large" id="modalEmoji"></span>
                        <span id="modalName"></span>
                    </h2>
                    <button class="close-btn" onclick="closeModal()">×</button>
                </div>

                <div class="keyword-input-container">
                    <input
                        type="text"
                        id="keywordInput"
                        class="keyword-input"
                        placeholder="Type to add keyword..."
                        autocomplete="off"
                    >
                    <div class="autocomplete-dropdown" id="autocompleteDropdown"></div>
                </div>

                <div class="keywords-list" id="keywordsList"></div>

                <div class="visibility-toggle">
                    <input type="checkbox" id="dontShowCheckbox" onchange="toggleVisibility()">
                    <label for="dontShowCheckbox">Hide this emoji from public view</label>
                </div>
            </div>
        </div>

        <div class="toast" id="toast"></div>

        <script>
            let currentEmojiId = null;
            let currentKeywords = [];

            // Filter emojis
            document.getElementById('filterInput').addEventListener('input', (e) => {
                const filter = e.target.value.toLowerCase();
                const items = document.querySelectorAll('.emoji-item');

                items.forEach(item => {
                    const name = item.dataset.name;
                    const category = item.dataset.category;
                    const matches = name.includes(filter) || category.includes(filter);
                    item.style.display = matches ? 'flex' : 'none';
                });
            });

            async function openModal(id, char, name, dontShow) {
                currentEmojiId = id;
                document.getElementById('modalEmoji').textContent = char;
                document.getElementById('modalName').textContent = name;
                document.getElementById('dontShowCheckbox').checked = dontShow;
                document.getElementById('modal').classList.add('show');

                // Load keywords
                await loadKeywords();

                // Focus input
                document.getElementById('keywordInput').focus();
            }

            function closeModal() {
                document.getElementById('modal').classList.remove('show');
                document.getElementById('keywordInput').value = '';
                document.getElementById('autocompleteDropdown').classList.remove('show');
                currentEmojiId = null;
                currentKeywords = [];
            }

            async function loadKeywords() {
                const response = await fetch(`api.php?action=get_emoji_keywords&emoji_id=${currentEmojiId}`);
                const keywords = await response.json();
                currentKeywords = keywords;
                renderKeywords();
            }

            function renderKeywords() {
                const container = document.getElementById('keywordsList');
                if (currentKeywords.length === 0) {
                    container.innerHTML = '<div style="color: #a0a0a0; font-size: 0.875rem;">No keywords yet. Add some above!</div>';
                } else {
                    container.innerHTML = currentKeywords.map(keyword =>
                        `<div class="keyword-tag">
                            #${keyword}
                            <button onclick="removeKeyword('${keyword.replace(/'/g, "\\'")}')">×</button>
                        </div>`
                    ).join('');
                }

                // Update visual indicator
                updateEmojiIndicator();
            }

            function updateEmojiIndicator() {
                const emojiElements = document.querySelectorAll('.emoji-item');
                emojiElements.forEach(el => {
                    if (el.textContent.trim() === document.getElementById('modalEmoji').textContent) {
                        if (currentKeywords.length > 0) {
                            el.classList.add('has-keywords');
                        } else {
                            el.classList.remove('has-keywords');
                        }
                    }
                });
            }

            async function addKeyword(keyword) {
                keyword = keyword.trim().toLowerCase();
                if (!keyword) return;

                if (currentKeywords.includes(keyword)) {
                    showToast(`"${keyword}" already exists`, 'error');
                    return;
                }

                const response = await fetch('api.php?action=add_keyword', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ emoji_id: currentEmojiId, keyword })
                });

                const result = await response.json();

                if (result.success) {
                    currentKeywords.push(keyword);
                    renderKeywords();
                    showToast(`Added #${keyword}`);
                    document.getElementById('keywordInput').value = '';
                } else {
                    showToast(result.error || 'Failed to add keyword', 'error');
                }
            }

            async function removeKeyword(keyword) {
                const response = await fetch('api.php?action=remove_keyword', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ emoji_id: currentEmojiId, keyword })
                });

                const result = await response.json();

                if (result.success) {
                    currentKeywords = currentKeywords.filter(k => k !== keyword);
                    renderKeywords();
                    showToast(`Removed #${keyword}`);
                } else {
                    showToast(result.error || 'Failed to remove keyword', 'error');
                }
            }

            async function toggleVisibility() {
                const response = await fetch('api.php?action=toggle_visibility', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ emoji_id: currentEmojiId })
                });

                const result = await response.json();

                if (result.success) {
                    // Update grid item
                    const emojiElements = document.querySelectorAll('.emoji-item');
                    emojiElements.forEach(el => {
                        if (el.textContent.trim() === document.getElementById('modalEmoji').textContent) {
                            if (result.dontShow) {
                                el.classList.add('hidden');
                            } else {
                                el.classList.remove('hidden');
                            }
                        }
                    });
                    showToast(result.dontShow ? 'Emoji hidden' : 'Emoji visible');
                } else {
                    showToast(result.error || 'Failed to update visibility', 'error');
                }
            }

            // Autocomplete functionality
            let autocompleteTimeout;
            document.getElementById('keywordInput').addEventListener('input', async (e) => {
                const query = e.target.value.trim();

                if (query.length < 1) {
                    document.getElementById('autocompleteDropdown').classList.remove('show');
                    return;
                }

                clearTimeout(autocompleteTimeout);
                autocompleteTimeout = setTimeout(async () => {
                    const response = await fetch(`api.php?action=autocomplete&q=${encodeURIComponent(query)}`);
                    const suggestions = await response.json();

                    const dropdown = document.getElementById('autocompleteDropdown');

                    if (suggestions.length > 0) {
                        dropdown.innerHTML = suggestions.map(s =>
                            `<div class="autocomplete-item" onclick="selectAutocomplete('${s.keyword.replace(/'/g, "\\'")}')">
                                <span>${s.keyword}</span>
                                <span class="autocomplete-count">${s.count} emoji${s.count !== 1 ? 's' : ''}</span>
                            </div>`
                        ).join('');
                        dropdown.classList.add('show');
                    } else {
                        dropdown.classList.remove('show');
                    }
                }, 300);
            });

            function selectAutocomplete(keyword) {
                document.getElementById('keywordInput').value = keyword;
                document.getElementById('autocompleteDropdown').classList.remove('show');
                document.getElementById('keywordInput').focus();
            }

            // Add keyword on Enter
            document.getElementById('keywordInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const value = e.target.value.trim();
                    if (value) {
                        addKeyword(value);
                        document.getElementById('autocompleteDropdown').classList.remove('show');
                    }
                }
            });

            // Close autocomplete when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.keyword-input-container')) {
                    document.getElementById('autocompleteDropdown').classList.remove('show');
                }
            });

            // Close modal on escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    closeModal();
                }
            });

            function showToast(message, type = 'success') {
                const toast = document.getElementById('toast');
                toast.textContent = message;
                toast.className = 'toast show' + (type === 'error' ? ' error' : '');

                setTimeout(() => {
                    toast.classList.remove('show');
                }, 2500);
            }
        </script>
    <?php endif; ?>
</body>
</html>
