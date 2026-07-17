# Quizly API Endpoint Implementation Checklist

Source: https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=quizly

Use this document as the implementation checklist for the backend API.

## Authentication

Login und Registrierung

### [x] POST /api/register/

**Description:** Registriert einen neuen Benutzer.

**Permissions:** No permissions required

**Request Body**

```json
{
    "username":  "your_username",
    "password":  "your_password",
    "confirmed_password":  "your_confirmed_password",
    "email":  "your_email@example.com"
}
```

**Success Response:** Benutzer wurde erfolgreich erstellt.

```json
{
    "detail":  "User created successfully!"
}
```

**Status Codes**

- `201`: Benutzer erfolgreich erstellt.
- `400`: Ungültige Daten.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [x] Add or update route
- [x] Add serializer/request validation
- [x] Add view/business logic
- [x] Add permissions/auth handling
- [x] Add tests for success and error cases

### [x] POST /api/login/

**Description:** Meldet den Benutzer an und setzt Auth-Cookies.

**Permissions:** No permissions required
**Extra:** Setzt `access_token` und `refresh_token` als Cookies.

**Request Body**

```json
{
    "username":  "your_username",
    "password":  "your_password"
}
```

**Success Response:** Login war erfolgreich. Cookies werden gesetzt.

```json
{
    "detail":  "Login successfully!",
    "user":  {
                 "id":  1,
                 "username":  "your_username",
                 "email":  "your_email@example.com"
             }
}
```

**Status Codes**

- `200`: Erfolgreicher Login.
- `401`: Ungültige Anmeldedaten.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [x] Add or update route
- [x] Add serializer/request validation
- [x] Add view/business logic
- [x] Add permissions/auth handling
- [x] Add tests for success and error cases

### [x] POST /api/logout/

**Description:** Meldet den Benutzer ab und löscht alle Token.

**Permissions:** Authentifizierung erforderlich.
**Extra:** Cookies `access_token` und `refresh_token` werden entfernt.

**Request Body**

```json
{

}
```

**Success Response:** Der Benutzer wird ausgeloggt, alle Tokens sind ungültig.

```json
{
    "detail":  "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
}
```

**Status Codes**

- `200`: Erfolgreicher Logout.
- `401`: Nicht authentifiziert.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [x] Add or update route
- [x] Add serializer/request validation
- [x] Add view/business logic
- [x] Add permissions/auth handling
- [x] Add tests for success and error cases

### [x] POST /api/token/refresh/

**Description:** Erneuert den Access-Token mithilfe des Refresh-Tokens.

**Permissions:** Authentifizierung über `refresh_token`-Cookie erforderlich.
**Extra:** Setzt neuen `access_token` Cookie.

**Request Body**

```json
{

}
```

**Success Response:** Gibt einen neuen Access-Token zurück.

```json
{
    "detail":  "Token refreshed"
}
```

**Status Codes**

- `200`: Token erfolgreich erneuert.
- `401`: Refresh Token ungültig oder fehlt.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [x] Add or update route
- [x] Add serializer/request validation
- [x] Add view/business logic
- [x] Add permissions/auth handling
- [x] Add tests for success and error cases

## Quiz Management

Erstellung, Verwaltung und Abfrage von Quizzes

### [x] POST /api/quizzes/

**Description:** Erstellt ein neues Quiz basierend auf einer YouTube-URL.

**Permissions:** Authentifizierung erforderlich.

**Request Body**

```json
{
    "url":  "https://www.youtube.com/watch?v=example"
}
```

**Success Response:** Gibt das erstellte Quiz mit allen Fragen zurück.

```json
{
    "id":  1,
    "title":  "Quiz Title",
    "description":  "Quiz Description",
    "created_at":  "2023-07-29T12:34:56.789Z",
    "updated_at":  "2023-07-29T12:34:56.789Z",
    "video_url":  "https://www.youtube.com/watch?v=example",
    "questions":  [
                      {
                          "id":  1,
                          "question_title":  "Question 1",
                          "question_options":  [
                                                   "Option A",
                                                   "Option B",
                                                   "Option C",
                                                   "Option D"
                                               ],
                          "answer":  "Option A",
                          "created_at":  "2023-07-29T12:34:56.789Z",
                          "updated_at":  "2023-07-29T12:34:56.789Z"
                      }
                  ]
}
```

**Status Codes**

- `201`: Quiz erfolgreich erstellt.
- `400`: Ungültige URL oder Anfragedaten.
- `401`: Nicht authentifiziert.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [x] Add or update route
- [x] Add serializer/request validation
- [x] Add view/business logic
- [x] Add permissions/auth handling
- [x] Add tests for success and error cases

### [ ] GET /api/quizzes/

**Description:** Ruft alle Quizzes des authentifizierten Benutzers ab.

**Permissions:** Authentifizierung erforderlich.

**Success Response:** Liste aller Quizzes des Benutzers mit Fragen.

