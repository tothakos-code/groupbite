const { defineConfig } = require('@vue/cli-service');
process.env.VUE_APP_VERSION = require('./package.json').version
process.env.VUE_APP_FALU_BANNER = process.env.FALU_BANNER

module.exports = defineConfig({
  transpileDependencies: true
});
