<?php
require 'db.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';
    $errors = [];
    if (!$username || !$password) $errors[] = 'Username and password required';
    if ($errors) {
        echo json_encode(['success'=>false, 'errors'=>$errors]);
        exit;
    }
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username=?");
    $stmt->execute([$username]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$user || !password_verify($password, $user['password_hash'])) {
        echo json_encode(['success'=>false, 'errors'=>['Invalid credentials']]);
        exit;
    }
    // Set session
    $_SESSION['user_id'] = $user['id'];
    $_SESSION['username'] = $user['username'];
    $_SESSION['role'] = $user['role'];
    // Update last_login
    $pdo->prepare("UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?")->execute([$user['id']]);
    echo json_encode(['success'=>true, 'message'=>'Login successful', 'role'=>$user['role']]);
    exit;
}
?> 