// CHRISTUS App – Shared translations (DE / EN)
(function () {
  var TRANS = {
    de: {
      // Navigation
      nav_home: 'Start',
      nav_learn: 'Lernen',
      nav_glossary: 'Glossar',
      nav_profile: 'Profil',
      back: '← Zurück',

      // Login
      login_tab: 'Anmelden',
      register_tab: 'Registrieren',
      username_label: 'Benutzername',
      username_placeholder: 'Dein Name',
      reg_placeholder: 'Wie heißt du?',
      login_btn: 'Anmelden →',
      register_btn: 'Konto erstellen →',
      guest_btn: '👤 Als Gast fortfahren',
      manual_divider: 'oder manuell',
      last_login_prefix: 'Zuletzt: ',
      tap_to_login: 'Tippe zum Anmelden',
      err_enter_name: 'Bitte gib deinen Namen ein.',
      err_user_not_found: 'Benutzer nicht gefunden. Bitte registrieren.',
      err_name_taken: 'Benutzername bereits vergeben.',
      msg_welcome_back: 'Willkommen zurück, ',
      msg_account_created: 'Konto erstellt! Willkommen, ',

      // Home
      greeting_morning: 'Guten Morgen',
      greeting_day: 'Guten Tag',
      greeting_evening: 'Guten Abend',
      greeting_sub: 'Willkommen in deiner Glaubensbildungs-App',
      greeting_back: 'Schön, dass du wieder da bist.',
      progress_label: 'Lernfortschritt',
      stat_done: 'Abgeschlossen',
      stat_total: 'Module gesamt',
      stat_remain: 'Ausstehend',
      quick_access: 'Schnellzugriff',
      learn_label: 'Lernbereich',
      learn_desc: '7 Kategorien · 42 Module · Vollständige Glaubensbildung',
      glossary_label: 'Glossar',
      glossary_desc: 'Schlüsselbegriffe',
      settings_label: 'Einstellungen',
      settings_desc: 'Profil & Sprache',
      recently: 'Zuletzt bearbeitet',
      empty_recent: 'Noch keine Module gestartet. Öffne den Lernbereich!',
      continue_btn: 'Weiter →',
      update_text: '🔄 Update verfügbar! Neue Version der App bereit.',
      update_btn: 'Jetzt aktualisieren',

      // Settings
      settings_header: 'Einstellungen',
      account_section: 'Konto',
      username_setting: 'Benutzername',
      progress_setting: 'Lernfortschritt',
      reset_btn: 'Zurücksetzen',
      lang_section: 'Sprache',
      app_section: 'App',
      offline_mode: 'Offline-Modus',
      offline_reload_sub: 'App-Daten neu laden',
      clear_cache_label: 'Cache leeren',
      clear_cache_btn: 'Leeren',
      logout_label: 'Abmelden',
      logout_sub: 'Session beenden',
      logout_btn: 'Abmelden',
      member_since: 'Mitglied seit ',
      guest_mode: 'Gast-Modus',
      modules_done_suffix: 'von 42 Modulen abgeschlossen',
      reset_confirm: 'Lernfortschritt wirklich zurücksetzen?',
      msg_progress_reset: 'Fortschritt zurückgesetzt.',
      msg_lang_saved: 'Sprache gespeichert.',
      msg_cache_cleared: 'Cache geleert. App wird neu geladen…',
      msg_no_cache: 'Kein Cache vorhanden.',
      offline_active: 'Aktiv – App ist offline verfügbar',
      offline_inactive: 'Nicht registriert',
      offline_unsupported: 'Nicht unterstützt',

      // Learn
      learn_area: 'Lernbereich',
      categories_label: 'Kategorien',
      modules_label: 'Module',
      done_label: 'Fertig',
      choose_cat: 'Wähle eine Kategorie',
      glossary_area: 'Glossar',
      glossary_sub: 'Schlüsselbegriffe aus allen Modulen',
      search_placeholder: 'Begriff suchen\u2026',
      no_terms: 'Keine Begriffe gefunden.',
      modul_prefix: 'Modul',
      cat_prefix: 'Kat. ',
      modules_count_suffix: ' Module',
      sec_fragestellung: 'Fragestellung',
      sec_frage_tag: 'Einstieg',
      sec_kern: 'Kernprinzip',
      sec_kern_tag: 'Einführung',
      sec_bibel: 'Bibelarbeit',
      sec_bibel_tag: 'Textarbeit',
      sec_zusammen: 'Zusammenfassung',
      sec_zusammen_tag: 'Freikirchliche Perspektive',
      sec_qv: 'Querverweise',
      sec_qv_tag: 'Vernetzung',
      sec_weiter: 'Weiterdenken',
      sec_weiter_tag: 'Vertiefung',
      sec_sk: 'Schlüsselbegriffe',
      sec_sk_tag: 'Glossar',
      terms_translations: 'Begriffe & Übersetzungen',
      mark_done_btn: 'Als abgeschlossen markieren',
      mark_undone_btn: '✓ Abgeschlossen',

      // Language selection
      lang_select_subtitle: 'Wähle deine Sprache / Select your language',
      lang_weiter: 'Weiter →',

      // Bible reader
      bible_label: 'Elberfelder Bibel',
      bible_desc: 'Elberfelder 1905 · Vollständige Bibel',
      nav_bible: 'Bibel',
      bible_header: 'Elberfelder Bibel 1905',
      bible_book: 'Buch wählen',
      bible_chapter: 'Kapitel wählen',
      bible_search_placeholder: 'Vers suchen…',
      bible_loading: 'Bibel wird geladen…',
      bible_load_error: 'Fehler beim Laden der Bibel.',
      bible_search_empty: 'Keine Ergebnisse gefunden.',
      bible_search_hint: 'Suchbegriff eingeben (mind. 3 Zeichen)',
      bible_select_book: '← Buch wählen',
      bible_select_chapter: '← Kapitel wählen',
      bible_verse_count: ' Verse',
      bible_chapter_count: ' Kapitel',
      search_result_one: 'Ergebnis',
      search_result_many: 'Ergebnisse',

      // Themen
      themen_label: 'Themen',
      themen_desc: '270 Themen · 18 Kategorien',
      nav_themen: 'Themen',
      themen_header: 'Themen',
      themen_sub: 'Alle Glaubensbereiche im Überblick',
      themen_count_label: 'Themen',
      themen_cat_label: 'Kategorien',
      themen_search_placeholder: 'Thema suchen…',
      themen_no_results: 'Keine Themen gefunden.',

      // Install / Download
      install_label: 'App installieren',
      install_desc: 'Offline & webunabhängig nutzen',
      install_btn: 'Installieren',
      install_sub: 'App auf Gerät installieren (offline verfügbar)',
      install_not_available: 'App kann im Browser bereits offline genutzt werden.',
      install_already: 'App ist bereits installiert.',

      // Copyright
      copyright_text: '© Mario Reiner Denzer',
      copyright_sub: 'Alle Rechte vorbehalten'
    },
    en: {
      // Navigation
      nav_home: 'Home',
      nav_learn: 'Learn',
      nav_glossary: 'Glossary',
      nav_profile: 'Profile',
      back: '← Back',

      // Login
      login_tab: 'Sign In',
      register_tab: 'Register',
      username_label: 'Username',
      username_placeholder: 'Your Name',
      reg_placeholder: "What's your name?",
      login_btn: 'Sign In →',
      register_btn: 'Create Account →',
      guest_btn: '👤 Continue as Guest',
      manual_divider: 'or manually',
      last_login_prefix: 'Last: ',
      tap_to_login: 'Tap to sign in',
      err_enter_name: 'Please enter your name.',
      err_user_not_found: 'User not found. Please register.',
      err_name_taken: 'Username already taken.',
      msg_welcome_back: 'Welcome back, ',
      msg_account_created: 'Account created! Welcome, ',

      // Home
      greeting_morning: 'Good Morning',
      greeting_day: 'Good Day',
      greeting_evening: 'Good Evening',
      greeting_sub: 'Welcome to your Faith Education App',
      greeting_back: 'Great to have you back.',
      progress_label: 'Learning Progress',
      stat_done: 'Completed',
      stat_total: 'Total Modules',
      stat_remain: 'Remaining',
      quick_access: 'Quick Access',
      learn_label: 'Learning Area',
      learn_desc: '7 Categories · 42 Modules · Complete Faith Education',
      glossary_label: 'Glossary',
      glossary_desc: 'Key Terms',
      settings_label: 'Settings',
      settings_desc: 'Profile & Language',
      recently: 'Recently Studied',
      empty_recent: 'No modules started yet. Open the Learning Area!',
      continue_btn: 'Continue →',
      update_text: '🔄 Update available! New version ready.',
      update_btn: 'Update now',

      // Settings
      settings_header: 'Settings',
      account_section: 'Account',
      username_setting: 'Username',
      progress_setting: 'Learning Progress',
      reset_btn: 'Reset',
      lang_section: 'Language',
      app_section: 'App',
      offline_mode: 'Offline Mode',
      offline_reload_sub: 'Reload app data',
      clear_cache_label: 'Clear Cache',
      clear_cache_btn: 'Clear',
      logout_label: 'Sign Out',
      logout_sub: 'End session',
      logout_btn: 'Sign Out',
      member_since: 'Member since ',
      guest_mode: 'Guest mode',
      modules_done_suffix: 'of 42 modules completed',
      reset_confirm: 'Really reset your learning progress?',
      msg_progress_reset: 'Progress reset.',
      msg_lang_saved: 'Language saved.',
      msg_cache_cleared: 'Cache cleared. Reloading app…',
      msg_no_cache: 'No cache found.',
      offline_active: 'Active – App is available offline',
      offline_inactive: 'Not registered',
      offline_unsupported: 'Not supported',

      // Learn
      learn_area: 'Learning Area',
      categories_label: 'Categories',
      modules_label: 'Modules',
      done_label: 'Done',
      choose_cat: 'Choose a category',
      glossary_area: 'Glossary',
      glossary_sub: 'Key Terms from all modules',
      search_placeholder: 'Search term\u2026',
      no_terms: 'No terms found.',
      modul_prefix: 'Module',
      cat_prefix: 'Cat. ',
      modules_count_suffix: ' Modules',
      sec_fragestellung: 'Question',
      sec_frage_tag: 'Introduction',
      sec_kern: 'Core Principle',
      sec_kern_tag: 'Introduction',
      sec_bibel: 'Bible Study',
      sec_bibel_tag: 'Text Study',
      sec_zusammen: 'Summary',
      sec_zusammen_tag: 'Free Church Perspective',
      sec_qv: 'Cross-references',
      sec_qv_tag: 'Connections',
      sec_weiter: 'Further Thinking',
      sec_weiter_tag: 'Deepening',
      sec_sk: 'Key Terms',
      sec_sk_tag: 'Glossary',
      terms_translations: 'Terms & Translations',
      mark_done_btn: 'Mark as complete',
      mark_undone_btn: '✓ Completed',

      // Language selection
      lang_select_subtitle: 'Wähle deine Sprache / Select your language',
      lang_weiter: 'Continue →',

      // Bible reader
      bible_label: 'Elberfelder Bible',
      bible_desc: 'Elberfelder 1905 · Complete Bible',
      nav_bible: 'Bible',
      bible_header: 'Elberfelder Bible 1905',
      bible_book: 'Select Book',
      bible_chapter: 'Select Chapter',
      bible_search_placeholder: 'Search verse…',
      bible_loading: 'Loading Bible…',
      bible_load_error: 'Error loading the Bible.',
      bible_search_empty: 'No results found.',
      bible_search_hint: 'Enter search term (min. 3 characters)',
      bible_select_book: '← Select book',
      bible_select_chapter: '← Select chapter',
      bible_verse_count: ' verses',
      bible_chapter_count: ' chapters',
      search_result_one: 'result',
      search_result_many: 'results',

      // Themen
      themen_label: 'Topics',
      themen_desc: '270 Topics · 18 Categories',
      nav_themen: 'Topics',
      themen_header: 'Topics',
      themen_sub: 'Overview of all faith areas',
      themen_count_label: 'Topics',
      themen_cat_label: 'Categories',
      themen_search_placeholder: 'Search topic…',
      themen_no_results: 'No topics found.',

      // Install / Download
      install_label: 'Install App',
      install_desc: 'Use offline & independently',
      install_btn: 'Install',
      install_sub: 'Install app on device (available offline)',
      install_not_available: 'App can already be used offline in the browser.',
      install_already: 'App is already installed.',

      // Copyright
      copyright_text: '© Mario Reiner Denzer',
      copyright_sub: 'All rights reserved'
    }
  };

  window.t = function (key) {
    var lang = localStorage.getItem('selectedLanguage') || 'de';
    var dict = TRANS[lang] || TRANS.de;
    if (dict[key] !== undefined) return dict[key];
    return TRANS.de[key] !== undefined ? TRANS.de[key] : key;
  };

  window.applyLang = function () {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var v = window.t(el.dataset.i18n);
      if (v != null) el.textContent = v;
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      var v = window.t(el.dataset.i18nPlaceholder);
      if (v != null) el.placeholder = v;
    });
  };
}());
