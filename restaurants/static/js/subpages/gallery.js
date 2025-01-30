import { MasonryGrid } from '../components/masonry.js';

function initializeGallery() {
    new MasonryGrid({
        gridClass: '.masonry-grid',
        itemClass: '.masonry-grid-item',
        columnWidth: '.masonry-grid-item',
        gutter: 16,
        percentPosition: true
    });
}

document.addEventListener('DOMContentLoaded', initializeGallery);