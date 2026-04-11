<?php
/**
 * Stores a study payload and returns a token for result.html (get.php).
 * Allows results: [] when the calculator returns no compliant options (e.g. small rooms).
 */
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON body']);
    exit;
}

if (!isset($data['sides']) || !is_array($data['sides']) || count($data['sides']) !== 4) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields: sides (array of 4 numbers)']);
    exit;
}
foreach ($data['sides'] as $s) {
    if (!is_numeric($s) || (float) $s <= 0) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing required fields: sides must be positive numbers']);
        exit;
    }
}

if (!isset($data['height']) || !is_numeric($data['height']) || (float) $data['height'] <= 0) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields: height']);
    exit;
}

if (!array_key_exists('results', $data) || !is_array($data['results'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields: results (array, may be empty)']);
    exit;
}

$token = bin2hex(random_bytes(16));
$dir = __DIR__ . '/data/studies';
if (!is_dir($dir) && !mkdir($dir, 0755, true)) {
    http_response_code(500);
    echo json_encode(['error' => 'Could not create storage directory']);
    exit;
}

$record = [
    'token' => $token,
    'saved_at' => gmdate('c'),
    'payload' => $data,
];

$path = $dir . '/' . $token . '.json';
if (file_put_contents($path, json_encode($record, JSON_UNESCAPED_UNICODE)) === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Could not save study']);
    exit;
}

echo json_encode(['status' => 'success', 'token' => $token], JSON_UNESCAPED_UNICODE);
