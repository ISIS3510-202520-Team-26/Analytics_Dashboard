# 🎯 Guía de Integración: Flutter App + Analytics Dashboard

## Estado Actual

### ✅ Lo que YA funciona

Tu app Flutter **SÍ está registrando eventos** correctamente a través del `TelemetryRepository`:

```dart
// Eventos que ya están funcionando:
✅ search.performed       // Búsquedas realizadas
✅ search.filter.used     // Uso de filtros
✅ category.clicked       // Clicks en categorías
✅ listing.viewed         // Vistas de listings
✅ listing.created        // Listings creados
✅ auth.login.success     // Logins exitosos
```

### ⚠️ Lo que falta implementar

Para que **todas las visualizaciones del dashboard** funcionen correctamente, necesitas agregar dos tipos de eventos adicionales:

1. **`ui.click`** - Para BQ 2.2 (Clicks por botón)
2. **`screen.view`** - Para BQ 2.4 (Tiempo en pantallas)

---

## 🔧 Implementación Recomendada

### Opción 1: Wrapper Automático (Recomendado)

Crea un widget que automáticamente registre clicks:

```dart
// lib/core/analytics/analytics_button.dart
import 'package:flutter/material.dart';
import '../../data/repositories/telemetry_repository.dart';

/// Widget que automáticamente registra clicks en el sistema de analytics
class AnalyticsButton extends StatelessWidget {
  final String buttonName;
  final VoidCallback onPressed;
  final Widget child;
  final ButtonStyle? style;

  const AnalyticsButton({
    Key? key,
    required this.buttonName,
    required this.onPressed,
    required this.child,
    this.style,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: style,
      onPressed: () {
        // Registrar el click
        TelemetryRepository().trackClick(buttonName);
        
        // Ejecutar la acción original
        onPressed();
      },
      child: child,
    );
  }
}

// Uso:
AnalyticsButton(
  buttonName: 'create_listing_submit',
  onPressed: () => _handleSubmit(),
  child: Text('Crear Listing'),
)
```

### Opción 2: Tracking Manual

Si prefieres mantener control manual, agrega tracking en cada botón importante:

```dart
// Antes
ElevatedButton(
  onPressed: () => _handleSubmit(),
  child: Text('Buscar'),
)

// Después
ElevatedButton(
  onPressed: () {
    TelemetryRepository().trackClick('search_button');
    _handleSubmit();
  },
  child: Text('Buscar'),
)
```

### Screen View Tracking

Implementa tracking automático de vistas de pantalla usando un `RouteObserver`:

```dart
// lib/core/analytics/screen_tracker.dart
import 'package:flutter/material.dart';
import '../../data/repositories/telemetry_repository.dart';

class ScreenTracker extends RouteObserver<PageRoute<dynamic>> {
  final _telemetry = TelemetryRepository();

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);
    if (route is PageRoute) {
      _trackScreen(route.settings.name ?? 'unknown');
    }
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPop(route, previousRoute);
    if (previousRoute is PageRoute) {
      _trackScreen(previousRoute.settings.name ?? 'unknown');
    }
  }

  void _trackScreen(String screenName) {
    _telemetry.trackScreenView(screenName);
  }
}

// En tu MaterialApp:
MaterialApp(
  navigatorObservers: [ScreenTracker()],
  routes: {
    '/home': (context) => HomePage(),
    '/login': (context) => LoginPage(),
    '/create_listing': (context) => CreateListingPage(),
    // ...
  },
)
```

---

## 📊 Mapeo de Nombres

Para que el dashboard muestre correctamente los datos, usa estos nombres estándar:

### Botones Principales
```dart
// Navegación
'home_button'
'search_button'
'profile_button'
'notifications_button'

// Filtros
'filter_open'           // Abrir panel de filtros
'filter_apply'          // Aplicar filtros
'filter_clear'          // Limpiar filtros
'filter_category'       // Seleccionar categoría
'toggle_location'       // Toggle de ubicación

// Listings
'listing_view'          // Ver detalle
'listing_favorite'      // Agregar a favoritos
'listing_contact'       // Contactar vendedor
'create_listing_start'  // Iniciar creación
'create_listing_submit' // Enviar listing

// Auth
'login_submit'
'register_submit'
'logout_button'
```

