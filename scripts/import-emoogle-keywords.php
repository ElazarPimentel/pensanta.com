<?php
/**
 * Import Emoogle Keywords into Pensanta Emoji Database
 *
 * This script reads the emoogle-emoji-keywords.json file and adds
 * missing keywords to the existing database.
 *
 * Usage: php import-emoogle-keywords.php [--dry-run]
 */

$dryRun = in_array('--dry-run', $argv);

if ($dryRun) {
    echo "=== DRY RUN MODE (no changes will be made) ===\n\n";
}

// Database config
$config = [
    'host' => 'pensanta.com',
    'user' => 'u105991616_jskdfik47hjfhf',
    'pass' => 'yYyY6#3#emgGgG',
    'name' => 'u105991616_pensantasite'
];

// Load emoogle keywords
$jsonFile = __DIR__ . '/emoogle-emoji-keywords.json';
if (!file_exists($jsonFile)) {
    die("Error: emoogle-emoji-keywords.json not found\n");
}

$emoogleData = json_decode(file_get_contents($jsonFile), true);
if (!$emoogleData) {
    die("Error: Failed to parse JSON\n");
}

echo "Loaded " . count($emoogleData) . " emojis from Emoogle database\n\n";

// Connect to database
$conn = new mysqli($config['host'], $config['user'], $config['pass'], $config['name']);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error . "\n");
}
$conn->set_charset("utf8mb4");

// Get all emojis from database
$result = $conn->query("SELECT id, emojiChar FROM emojis");
$dbEmojis = [];
while ($row = $result->fetch_assoc()) {
    $dbEmojis[$row['emojiChar']] = $row['id'];
}
echo "Found " . count($dbEmojis) . " emojis in database\n\n";

// Get existing keywords
$result = $conn->query("SELECT emojiId, keyword FROM keywords");
$existingKeywords = [];
while ($row = $result->fetch_assoc()) {
    $key = $row['emojiId'] . '|' . strtolower($row['keyword']);
    $existingKeywords[$key] = true;
}
echo "Found " . count($existingKeywords) . " existing keywords\n\n";

// Prepare insert statement
$insertStmt = $conn->prepare("INSERT INTO keywords (emojiId, keyword) VALUES (?, ?)");

$stats = [
    'emojis_matched' => 0,
    'emojis_not_found' => 0,
    'keywords_added' => 0,
    'keywords_skipped' => 0
];

$notFoundEmojis = [];

foreach ($emoogleData as $emoji => $keywords) {
    // Skip the first keyword (it's usually the name/description)
    $keywordsToAdd = array_slice($keywords, 1);

    if (!isset($dbEmojis[$emoji])) {
        $stats['emojis_not_found']++;
        $notFoundEmojis[] = $emoji;
        continue;
    }

    $emojiId = $dbEmojis[$emoji];
    $stats['emojis_matched']++;

    foreach ($keywordsToAdd as $keyword) {
        $keyword = trim($keyword);
        if (empty($keyword)) continue;

        // Check if keyword already exists
        $key = $emojiId . '|' . strtolower($keyword);
        if (isset($existingKeywords[$key])) {
            $stats['keywords_skipped']++;
            continue;
        }

        // Add new keyword
        if (!$dryRun) {
            $insertStmt->bind_param("is", $emojiId, $keyword);
            $insertStmt->execute();
        }
        $stats['keywords_added']++;
        $existingKeywords[$key] = true; // Prevent duplicates in same run
    }
}

echo "=== RESULTS ===\n";
echo "Emojis matched: {$stats['emojis_matched']}\n";
echo "Emojis not found in DB: {$stats['emojis_not_found']}\n";
echo "New keywords added: {$stats['keywords_added']}\n";
echo "Keywords skipped (already exist): {$stats['keywords_skipped']}\n";

if ($stats['emojis_not_found'] > 0 && $stats['emojis_not_found'] <= 20) {
    echo "\nEmojis not found: " . implode(' ', $notFoundEmojis) . "\n";
}

$insertStmt->close();
$conn->close();

if ($dryRun) {
    echo "\n=== This was a DRY RUN. Run without --dry-run to apply changes ===\n";
}
