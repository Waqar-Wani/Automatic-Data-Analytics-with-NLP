<?php
// SQLite connection for authentication
try {
    $pdo = new PDO('sqlite:' . __DIR__ . '/../auth.db');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die('Database connection failed: ' . $e->getMessage());
}
?> 