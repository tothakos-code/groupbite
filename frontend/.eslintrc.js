module.exports = {
  root: true,
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-recommended",
    // "@vue/prettier",
  ],
  rules: {
    "vue/no-unused-vars": "error"
  },
  globals: {
    process: true,
  },
  env: {
  browser: true,
  node: true,
  },
}
