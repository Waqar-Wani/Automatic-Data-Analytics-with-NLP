<?php
require 'db.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $position = $_POST['position'] ?? '';
    $role = $_POST['role'] ?? 'user';

    // Validate fields
    $errors = [];
    if (!preg_match('/^[a-zA-Z0-9_]{3,}$/', $username)) $errors[] = 'Invalid username';
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) $errors[] = 'Invalid email';
    if (strlen($password) < 8) $errors[] = 'Password too short';
    if (!$position) $errors[] = 'Position required';
    if ($role === 'admin') {
        $stmt = $pdo->query("SELECT COUNT(*) FROM users WHERE role='admin'");
        if ($stmt->fetchColumn() >= 3) $errors[] = 'Admin limit reached';
    }
    // Check for existing username/email
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE username=? OR email=?");
    $stmt->execute([$username, $email]);
    if ($stmt->fetchColumn() > 0) $errors[] = 'Username or email already exists';

    if ($errors) {
        echo json_encode(['success'=>false, 'errors'=>$errors]);
        exit;
    }
    $hash = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $pdo->prepare("INSERT INTO users (username, password_hash, email, position, role) VALUES (?, ?, ?, ?, ?)");
    $stmt->execute([$username, $hash, $email, $position, $role]);
    echo json_encode(['success'=>true, 'message'=>'Registration successful']);
    exit;
}
?> 