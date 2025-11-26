<?php
/**
 * Emoji API Endpoints
 * Handles autocomplete and keyword management
 */

session_start();

$config = require __DIR__ . '/config.php';
$conn = new mysqli($config['dbHost'], $config['dbUser'], $config['dbPass'], $config['dbName']);
$conn->set_charset("utf8mb4");

header('Content-Type: application/json');

// Check if user is admin
function isAdmin() {
    return isset($_SESSION['emoji_admin']) && $_SESSION['emoji_admin'] === true;
}

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'autocomplete':
        // Get keyword suggestions with usage counts
        $query = $_GET['q'] ?? '';
        $query = $conn->real_escape_string($query);

        $sql = "
            SELECT keyword, COUNT(*) as usage_count
            FROM keywords
            WHERE keyword LIKE '%$query%'
            GROUP BY keyword
            ORDER BY usage_count DESC, keyword ASC
            LIMIT 10
        ";

        $result = $conn->query($sql);
        $suggestions = [];

        while ($row = $result->fetch_assoc()) {
            $suggestions[] = [
                'keyword' => $row['keyword'],
                'count' => (int)$row['usage_count']
            ];
        }

        echo json_encode($suggestions);
        break;

    case 'get_emoji_keywords':
        // Get keywords for a specific emoji
        if (!isAdmin()) {
            http_response_code(403);
            echo json_encode(['error' => 'Unauthorized']);
            exit;
        }

        $emojiId = (int)($_GET['emoji_id'] ?? 0);

        $stmt = $conn->prepare("SELECT keyword FROM keywords WHERE emojiId = ? ORDER BY keyword");
        $stmt->bind_param("i", $emojiId);
        $stmt->execute();
        $result = $stmt->get_result();

        $keywords = [];
        while ($row = $result->fetch_assoc()) {
            $keywords[] = $row['keyword'];
        }

        echo json_encode($keywords);
        break;

    case 'add_keyword':
        // Add keyword to emoji
        if (!isAdmin()) {
            http_response_code(403);
            echo json_encode(['error' => 'Unauthorized']);
            exit;
        }

        $data = json_decode(file_get_contents('php://input'), true);
        $emojiId = (int)($data['emoji_id'] ?? 0);
        $keyword = trim($data['keyword'] ?? '');

        if (!$emojiId || !$keyword) {
            echo json_encode(['error' => 'Invalid input']);
            exit;
        }

        // Check if already exists
        $stmt = $conn->prepare("SELECT id FROM keywords WHERE emojiId = ? AND keyword = ?");
        $stmt->bind_param("is", $emojiId, $keyword);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            echo json_encode(['error' => 'Keyword already exists for this emoji']);
            exit;
        }

        // Insert new keyword
        $stmt = $conn->prepare("INSERT INTO keywords (emojiId, keyword) VALUES (?, ?)");
        $stmt->bind_param("is", $emojiId, $keyword);

        if ($stmt->execute()) {
            echo json_encode(['success' => true]);
        } else {
            echo json_encode(['error' => 'Failed to add keyword']);
        }
        break;

    case 'remove_keyword':
        // Remove keyword from emoji
        if (!isAdmin()) {
            http_response_code(403);
            echo json_encode(['error' => 'Unauthorized']);
            exit;
        }

        $data = json_decode(file_get_contents('php://input'), true);
        $emojiId = (int)($data['emoji_id'] ?? 0);
        $keyword = trim($data['keyword'] ?? '');

        if (!$emojiId || !$keyword) {
            echo json_encode(['error' => 'Invalid input']);
            exit;
        }

        $stmt = $conn->prepare("DELETE FROM keywords WHERE emojiId = ? AND keyword = ?");
        $stmt->bind_param("is", $emojiId, $keyword);

        if ($stmt->execute()) {
            echo json_encode(['success' => true]);
        } else {
            echo json_encode(['error' => 'Failed to remove keyword']);
        }
        break;

    case 'toggle_visibility':
        // Toggle dontShow flag for emoji
        if (!isAdmin()) {
            http_response_code(403);
            echo json_encode(['error' => 'Unauthorized']);
            exit;
        }

        $data = json_decode(file_get_contents('php://input'), true);
        $emojiId = (int)($data['emoji_id'] ?? 0);

        if (!$emojiId) {
            echo json_encode(['error' => 'Invalid input']);
            exit;
        }

        $stmt = $conn->prepare("UPDATE emojis SET dontShow = NOT dontShow WHERE id = ?");
        $stmt->bind_param("i", $emojiId);

        if ($stmt->execute()) {
            // Get new status
            $stmt = $conn->prepare("SELECT dontShow FROM emojis WHERE id = ?");
            $stmt->bind_param("i", $emojiId);
            $stmt->execute();
            $result = $stmt->get_result();
            $row = $result->fetch_assoc();

            echo json_encode([
                'success' => true,
                'dontShow' => (bool)$row['dontShow']
            ]);
        } else {
            echo json_encode(['error' => 'Failed to update visibility']);
        }
        break;

    default:
        http_response_code(400);
        echo json_encode(['error' => 'Invalid action']);
}

$conn->close();
