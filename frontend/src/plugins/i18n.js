import { createI18n } from "vue-i18n";
import hu from "@/locales/hu.json";

const i18n = createI18n({
  legacy: false,
  locale: "hu",
  messages: { hu },
});

export default i18n;
