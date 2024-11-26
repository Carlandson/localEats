const path = require('path');

module.exports = {
    // Entry point is your main layoutEditor.js
    entry: {
        layoutEditor: './restaurants/static/js/layoutEditor.js',
        auth: './restaurants/static/js/auth/logout.js'
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'restaurants/static/dist')
    },
    // Help webpack resolve imports without full paths
    resolve: {
        alias: {
            '@utils': path.resolve(__dirname, 'restaurants/static/js/utils/'),
            '@handlers': path.resolve(__dirname, 'restaurants/static/js/handlers/'),
            '@components': path.resolve(__dirname, 'restaurants/static/js/components/')
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