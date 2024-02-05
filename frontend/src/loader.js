const fs = require('fs');
const path = require('path');

const pluginsDir = path.join(__dirname, 'plugins');

const loadPlugins = () => {
  const plugins = fs.readdirSync(pluginsDir).filter(plugin => {
    const pluginPath = path.join(pluginsDir, plugin);
    return fs.statSync(pluginPath).isDirectory();
  });

  plugins.forEach(plugin => {
    const initFilePath = path.join(pluginsDir, plugin, '__init__.js');
    if (fs.existsSync(initFilePath)) {
      require(initFilePath);
    }
  });
};

module.exports = loadPlugins;
