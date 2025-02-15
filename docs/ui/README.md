# Documentación de UI/UX 🎨

## 1. Sistema de Diseño

### 1.1 Colores
```css
:root {
  /* Primarios */
  --primary-50: #f0f9ff;
  --primary-100: #e0f2fe;
  --primary-500: #0ea5e9;
  --primary-700: #0369a1;
  
  /* Neutrales */
  --neutral-50: #f8fafc;
  --neutral-100: #f1f5f9;
  --neutral-700: #334155;
  --neutral-900: #0f172a;
  
  /* Semánticos */
  --success: #22c55e;
  --warning: #eab308;
  --error: #ef4444;
  --info: #3b82f6;
}
```

### 1.2 Tipografía
```css
:root {
  --font-sans: 'Inter', system-ui;
  --font-mono: 'JetBrains Mono', monospace;
  
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
}
```

### 1.3 Espaciado
```css
:root {
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;
}
```

## 2. Componentes Core

### 2.1 Document Viewer
```tsx
// Visor de Documentos
<DocumentViewer
  document={document}
  preferences={userPrefs}
  annotations={annotations}
  collaborators={activeUsers}
/>

// Grid de Miniaturas
<ThumbnailGrid
  documentId={docId}
  totalPages={totalPages}
  viewMode={prefs.thumbnails.viewMode}
  size={prefs.thumbnails.size}
/>

// Panel de Anotaciones
<AnnotationsPanel
  annotations={pageAnnotations}
  defaultColor={prefs.annotations.defaultColor}
  defaultType={prefs.annotations.defaultType}
/>
```

### 2.2 Preferencias
```tsx
// Panel de Preferencias
<PreferencesPanel
  sections={[
    {
      title: "Visor",
      items: [
        {
          type: "select",
          label: "Tema",
          options: ["light", "dark", "system"]
        },
        {
          type: "slider",
          label: "Tamaño de fuente",
          min: 12,
          max: 24
        }
      ]
    }
  ]}
/>

// Atajos de Teclado
<KeyboardShortcuts
  shortcuts={prefs.keyboard.shortcuts}
  enabledFeatures={prefs.keyboard.enabledFeatures}
/>
```

### 2.3 Sincronización
```tsx
// Indicador de Estado
<SyncIndicator
  status={syncStatus}
  pendingOperations={pendingOps.length}
/>

// Panel de Conflictos
<ConflictResolution
  conflicts={syncConflicts}
  onResolve={handleConflictResolution}
/>
```

## 3. Estados de UI

### 3.1 Loading
```tsx
// Skeleton Loading
<SkeletonLoader
  type="document-viewer"
  pages={5}
/>

// Progress Indicator
<CircularProgress
  size="medium"
  label="Generando miniaturas..."
/>
```

### 3.2 Error
```tsx
// Error States
<ErrorBoundary
  fallback={<ErrorDisplay
    title="Error al cargar documento"
    message={error.message}
    action={retryLoad}
  />}
/>

// Toast Notifications
<Toast
  type="error"
  message="No se pudo guardar los cambios"
  action="Reintentar"
/>
```

### 3.3 Empty
```tsx
// Empty States
<EmptyState
  icon={<DocumentIcon />}
  title="Sin documentos"
  description="Comienza subiendo un documento"
  action={<UploadButton />}
/>
```

## 4. Responsive Design

### 4.1 Breakpoints
```css
/* Breakpoints */
--screen-sm: 640px;
--screen-md: 768px;
--screen-lg: 1024px;
--screen-xl: 1280px;
```

### 4.2 Layouts
```tsx
// Responsive Grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {thumbnails.map(thumb => (
    <ThumbnailCard key={thumb.id} {...thumb} />
  ))}
</div>

// Stack/Split View
<div className="flex flex-col lg:flex-row">
  <DocumentViewer className="w-full lg:w-2/3" />
  <AnnotationsPanel className="w-full lg:w-1/3" />
</div>
```

## 5. Animaciones

### 5.1 Transiciones
```css
/* Transiciones suaves */
.transition-base {
  transition: all 0.2s ease-in-out;
}

.transition-slow {
  transition: all 0.3s ease-in-out;
}
```

### 5.2 Micro-interacciones
```tsx
// Hover Effects
<Button
  className="hover:scale-105 active:scale-95 transition-base"
  onClick={handleClick}
/>

// Loading States
<div className="animate-pulse bg-gray-200 rounded-md" />
```

## 6. Accesibilidad

### 6.1 Contraste y Color
```css
/* Alto contraste */
.text-high-contrast {
  color: var(--neutral-900);
}

/* Indicadores sin color */
.focus-visible:outline-none {
  box-shadow: 0 0 0 2px var(--primary-500);
}
```

### 6.2 Keyboard Navigation
```tsx
// Focus Management
<FocusTrap>
  <Dialog
    aria-labelledby="dialog-title"
    aria-describedby="dialog-description"
  />
</FocusTrap>
```

## 7. Performance

### 7.1 Lazy Loading
```tsx
// Componentes
const DocumentViewer = lazy(() => import('./DocumentViewer'));

// Imágenes
<img
  loading="lazy"
  src={thumbnail.url}
  alt={thumbnail.alt}
/>
```

### 7.2 Virtualization
```tsx
// Listas largas
<VirtualList
  height={400}
  itemCount={1000}
  itemSize={50}
  renderItem={renderThumbnail}
/>
```

## 8. Testing

### 8.1 Unit Tests
```tsx
describe('DocumentViewer', () => {
  it('renders document content', () => {
    const { getByText } = render(<DocumentViewer doc={mockDoc} />);
    expect(getByText(mockDoc.title)).toBeInTheDocument();
  });
});
```

### 8.2 Integration Tests
```tsx
describe('Document Workflow', () => {
  it('allows annotation creation', async () => {
    const { getByRole, findByText } = render(<DocumentWorkflow />);
    
    await userEvent.click(getByRole('button', { name: /annotate/i }));
    expect(await findByText(/annotation saved/i)).toBeInTheDocument();
  });
});
```

## 9. Mejores Prácticas

1. Mobile First Design
2. Progressive Enhancement
3. Semantic HTML
4. ARIA labels
5. Error Boundaries
6. Performance Monitoring
7. A11y Testing
8. Visual Regression Tests

## 10. Recursos

- [Figma Designs](https://figma.com/firstcourt)
- [Component Library](https://storybook.firstcourt.legal)
- [A11y Guidelines](https://firstcourt.legal/a11y)
- [Performance Metrics](https://lighthouse.firstcourt.legal)
