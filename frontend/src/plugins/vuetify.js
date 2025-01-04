import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
// import '@mdi/font/css/materialdesignicons.css';

const dark = {
  dark: true,
  colors: {
    background: "#212529",
    surface: "#0c1a1d",
    primary: "#4c8c88",
    secondary: "#202626",
    error: "#f44336",
    info: "#2196F3",
    success: "#4caf50",
    warning: "#fb8c00",
  },
};

const light = {
  dark: false,
  colors: {
    background: "#edf4fb",
    surface: "#ebfeff",
    primary: "#67bcb7",
    secondary: "#e6eaee",
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
