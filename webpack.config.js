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
  const moduleName = title.toLowerCase();

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

const pages = populateHtmlPlugins(["Transformations/Copy"]);

module.exports = {
  mode: 'production',
  entry: {
    ['transformations/copy']: __dirname + "/ui/src/pages/transformations/copy.js",
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
      filename: "index.css",
      chunkFilename: "[id].css",
    }),
    new ESLintPlugin(),
  ],
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
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
