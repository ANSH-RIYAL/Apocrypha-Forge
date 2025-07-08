// Marketplace functionality
class MarketplaceInterface {
    constructor() {
        this.ideas = [];
        this.filteredIdeas = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadIdeas();
    }
    
    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.statusFilter = document.getElementById('statusFilter');
        this.sortBy = document.getElementById('sortBy');
        this.ideasGrid = document.getElementById('ideasGrid');
        this.noResults = document.getElementById('noResults');
    }
    
    bindEvents() {
        this.searchInput.addEventListener('input', () => this.filterIdeas());
        this.statusFilter.addEventListener('change', () => this.filterIdeas());
        this.sortBy.addEventListener('change', () => this.filterIdeas());
    }
    
    loadIdeas() {
        // Get ideas from DOM
        this.ideas = Array.from(document.querySelectorAll('.idea-card')).map(card => ({
            element: card,
            title: card.dataset.title,
            description: card.dataset.description,
            status: card.dataset.status,
            submitted: card.dataset.submitted,
            views: parseInt(card.dataset.views),
            comments: parseInt(card.dataset.comments)
        }));
        
        this.filteredIdeas = [...this.ideas];
        this.applyFilters();
    }
    
    filterIdeas() {
        const searchTerm = this.searchInput.value.toLowerCase();
        const statusFilter = this.statusFilter.value;
        const sortBy = this.sortBy.value;
        
        // Filter ideas
        this.filteredIdeas = this.ideas.filter(idea => {
            const matchesSearch = !searchTerm || 
                idea.title.includes(searchTerm) || 
                idea.description.includes(searchTerm);
            
            const matchesStatus = statusFilter === 'all' || idea.status === statusFilter;
            
            return matchesSearch && matchesStatus;
        });
        
        // Sort ideas
        this.filteredIdeas.sort((a, b) => {
            switch (sortBy) {
                case 'newest':
                    return new Date(b.submitted) - new Date(a.submitted);
                case 'oldest':
                    return new Date(a.submitted) - new Date(b.submitted);
                case 'most_viewed':
                    return b.views - a.views;
                case 'most_commented':
                    return b.comments - a.comments;
                default:
                    return 0;
            }
        });
        
        this.applyFilters();
    }
    
    applyFilters() {
        // Hide all ideas
        this.ideas.forEach(idea => {
            idea.element.style.display = 'none';
        });
        
        // Show filtered ideas
        this.filteredIdeas.forEach(idea => {
            idea.element.style.display = 'block';
        });
        
        // Show/hide no results message
        if (this.filteredIdeas.length === 0) {
            this.noResults.classList.remove('d-none');
        } else {
            this.noResults.classList.add('d-none');
        }
        
        // Update results count
        this.updateResultsCount();
    }
    
    updateResultsCount() {
        const totalIdeas = this.ideas.length;
        const filteredCount = this.filteredIdeas.length;
        
        // You can add a results counter here if needed
        console.log(`Showing ${filteredCount} of ${totalIdeas} ideas`);
    }
}

// Utility functions for marketplace
class MarketplaceUtils {
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
    
    static formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        
        if (diffInMinutes < 60) {
            return `${diffInMinutes} minutes ago`;
        } else if (diffInMinutes < 1440) {
            return `${Math.floor(diffInMinutes / 60)} hours ago`;
        } else {
            return `${Math.floor(diffInMinutes / 1440)} days ago`;
        }
    }
    
    static truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize marketplace when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new MarketplaceInterface();
    
    // Add smooth scrolling for any anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add loading animation for card interactions
    document.querySelectorAll('.idea-card').forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                e.target.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Loading...';
            }
        });
    });
});
