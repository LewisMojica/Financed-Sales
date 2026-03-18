### Translation Management

This app uses CSV-based translations instead of the Translation DocType fixtures. This approach is simpler and more maintainable.

## File Location

Place translation CSV files in:
```
[app_name]/[app_name]/translations/[lang].csv
```

Example for factory_miscel Spanish:
```
factory_miscel/factory_miscel/translations/es.csv
```

## Adding Translations

1. Create `translations/[lang].csv` (e.g., `es.csv` for Spanish)
2. Add translations in CSV format
3. Rebuild the app: `bench build --app factory_miscel`
4. Clear cache: `bench clear-cache`

## CSV Format

```csv
"Source String","Translated String"
"Button Text","Texto del Boton"
"Error: {0}","Error: {0}"
```

**Rules:**
- One translation per line
- Source and translation separated by comma
- Strings with special chars must be quoted
- Use `{0}`, `{1}` for placeholders

## Example: es.csv

```csv
"Submit with Adjustment","Enviar con Ajuste"
"Actions","Acciones"
"Checking batch quantities...","Verificando cantidades de lotes..."
"Error checking batch quantities: {0}","Error al verificar cantidades de lotes: {0}"
"Batch Quantity Adjustment Required","Se Requiere Ajuste de Cantidad de Lote"
"The following batches have insufficient quantities:","Los siguientes lotes tienen cantidades insuficientes:"
"Batch","Lote"
"Item","Articulo"
"Warehouse","Almacen"
"Required","Requerido"
"Available","Disponible"
"Adjustment","Ajuste"
"Create stock adjustments for missing quantities and submit?","Crear ajustes de inventario para cantidades faltantes y enviar?"
"Submission cancelled","Envio cancelado"
"Creating adjustments and submitting...","Creando ajustes y enviando..."
"Stock Entry submitted successfully!","Entrada de Stock enviada exitosamente!"
"Created {0} stock adjustment(s):","{0} ajuste(s) de inventario creado(s):"
"Stock Entry submitted successfully","Entrada de Stock enviada exitosamente"
"Error submitting stock entry: {0}","Error al enviar entrada de stock: {0}"
"Unknown error","Error desconocido"
"Submitting...","Enviando..."
```

## Why CSV Over Fixtures?

| Fixtures/Translation DocType | CSV Approach |
|------------------------------|--------------|
| Create documents in UI | Edit directly in code |
| Export via command | Already in version control |
| Harder to review changes | Easy to diff in git |
| Requires import on new sites | Travels with app code |
| More steps for updates | Just edit and rebuild |

## Supported Languages

Add a new file for each language:
- `translations/es.csv` - Spanish
- `translations/fr.csv` - French
- `translations/de.csv` - German
- etc.
