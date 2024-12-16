export class PreviewCache {
    constructor() {
        this.cache = new Map();
        this.maxEntries = 10;
    }

    getKey(pageType, data) {
        return `${pageType}-${JSON.stringify(data)}`;
    }

    set(pageType, data, html) {
        const key = this.getKey(pageType, data);
        if (this.cache.size >= this.maxEntries) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, {
            html,
            timestamp: Date.now()
        });
    }

    get(pageType, data) {
        const key = this.getKey(pageType, data);
        const cached = this.cache.get(key);
        if (!cached || Date.now() - cached.timestamp > 5 * 60 * 1000) {
            this.cache.delete(key);
            return null;
        }
        return cached.html;
    }
}