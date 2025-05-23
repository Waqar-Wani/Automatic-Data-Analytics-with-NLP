document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-review-form');
    const reviewsList = document.querySelector('.reviews-list');
    const leftArrow = document.querySelector('.carousel-arrow.left');
    const rightArrow = document.querySelector('.carousel-arrow.right');
    let allReviews = [];
    let startIdx = 0;
    const VISIBLE_COUNT = 3;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            rating: parseInt(formData.get('rating'), 10),
            review: formData.get('review')
        };
        fetch('/user-reviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                form.reset();
                loadReviews();
            } else {
                alert(result.error || 'Failed to submit review.');
            }
        })
        .catch(() => alert('Failed to submit review.'));
    });

    function renderVisibleReviews() {
        reviewsList.innerHTML = '';
        const visible = allReviews.slice(startIdx, startIdx + VISIBLE_COUNT);
        visible.forEach(review => {
            const card = document.createElement('div');
            card.className = 'review-card';
            card.innerHTML = `
                <div class="review-header">
                    <span class="review-name">${review.Name}</span>
                    <span class="review-rating">${'★'.repeat(review.Rating)}${'☆'.repeat(5 - review.Rating)}</span>
                </div>
                <div class="review-text">${review.Review}</div>
            `;
            reviewsList.appendChild(card);
        });
        // Disable arrows at ends
        if (leftArrow) leftArrow.disabled = startIdx === 0;
        if (rightArrow) rightArrow.disabled = (startIdx + VISIBLE_COUNT) >= allReviews.length;
    }

    function loadReviews() {
        fetch('/user-reviews')
            .then(res => res.text())
            .then(html => {
                // Parse the returned HTML and extract all reviews from the reviews-list section
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const reviewCards = doc.querySelectorAll('.reviews-list .review-card');
                allReviews = Array.from(reviewCards).map(card => ({
                    Name: card.querySelector('.review-name').textContent,
                    Rating: card.querySelector('.review-rating').textContent.replace(/[^★]/g, '').length,
                    Review: card.querySelector('.review-text').textContent
                }));
                startIdx = 0;
                renderVisibleReviews();
            });
    }

    if (leftArrow) {
        leftArrow.addEventListener('click', function() {
            if (startIdx > 0) {
                startIdx--;
                renderVisibleReviews();
            }
        });
    }
    if (rightArrow) {
        rightArrow.addEventListener('click', function() {
            if ((startIdx + VISIBLE_COUNT) < allReviews.length) {
                startIdx++;
                renderVisibleReviews();
            }
        });
    }

    // If reviewsList exists but not in add-review context, initialize carousel for index page
    if (reviewsList && !form) {
        // Collect reviews from static HTML for index page
        allReviews = Array.from(reviewsList.querySelectorAll('.review-card')).map(card => ({
            Name: card.querySelector('.review-name').textContent,
            Rating: card.querySelector('.review-rating').textContent.replace(/[^★]/g, '').length,
            Review: card.querySelector('.review-text').textContent
        }));
        renderVisibleReviews();
    }

    // Star rating interactivity
    const stars = document.querySelectorAll('#star-rating .star');
    const ratingInput = document.getElementById('rating-input');
    if (stars.length && ratingInput) {
        stars.forEach((star, idx) => {
            star.addEventListener('click', () => {
                ratingInput.value = idx + 1;
                updateStars(idx + 1);
            });
            star.addEventListener('mouseover', () => {
                updateStars(idx + 1);
            });
            star.addEventListener('mouseout', () => {
                updateStars(parseInt(ratingInput.value));
            });
        });
        function updateStars(rating) {
            stars.forEach((star, idx) => {
                star.style.color = idx < rating ? '#fbbf24' : '#ccc';
            });
        }
        updateStars(parseInt(ratingInput.value));
    }

    // Initial load
    loadReviews();
}); 