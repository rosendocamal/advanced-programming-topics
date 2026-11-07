# Manual para los colaboradores

## Gestor de paquetes y proyectos en Python (uv)

Para instalar el gestor de paquetes y de proyectos `uv` se emplea alguno de los dos comandos siguientes:

* Instalación para Linux y macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

* Instalación para Windows:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`uv` gestiona dependencias de proyectos y entornos, con soporte para archivos de bloqueo, espacios de trabajo y más, similar a `rye` o `poetry`.

## Creación del proyecto

Para generar nuestro proyecto se sigue la secuencia ulterior:

```bash
uvx --with flet-cli flet create advanced-programming-topics

cd advanced-programming-topics/

python3 --version

uv python pin 3.14.18

uv run flet run
```

A partir de este momento, se realiza la configuración de `git` y se crea el repositorio en **GitHub** (_rulesets_, agregar colaboradores, entre otras configuraciones).

> [!IMPORTANT]
> La secuencia anterior se ejecuta una vez (al principio del proyecto) y es efectuada por el **administrador**.

## Ejecución de la aplicación

> [!NOTE]
> Esta sección lo puede efectuar cualquier colaborador para prueba y ejecución de la aplicación.

Para correr la aplicación Flet como aplicación de escritorio, se usa el siguiente comando:

```bash
uv run flet run
```

Si hay diferentes rutas o archivos para ejecutar se emplea:

```bash
uv run flet run [script] # Intercambia [script] por la ruta o archivo a ejecutar
```

Para correr la aplicación Flet como aplicación web, se usa el siguiente comando:

```bash
uv run flet run --web [script] # Intercambia [script] por el archivo a ejecutar
```

## Trabajo colaborativo

> [!NOTE]
> Esta sección está disponible para cualquier colaborador.

El colaborador debe tener una cuenta en **GitHub**, tener instalado `python`, `git`, `uv` y un editor de código. Para trabajar con el proyecto debe clonar el repositorio con `git clone` y crear su rama local con `git checkout -b [branch]`.

Luego debe sincronizar las dependencias con:

```bash
uv lock

uv sync
```

A partir de aquí empieza el desarrollo que le corresponde y en su rama, luego para guardar cambios realiza `git add` y `git commit`. Con los cambios confirmados ejecuta `git push origin [branch]`, se envía al repositorio remoto, se apertura una _pull request_ y se espera la revisión por el **administrador**. Antes de abrir una _pull request_ quizás sea necesario realizar un `git pull`.

Ahora corresponde continuar el desarrollo y la confirmación de cambios, el envío a servidor remote, la apertura de _pull request_ y el _code review_. Este proceso ya es cíclico. Todos los detalles, inconvenientes o conflictos se resolverán con las guías oficiales de `git` y **GitHub**, documentación de `flet` y `uv`.

## Fuentes de consulta

- [Trabajo colaborativo en GitHub](REPOSITORIO.md)
- [Flujo de trabajo con Git](WORKFLOW.md)
- [uv](https://docs.astral.sh/uv/)
- [Flet](https://flet.dev/docs)
- [git](https://git-scm.com/docs)
- [GitHub](https://docs.github.com/en)

## Notas

Este documento ha sido elaborado y supervisado por **@rosendocamal**.
