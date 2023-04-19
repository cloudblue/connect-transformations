/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
const path = require('path');
const htmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const ESLintPlugin = require('eslint-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

const generateHtmlPlugin = (title) => {
  const moduleName = title.toLowerCase().replace(/\s/g, '_');

  return new htmlWebpackPlugin({
    title,
    filename: `${moduleName}.html`,
    template: `./ui/pages/${moduleName}.html`,
    chunks: [moduleName]
  });
}

const populateHtmlPlugins = (pagesArray) => {
  res = [];
  pagesArray.forEach(page => {
    res.push(generateHtmlPlugin(page));
  })
  return res;
}

const pages = populateHtmlPlugins([
  "Transformations/Copy",
  "Transformations/Lookup Subscription",
  "Transformations/Lookup Product Item",
  "Transformations/Currency Conversion",
  "Transformations/Manual",
  "Transformations/Split Column",
  "Transformations/Formula",
  "Transformations/Filter Row",
]);

module.exports = {
  mode: 'production',
  entry: {
    ['transformations/copy']: __dirname + "/ui/src/pages/transformations/copy.js",
    ['transformations/currency_conversion']: __dirname + "/ui/src/pages/transformations/currency_conversion.js",
    ['transformations/filter_row']: __dirname + "/ui/src/pages/transformations/filter_row.js",
    ['transformations/formula']: __dirname + "/ui/src/pages/transformations/formula.js",
    ['transformations/lookup_subscription']: __dirname + "/ui/src/pages/transformations/lookup_subscription.js",
    ['transformations/lookup_product_item']: __dirname + "/ui/src/pages/transformations/lookup_product_item.js",
    ['transformations/manual']: __dirname + "/ui/src/pages/transformations/manual.js",
    ['transformations/split_column']: __dirname + "/ui/src/pages/transformations/split_column.js",  
  },
  output: {
    filename: '[name].[contenthash].js',
    path: path.resolve(__dirname, 'connect_transformations/static'),
    clean: true,
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
     minimizer: [
      new CssMinimizerPlugin(),
    ],
  },
  plugins: [
    ...pages,
    new CopyWebpackPlugin({
      patterns: [
        { from: __dirname + "/ui/images", to: "images" },
      ],
    }),
    new MiniCssExtractPlugin({
      filename: "[name].[contenthash].css",
      chunkFilename: "[id].css",
    }),
    new ESLintPlugin(),
  ],
  resolve: {
    alias: {
      '~styles': path.resolve(__dirname, 'ui/styles'),
    },
  },
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.styl(us)?$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
          'stylus-loader',
        ],
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts/'
            },
          },
        ],
      },
    ],
  },
}
