# Gitflow y Trunk-Based Development

> [!IMPORTANT]
> Este documento tiene como único objetivo el ser didáctico y divulgativo. Este archivo no pretende actuar como un manual.

## 1. Modelo Gitflow

_Gitflow_ es una estrategia de control de versiones fundamentada en el aislamiento de fases mediante ramas estandarizadas de larga y corta duración.

### 1.1. Ecosistema de Ramas

#### Ramas Permanentes
* **`main`**: Alberga el código fuente homologado que se encuentra en ejecución dentro del entorno de producción. Cada actualización es etiquetada con una versión semántica (`vX.Y.Z`). Ejemplos de versiones semánticas: `v1`, `v2`, `v1.1.0`.
* **`develop`**: Centraliza el código fuente validado que se encuentra pendiente de liberación. Sirve como punto de convergencia para el trabajo finalizado.

#### Ramas Temporales
* **`feature/*`**: Se originan desde `develop`. Contienen el desarrollo de requisitos funcionales específicos.
* **`release/*`**: Se originan desde `develop` cuando se alcanza la madurez de un paquete de entrega. Se destinan a pruebas de integración y correcciones menores.
* **`hotfix/*`**: Se originan desde `main` ante fallos críticos en producción. Permiten aplicar correcciones urgentes sin interrumpir el flujo de `develop`.

### 1.2. Procedimiento Operativo

1. **Desarrollo de Funcionalidades**:
   * Creación de la rama desde `develop`:
    ```bash
    git checkout -b feature/ID-tarea develop
    ```
   * Finalizado el trabajo, la rama es fusionada en `develop` evitando el avance rápido para conservar la trazabilidad del historial:
    ```bash
    git merge --no-ff feature/ID-tarea
    ```

2. **Preparación de Lanzamiento**:
   * Creación de la rama de liberación desde `develop`:
    ```bash
    git checkout -b release/v1.0.0 develop
    ```
   * Ejecución de pruebas de aceptación y correcciones de errores.

3. **Cierre de Liberación**:
   * Fusión de la rama de liberación en `main` y asignación de etiqueta:
    ```bash
    git merge --no-ff release/v1.0.0
    git tag -a v1.0.0 -m "Versión 1.0.0"
    ```
   * Fusión de los cambios de la liberación hacia `develop`:
    ```bash
    git checkout develop
    git merge --no-ff release/v1.0.0
    ```

---

## 2. Modelo Trunk-Based Development

_Trunk-Based Development_ es una estrategia de control de versiones estructurada sobre un tronco central de integración continua donde se incorporan modificaciones de alcance acotado con alta frecuencia.

### 2.1. Ecosistema de Ramas

* **`main` (o `trunk`)**: Única rama permanente en la cual se integra de forma continua el trabajo realizado por el equipo de desarrollo.
* **Ramas de Corta Duración**: Ramas efímeras creadas para realizar tareas específicas cuya duración no excede las 24 horas antes de ser integradas en el tronco principal.

### 2.2. Procedimiento Operativo

1. **Obtención del Estado Actual**:
   * Sincronización diaria del repositorio local con la rama principal:
    ```bash
    git pull origin main
    ```

2. **Desarrollo Acotado**:
   * Creación de una rama temporal para la tarea asignada:
    ```bash
    git checkout -b task/ID-tarea
    ```
   * Implementación de modificaciones en incrementos pequeños de código.

3. **Integración Frecuente**:
   * Reorganización del historial local con respecto a la rama principal previa a la integración:
    ```bash
    git rebase origin/main
    ```
   * Fusión de los cambios en la rama principal tras la verificación por pruebas automatizadas:
	```bash
    git merge task/ID-tarea
    ```

4. **Gestión de Funcionalidades Incompletas**:
   * El código en proceso de desarrollo que es integrado en el tronco principal debe ser aislado lógicamente mediante condicionales de control (*Feature Flags*) para evitar la exposición de código no terminado en producción.

## Notas

Este documento ha sido redactado mediante asistentes de inteligencia artificial y supervisado por **@rosendocamal**.