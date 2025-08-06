module.exports = {
  root: true,
  extends: [
    "eslint:recommended",
    "plugin:vue/recommended",
    // "@vue/prettier",
  ],
  rules: {
    "vue/no-unused-vars": "error",
    'vue/valid-v-slot': [
      'error', {
        allowModifiers: true,
      },
    ],
  },
  globals: {
    process: true,
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@babel/eslint-parser',
    ecmaVersion: 2020,
    sourceType: 'module',
    requireConfigFile: false,
  },
  env: {
    es6: true,
    browser: true,
    node: true,
  },
}
