const path = require('path');

module.exports = {
    entry: {
        layoutEditor: './restaurants/static/js/layoutEditor.js',
        auth: './restaurants/static/js/auth/logout.js',
        edit_business: './restaurants/static/js/subpages/editBusiness.js',
        about: './restaurants/static/js/subpages/about.js',
        gallery: './restaurants/static/js/subpages/gallery.js',
        home: './restaurants/static/js/subpages/home.js',
        menu: './restaurants/static/js/subpages/menubuilder.js',
        events: './restaurants/static/js/subpages/events.js',
        products: './restaurants/static/js/subpages/products.js',
        merch: './restaurants/static/js/subpages/merch.js',
        services: './restaurants/static/js/subpages/services.js',
        contact: './restaurants/static/js/subpages/contact.js'
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'restaurants/static/dist')
    },

    resolve: {
        alias: {
            '@utils': path.resolve(__dirname, 'localeats/restaurants/static/js/utils/'),
            '@handlers': path.resolve(__dirname, 'localeats/restaurants/static/js/handlers/'),
            '@components': path.resolve(__dirname, 'localeats/restaurants/static/js/components/')
        }
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    },
    devtool: process.env.NODE_ENV === 'production' ? 'source-map' : 'eval-source-map'
};