```json
{
    "id":  1,
    "title":  "Quiz Title",
    "description":  "Quiz Description",
    "created_at":  "2023-07-29T12:34:56.789Z",
    "updated_at":  "2023-07-29T12:34:56.789Z",
    "video_url":  "https://www.youtube.com/watch?v=example",
    "questions":  [
                      {
                          "id":  1,
                          "question_title":  "Question 1",
                          "question_options":  [
                                                   "Option A",
                                                   "Option B",
                                                   "Option C",
                                                   "Option D"
                                               ],
                          "answer":  "Option A"
                      }
                  ]
}
```

**Status Codes**

- `200`: Quizzes erfolgreich abgerufen.
- `401`: Nicht authentifiziert.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [ ] Add or update route
- [ ] Add serializer/request validation
- [ ] Add view/business logic
- [ ] Add permissions/auth handling
- [ ] Add tests for success and error cases

### [ ] GET /api/quizzes/{id}/

**Description:** Ruft ein spezifisches Quiz des Benutzers ab.

**Permissions:** Authentifizierung erforderlich. Benutzer kann nur eigene Quizzes abrufen.

**URL Parameters**

| Name | Required | Description |
| --- | --- | --- |
| id | yes | Die ID des Quiz, das abgerufen werden soll. |

**Success Response:** Das spezifische Quiz mit allen Fragen und Details.

```json
{
    "id":  1,
    "title":  "Quiz Title",
    "description":  "Quiz Description",
    "created_at":  "2023-07-29T12:34:56.789Z",
    "updated_at":  "2023-07-29T12:34:56.789Z",
    "video_url":  "https://www.youtube.com/watch?v=example",
    "questions":  [
                      {
                          "id":  1,
                          "question_title":  "Question 1",
                          "question_options":  [
                                                   "Option A",
                                                   "Option B",
                                                   "Option C",
                                                   "Option D"
                                               ],
                          "answer":  "Option A"
                      }
                  ]
}
```

**Status Codes**

- `200`: Quiz erfolgreich abgerufen.
- `401`: Nicht authentifiziert.
- `404`: Quiz nicht gefunden.
- `403`: Zugriff verweigert - Quiz gehört nicht dem Benutzer.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [ ] Add or update route
- [ ] Add serializer/request validation
- [ ] Add view/business logic
- [ ] Add permissions/auth handling
- [ ] Add tests for success and error cases

### [ ] PATCH /api/quizzes/{id}/

**Description:** Aktualisiert einzelne Felder eines Quiz (partielle Aktualisierung).

**Permissions:** Authentifizierung erforderlich. Benutzer kann nur eigene Quizzes bearbeiten.

**URL Parameters**

| Name | Required | Description |
| --- | --- | --- |
| id | yes | Die ID des Quiz, das aktualisiert werden soll. |

**Request Body**

```json
{
    "title":  "Partially Updated Title",
    "description":  "Partially Updated Description"
}
```

**Success Response:** Das aktualisierte Quiz mit allen Details.

```json
{
    "id":  1,
    "title":  "Partially Updated Title",
    "description":  "Quiz Description",
    "created_at":  "2023-07-29T12:34:56.789Z",
    "updated_at":  "2023-07-29T14:45:12.345Z",
    "video_url":  "https://www.youtube.com/watch?v=example",
    "questions":  [
                      {
                          "id":  1,
                          "question_title":  "Question 1",
                          "question_options":  [
                                                   "Option A",
                                                   "Option B",
                                                   "Option C",
                                                   "Option D"
                                               ],
                          "answer":  "Option A"
                      }
                  ]
}
```

**Status Codes**

- `200`: Quiz erfolgreich aktualisiert.
- `400`: Ungültige Anfragedaten.
- `401`: Nicht authentifiziert.
- `403`: Zugriff verweigert - Quiz gehört nicht dem Benutzer.
- `404`: Quiz nicht gefunden.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [ ] Add or update route
- [ ] Add serializer/request validation
- [ ] Add view/business logic
- [ ] Add permissions/auth handling
- [ ] Add tests for success and error cases

### [ ] DELETE /api/quizzes/{id}/

**Description:** Löscht ein Quiz und alle zugehörigen Fragen permanent.

**Permissions:** Authentifizierung erforderlich. Benutzer kann nur eigene Quizzes löschen.
**Extra:** Warnung: Das Löschen ist permanent und kann nicht rückgängig gemacht werden.

**URL Parameters**

| Name | Required | Description |
| --- | --- | --- |
| id | yes | Die ID des Quiz, das gelöscht werden soll. |

**Success Response:** Keine Antwortdaten bei erfolgreichem Löschen.

```json
null
```

**Status Codes**

- `204`: Quiz erfolgreich gelöscht.
- `401`: Nicht authentifiziert.
- `403`: Zugriff verweigert - Quiz gehört nicht dem Benutzer.
- `404`: Quiz nicht gefunden.
- `500`: Interner Serverfehler.

**Rate Limits:** No limit

**Implementation Tasks**

- [ ] Add or update route
- [ ] Add serializer/request validation
- [ ] Add view/business logic
- [ ] Add permissions/auth handling
- [ ] Add tests for success and error cases
