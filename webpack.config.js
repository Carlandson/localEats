const path = require('path');

module.exports = {
    mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
    entry: {
        layoutEditor: './restaurants/static/js/layoutEditor.js',
        create: [
            './restaurants/static/js/auth/addressValidate.js',
            './restaurants/static/js/constants/businessTypes.js',
        ],
        edit_business: './restaurants/static/js/subpages/editBusiness.js',
        about: './restaurants/static/js/subpages/about.js',
        gallery: './restaurants/static/js/subpages/gallery.js',
        home: './restaurants/static/js/subpages/home.js',
        menu: './restaurants/static/js/subpages/menubuilder.js',
        events: './restaurants/static/js/subpages/events.js',
        products: './restaurants/static/js/subpages/products.js',
        merch: './restaurants/static/js/subpages/merch.js',
        services: './restaurants/static/js/subpages/services.js',
        contact: './restaurants/static/js/subpages/contact.js',
        login: './restaurants/static/js/auth/login.js',
        index: [
            './restaurants/static/js/auth/logout.js',
            './restaurants/static/js/index.js',
        ],
        auth: './restaurants/static/js/auth/logout.js',
        register: './restaurants/static/js/auth/register.js',
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'restaurants/static/dist')
    },
    resolve: {
        extensions: ['.js'],
        modules: [
            path.resolve(__dirname, 'restaurants/static/js'),
            'node_modules'
        ]
    },
    // resolve: {
    //     alias: {
    //         '@utils': path.resolve(__dirname, 'localeats/restaurants/static/js/utils/'),
    //         '@handlers': path.resolve(__dirname, 'localeats/restaurants/static/js/handlers/'),
    //         '@components': path.resolve(__dirname, 'localeats/restaurants/static/js/components/')
    //     }
    // },
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
    // devtool: process.env.NODE_ENV === 'production' ? 'source-map' : 'eval-source-map',
    devtool: 'eval-source-map',
    optimization: {
        splitChunks: {
            chunks: 'all',
            minSize: 20000,
            maxSize: 244000,
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all'
                },
                common: {
                    name: 'common',
                    minChunks: 2,
                    chunks: 'all',
                    priority: -20
                }
            }
        }
    },
    
    // Increase limits to accommodate layoutEditor.bundle.js
    performance: {
        maxEntrypointSize: 800000,    // Increased to 800 KiB
        maxAssetSize: 800000          // Increased to 800 KiB
    }
};