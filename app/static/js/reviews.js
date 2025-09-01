document.addEventListener("DOMContentLoaded", function() {
    const reviewForm = document.getElementById("review-form");
    const reviewList = document.getElementById("review-list");
    const stars = document.querySelectorAll(".star");
    const ratingValue = document.getElementById("rating-value");

    // Star Rating Selection
    stars.forEach(star => {
        star.addEventListener("click", function() {
            let rating = this.getAttribute("data-value");
            ratingValue.value = rating;

            // Highlight selected stars
            stars.forEach(s => s.classList.remove("selected"));
            for (let i = 0; i < rating; i++) {
                stars[i].classList.add("selected");
            }
        });
    });

    // Review Form Submission
    reviewForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent page refresh

        const username = document.getElementById("username").value.trim();
        const reviewText = document.getElementById("review-text").value.trim();
        const rating = ratingValue.value;

        if (username === "" || reviewText === "" || rating === "0") {
            alert("Please enter your name, review, and select a rating.");
            return;
        }

        // Create new review element
        const reviewItem = document.createElement("div");
        reviewItem.classList.add("review-item");
        reviewItem.innerHTML = `<strong>${username}:</strong> ${"★".repeat(rating)} ${reviewText}`;

        // Append to the review list
        reviewList.appendChild(reviewItem);

        // Reset form
        document.getElementById("username").value = "";
        document.getElementById("review-text").value = "";
        ratingValue.value = "0";
        stars.forEach(s => s.classList.remove("selected"));
    });
});
