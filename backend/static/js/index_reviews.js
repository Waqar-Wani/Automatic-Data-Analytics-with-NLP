document.addEventListener('DOMContentLoaded', function() {
    const reviewsList = document.getElementById('reviews-list');
    const leftArrow = document.querySelector('.carousel-arrow.left');
    const rightArrow = document.querySelector('.carousel-arrow.right');
    let allReviews = [];
    let startIdx = 0;
    const VISIBLE_COUNT = 3;

    // Get reviews from data attribute
    if (reviewsList && reviewsList.dataset.reviews) {
        allReviews = JSON.parse(reviewsList.dataset.reviews);
    }

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
        if (leftArrow) leftArrow.disabled = startIdx === 0;
        if (rightArrow) rightArrow.disabled = (startIdx + VISIBLE_COUNT) >= allReviews.length;
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

    renderVisibleReviews();
}); 