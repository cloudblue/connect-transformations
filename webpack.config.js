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
  "Transformations/Airtable lookup",
  "Transformations/Copy",
  "Transformations/Attachment lookup",
  "Transformations/Lookup subscription",
  "Transformations/Lookup FF request",
  "Transformations/Lookup product item",
  "Transformations/Currency conversion",
  "Transformations/Manual",
  "Transformations/Split columns",
  "Transformations/Formula",
  "Transformations/Filter row",
  "Transformations/VAT rate",
]);

module.exports = {
  mode: 'production',
  entry: {
    ['transformations/airtable_lookup']: __dirname + "/ui/src/pages/transformations/airtable_lookup.js",
    ['transformations/copy']: __dirname + "/ui/src/pages/transformations/copy.js",
    ['transformations/currency_conversion']: __dirname + "/ui/src/pages/transformations/currency_conversion.js",
    ['transformations/filter_row']: __dirname + "/ui/src/pages/transformations/filter_row.js",
    ['transformations/formula']: __dirname + "/ui/src/pages/transformations/formula.js",
    ['transformations/lookup_subscription']: __dirname + "/ui/src/pages/transformations/lookup_subscription.js",
    ['transformations/lookup_ff_request']: __dirname + "/ui/src/pages/transformations/lookup_ff_request.js",
    ['transformations/lookup_product_item']: __dirname + "/ui/src/pages/transformations/lookup_product_item.js",
    ['transformations/manual']: __dirname + "/ui/src/pages/transformations/manual.js",
    ['transformations/split_columns']: __dirname + "/ui/src/pages/transformations/split_columns.js",
    ['transformations/attachment_lookup']: __dirname + "/ui/src/pages/transformations/attachment_lookup.js",
    ['transformations/vat_rate']: __dirname + "/ui/src/pages/transformations/vat_rate.js",
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
