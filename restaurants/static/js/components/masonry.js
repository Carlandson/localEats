export class MasonryGrid {
    constructor(options = {}) {
        this.defaultOptions = {
            gridClass: '.masonry-grid',
            itemClass: '.masonry-grid-item',
            columnWidth: '.masonry-grid-item',  // Added this
            gutter: 16,
            percentPosition: true,
            transitionDuration: '0.3s',
            initLayout: true,
            ...options
        };
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupMasonry());
        } else {
            this.setupMasonry();
        }
    }

    setupMasonry() {
        const grid = document.querySelector(this.defaultOptions.gridClass);
        if (!grid) return;

        // Initialize Masonry with columnWidth
        const masonry = new Masonry(grid, {
            itemSelector: this.defaultOptions.itemClass,
            columnWidth: this.defaultOptions.columnWidth,
            gutter: this.defaultOptions.gutter,
            percentPosition: this.defaultOptions.percentPosition,
            transitionDuration: this.defaultOptions.transitionDuration,
            initLayout: this.defaultOptions.initLayout
        });

        // Layout Masonry after each image loads
        imagesLoaded(grid).on('progress', () => {
            masonry.layout();
        });

        // Handle window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                masonry.layout();
            }, 250);
        });

        // Store masonry instance for potential future use
        grid.masonry = masonry;
    }

    // Static method to initialize multiple grids with different options
    static initializeGrids(gridsOptions = []) {
        if (gridsOptions.length === 0) {
            // If no options provided, initialize with defaults
            new MasonryGrid();
        } else {
            gridsOptions.forEach(options => new MasonryGrid(options));
        }
    }
}