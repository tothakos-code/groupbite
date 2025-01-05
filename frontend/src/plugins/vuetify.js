import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
// import '@mdi/font/css/materialdesignicons.css';

const dark = {
  dark: true,
  colors: {
    background: "#212529",
    surface: "#212529",
    primary: "#447e7a",
    secondary: "#2e5452",
    header: "#252a2e",
    error: "#f44336",
    info: "#2196F3",
    success: "#2c792f",
    warning: "#fb8c00",
  },
};

const light = {
  dark: false,
  colors: {
    background: "#ebfeff",
    surface: "#ffffff",
    primary: "#67bcb7",
    secondary: "#d1ebe9",
    header: "#f8f8f8",
    error: "#f44336",
    info: "#2196F3",
    success: "#4caf50",
    warning: "#fb8c00",
  },
};


const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: "mdi",
  },
  display: {
    thresholds: {
      xs: 0,
      sm: 576,
      md: 768,
      lg: 960,
      xl: 1200,
      xxl: 1400,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      dark,
      light
    }
  },
});

export default vuetify;
