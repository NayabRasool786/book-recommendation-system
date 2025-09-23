// frontend_web/script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Get references to our HTML elements ---
    const bookInput = document.getElementById('book-input');
    const searchBtn = document.getElementById('search-btn');
    const recommendationsContainer = document.getElementById('recommendations-container');
    const messageArea = document.getElementById('message-area');
    const bookTitlesDatalist = document.getElementById('book-titles');
    const topAuthorsList = document.getElementById('top-authors-list');
    const genreChartCanvas = document.getElementById('genre-chart');
    const ratingChartCanvas = document.getElementById('rating-chart');

    const API_URL = 'http://127.0.0.1:5000';
    let genreChart, ratingChart; // Variables to hold the chart instances

    // --- 2. Define All Functions ---

    // Fetches all book titles for the search bar autocomplete
    async function fetchAllBookTitles() {
        try {
            const response = await fetch(`${API_URL}/books`);
            const titles = await response.json();
            bookTitlesDatalist.innerHTML = titles.map(title => `<option value="${title}"></option>`).join('');
        } catch (error) {
            console.error('Failed to fetch book titles:', error);
        }
    }

    // Fetches and displays book recommendations based on user input
    async function getRecommendations() {
        const bookTitle = bookInput.value.trim();
        if (!bookTitle) {
            messageArea.textContent = 'Please enter a book title.';
            return;
        }
        recommendationsContainer.innerHTML = '';
        messageArea.textContent = '🔍 Finding similar books...';
        try {
            const response = await fetch(`${API_URL}/recommend?title=${encodeURIComponent(bookTitle)}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error);
            }
            const recommendations = await response.json();
            displayRecommendations(recommendations);
        } catch (error) {
            messageArea.textContent = `Error: ${error.message}`;
        }
    }
    
    // Fetches and displays the advanced analytics data
    async function getAndDisplayStats() {
        try {
            const response = await fetch(`${API_URL}/stats`);
            const stats = await response.json();
            
            topAuthorsList.innerHTML = stats.top_authors.map(a => 
                `<li>${a.author} <span>${a.ratings.toLocaleString()} ratings</span></li>`
            ).join('');

            renderGenreChart(stats.top_genres);
            renderRatingDistribution(stats.rating_distribution);

        } catch (error) {
            console.error('Failed to fetch stats:', error);
            messageArea.textContent = "Could not load literary insights. Is the backend server running?";
        }
    }

    // Renders the recommendation cards to the page
    function displayRecommendations(books) {
        messageArea.textContent = '';
        if (books.length === 0) {
            messageArea.textContent = 'No recommendations found.';
            return;
        }
        recommendationsContainer.innerHTML = books.map(book => `
            <div class="book-card">
                <div>
                    <h3>${book.book}</h3>
                    <p class="author">by ${book.author}</p>
                    <p class="genres">${book.genres}</p>
                </div>
                <div class="book-stats">
                    <p>⭐ ${book.avg_rating} (${book.num_ratings.toLocaleString()} ratings)</p>
                </div>
                <a href="${book.url}" target="_blank" class="url-link">View Book</a>
            </div>
        `).join('');
    }

    // Renders the Top Genres bar chart
    function renderGenreChart(genreData) {
        if (genreChart) genreChart.destroy();
        genreChart = new Chart(genreChartCanvas, {
            type: 'bar',
            data: {
                labels: genreData.map(g => g.genre),
                datasets: [{
                    label: 'Book Count by Genre',
                    data: genreData.map(g => g.count),
                    backgroundColor: 'rgba(0, 123, 255, 0.7)'
                }]
            },
            options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }
        });
    }

    // Renders the Rating Distribution bar chart
    function renderRatingDistribution(ratingData) {
        if (ratingChart) ratingChart.destroy();
        ratingChart = new Chart(ratingChartCanvas, {
            type: 'bar',
            data: {
                labels: ratingData.ratings,
                datasets: [{
                    label: 'Number of Books',
                    data: ratingData.counts,
                    backgroundColor: 'rgba(40, 167, 69, 0.7)'
                }]
            },
            options: { responsive: true, scales: { x: { title: { display: true, text: 'Average Rating' } } } }
        });
    }

    // --- 3. Attach Event Listeners and Run Initial Functions ---
    searchBtn.addEventListener('click', getRecommendations);
    bookInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') getRecommendations();
    });

    // Run these functions when the page first loads
    fetchAllBookTitles();
    getAndDisplayStats();
});