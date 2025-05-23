document.addEventListener('DOMContentLoaded', function() {
    // Placeholder for future interactivity (e.g., filtering, modals, dynamic loading)
    // Example: Highlight author cards on hover
    const cards = document.querySelectorAll('.author-card, .contributor-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => card.classList.add('highlight'));
        card.addEventListener('mouseleave', () => card.classList.remove('highlight'));
    });
}); 