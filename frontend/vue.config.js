const { defineConfig } = require("@vue/cli-service");
const packageJson = require("./package.json");
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const CompressionPlugin = require('compression-webpack-plugin');
const { VuetifyPlugin } = require('webpack-plugin-vuetify')

module.exports = defineConfig({
  chainWebpack: (config) => {
    // Set environment variables for Webpack
    config.plugin("define").tap((args) => {
      args[0]["process.env"].VUE_APP_VERSION = JSON.stringify(packageJson.version);
      return args;
    });
  },
  productionSourceMap: true,
  lintOnSave: true,
  configureWebpack: {
    devServer: {
      historyApiFallback: true
    },
    mode: 'development',
    optimization: {
      splitChunks: {
        chunks: 'all',
      },
      usedExports: true,
      minimize: process.env.NODE_ENV === 'production',
    },
    plugins: [
      // new BundleAnalyzerPlugin(),
      new CompressionPlugin({
        algorithm: 'gzip',
        test: /\.(js|css|html|svg)$/,
        threshold: 10240, // Only compress files larger than 10 KB
        minRatio: 0.8
      }),
      new VuetifyPlugin(),
    ]
  },
  transpileDependencies: true
});
