const { defineConfig } = require("@vue/cli-service");
const packageJson = require("./package.json");
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = defineConfig({
  chainWebpack: (config) => {
    // Set environment variables for Webpack
    config.plugin("define").tap((args) => {
      args[0]["process.env"].VUE_APP_VERSION = JSON.stringify(packageJson.version);
      return args;
    });
  },
  configureWebpack: {
    devServer: {
      historyApiFallback: true
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
      },
      usedExports: true,
    },
    plugins: [
      // new BundleAnalyzerPlugin(),
      new CompressionPlugin({
        algorithm: 'gzip',
        test: /\.(js|css|html|svg)$/,
        threshold: 10240, // Only compress files larger than 10 KB
        minRatio: 0.8
      })]
  },
  transpileDependencies: true
});