### Pantallas
```dart
'home'
'login'
'register'
'search'
'listing_detail'
'create_listing'
'profile'
'favorites'
'messages'
'settings'
```

---

## 🎯 Validación

### 1. Verificar en Logs Locales

Agrega logging temporal para verificar:

```dart
@override
Future<void> trackClick(String buttonName) async {
  debugPrint('📊 Analytics: Click on $buttonName');
  await super.trackClick(buttonName);
}

@override
Future<void> trackScreenView(String screenName) async {
  debugPrint('📊 Analytics: Screen view $screenName');
  await super.trackScreenView(screenName);
}
```

### 2. Verificar en el Backend

Usa este comando PowerShell para ver si los eventos llegan:

```powershell
# Ver clicks (BQ 2.2)
Invoke-RestMethod -Uri "http://3.19.208.242:8000/v1/analytics/bq/2_2?start=2025-11-11T00:00:00Z&end=2025-11-11T23:59:59Z"

# Ver tiempo en pantallas (BQ 2.4)
Invoke-RestMethod -Uri "http://3.19.208.242:8000/v1/analytics/bq/2_4?start=2025-11-11T00:00:00Z&end=2025-11-11T23:59:59Z"
```

### 3. Verificar en el Dashboard

1. Abre el dashboard: `http://localhost:8501`
2. Ve a **🎯 UX Tuning (Flutter)**
3. Selecciona "Últimos 7 días"
4. Verifica que aparezcan los eventos

---

## 📈 Migración Gradual

No necesitas implementar todo de una vez. Aquí está el orden recomendado:

### Fase 1: Screen Tracking (Más importante)
1. Implementa `ScreenTracker` con `RouteObserver`
2. Asigna nombres a todas tus rutas
3. Verifica en BQ 2.4

### Fase 2: Botones Críticos
1. Search button
2. Filter buttons
3. Create listing button
4. Login/Register buttons

### Fase 3: Botones Secundarios
1. Navigation buttons
2. List item buttons
3. Settings buttons

---

## 🔍 Troubleshooting

### "No aparecen datos en el dashboard"

1. **Verifica la conexión:**
   ```dart
   final events = await TelemetryRepository().trackClick('test_button');
   print('Event registered: $events');
   ```

2. **Verifica el rango de fechas:**
   - El dashboard busca datos en el rango seleccionado
   - Asegúrate de seleccionar "Últimos 7 días" o un rango que incluya hoy

3. **Flush manual:**
   ```dart
   await TelemetryRepository().flush(); // Envía eventos inmediatamente
   ```

### "Eventos duplicados"

Si ves el mismo evento múltiples veces:
- Asegúrate de no llamar `trackClick()` en el `build()` method
- Usa `onPressed`, no `onTap` del GestureDetector (a menos que sea necesario)

---

## 💡 Mejores Prácticas

1. **Nombres consistentes:** Usa snake_case para nombres de eventos
2. **No trackees todo:** Solo botones y pantallas importantes
3. **Agrega contexto:** Usa el parámetro `properties` para metadata adicional
4. **Performance:** Los eventos se envían en batch automáticamente
5. **Privacy:** No registres datos sensibles (contraseñas, tokens, etc.)

---

## 📚 Referencias

- **TelemetryRepository:** `lib/data/repositories/telemetry_repository.dart`
- **UxTuningService:** `lib/core/ux/ux_tunning_service.dart`
- **Backend Docs:** `Backend/README.md`
- **Dashboard:** `analytics-dashboard/README.md`

---

¿Necesitas ayuda implementando alguna de estas funcionalidades? ¡Avísame! 🚀
