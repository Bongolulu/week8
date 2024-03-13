sequenceDiagram
    participant U as User
    participant C as Chrome
    participant F as Flask Server mit app.py
    participant T as index.html Template
    

    Note over F: Flask startet als Webserver
    Note over F: "Listen" auf 127.0.0.1:80
    U->>C: URL eingeben: http://127.0.0.1/hello?name=John
    Note over C: Chrome zerlegt URL in http, 127.0.0.1 und "/hello?name=John"
    C->>F: Baue TCP Verbindung to 127.0.0.1:80 auf
    Note over C, F: TCP Verbindung aufgebaut
    Note over C: Chrome verwendet Route ("/hello") and Paremeter ("?name=John")
    C->>F: Sendet "HTTP GET request" mit Inhalt "/hello?name=John"
    Note over F: Flask analysiert HTTP request und ruft passende Funktion bei "/hello" auf
    Note over F: Flask erstellt "Dictionary" mit dem Key "name" und dem Value "John" in "request.params"
    Note over T: index.html content: '<body>Hello {{ name }}</body>'
    F->>T: Flask setzt den Value "John" ins Template ein
    T-->>F: generiert HTML: '<body>Hello John</body>'
    F-->>C: Antwortet mit HTTP Respose mit dem Inhalt des fertigen htmls.
    C->>F: Sendet ggf. "HTTP GET request" mit Inhalt "/styles.css"
    C->>F: Sendet ggf. "HTTP GET request" mit Inhalt "/script.js"
    C->>C: Führt ggf. JavaScript aus
    C->>U: Zeigt die fertige html Seite mit Hello John an.
    C->>C: Javascript, reagiert auf Ereignisse
    C->>U: Aktualisiert ggf. die Anzeige mit JavaScript
