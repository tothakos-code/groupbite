const { defineConfig } = require('@vue/cli-service');
const packageJson = require('./package.json');


module.exports = defineConfig({
  chainWebpack: (config) => {
    // Set environment variables for Webpack
    config.plugin('define').tap((args) => {
      args[0]['process.env'].VUE_APP_VERSION = JSON.stringify(packageJson.version);
      return args;
    });
  },
  configureWebpack: {
    devServer: {
      historyApiFallback: true
    }
  },
  transpileDependencies: true
});
