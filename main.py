import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.core.window import Window

if platform == 'android':
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    Activity = autoclass('org.kivy.android.PythonActivity').mActivity
else:
    run_on_ui_thread = lambda func: func

class WebBrowserApp(App):
    def build(self):
        Window.bind(on_keyboard=self.on_back_key)
        self.webview = None
        self.create_webview()
        return BoxLayout()

    @run_on_ui_thread
    def create_webview(self):
        if platform == 'android':
            self.webview = WebView(Activity)
            settings = self.webview.getSettings()
            
            # Включаем JavaScript, поддержку хранилищ и баз данных
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setDatabaseEnabled(True)
            
            # Разрешаем доступ к локальным ресурсам внутри WebView
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)
            settings.setAllowFileAccessFromFileURLs(True)
            settings.setAllowUniversalAccessFromFileURLs(True)
            
            # Ссылки открываются внутри нашего приложения
            self.webview.setWebViewClient(WebViewClient())
            
            # Растягиваем WebView на весь экран смартфона поверх Kivy
            Activity.addContentView(
                self.webview, 
                autoclass('android.view.ViewGroup$LayoutParams')(
                    autoclass('android.view.ViewGroup$LayoutParams').MATCH_PARENT,
                    autoclass('android.view.ViewGroup$LayoutParams').MATCH_PARENT
                )
            )
            
            # Читаем содержимое вашего index.html в строку
            current_dir = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(current_dir, 'index.html')
            
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Обманываем систему безопасности Android:
                # Загружаем HTML-код напрямую как безопасную строку данных.
                # BaseURL "https://localhost/" заставит Android считать контент безопасным HTTPS,
                # поэтому ошибка CLEARTEXT полностью исчезнет!
                self.webview.loadDataWithBaseURL(
                    "https://localhost/", 
                    html_content, 
                    "text/html", 
                    "UTF-8", 
                    None
                )
            except Exception as e:
                print(f"Ошибка чтения index.html: {e}")

    def on_back_key(self, window, key, scancode, codepoint, modifier):
        if key == 27 and self.webview:
            if self.webview.canGoBack():
                self.webview.goBack()
                return True
        return False

if __name__ == '__main__':
    WebBrowserApp().run()
