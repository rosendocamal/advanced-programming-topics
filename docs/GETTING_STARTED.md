# Manual para los colaboradores

## Control de versiones (git)

Para instalar `git` se requiere seguir un proceso u otro según el sistema operativo utilizado.

* Instalación para **Linux**:
```bash
sudo apt install git -y # Ubuntu

sudo dnf install git -y # Fedora
```

* Instalación en **macOS**:
```bash
brew install git # Requiere instalar primero el gestor de paquetes Homebrew
```

* La instalación en **Windows** como en **macOs** puede ser partir del paquete de instalación oficial, para ello hay que acudir a la página oficial de Git y una vez descargado el binario, ejecutar y seguir los pasos del asistente.

Independiente del método empleado, se comprueba si la instalación de `git` fue exitosa mediante:
```bash
git --version
```

## Gestor de paquetes y proyectos en Python (uv)

Para instalar el gestor de paquetes y de proyectos `uv` se emplea alguno de los dos comandos siguientes:

* Instalación para **Linux** y **macOS**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

* Instalación para **Windows**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Para comprobar si la instalación fue exitosa, se ejecuta el siguiente comando:
```bash
uv
```

`uv` gestiona dependencias de proyectos y entornos, con soporte para archivos de bloqueo, espacios de trabajo y más, similar a `rye` o `poetry`.

## Creación del proyecto

> [!IMPORTANT]
> La secuencia siguiente se ejecuta una vez (al principio del proyecto) y es efectuada por el **administrador**.

Para generar el proyecto se sigue la secuencia ulterior:

```bash
uvx --with flet-cli flet create advanced-programming-topics

cd advanced-programming-topics/

python3 --version

uv python pin 3.14.18

uv run flet run
```

A partir de este momento, se realiza la configuración de `git` y se crea el repositorio en **GitHub** (_rulesets_, agregar colaboradores, entre otras configuraciones).

## Ejecución de la aplicación


Para correr la aplicación Flet como aplicación de escritorio, se usa el siguiente comando:

```bash
uv run flet run
```

Si hay diferentes rutas o archivos para ejecutar se emplea:

```bash
uv run flet run [script] # Intercambia [script] por la ruta o archivo a ejecutar
```

Para correr la aplicación Flet como aplicación web (útil para desarrollo adaptativo rápido), se usa el siguiente comando:

```bash
uv run flet run --web [script] # Intercambia [script] por el archivo a ejecutar
```

## Trabajo colaborativo

El colaborador debe tener una cuenta en **GitHub**, tener instalado `python`, `git`, `uv` y un editor de código. Para trabajar con el proyecto debe clonar el repositorio con `git clone` y crear su rama local con `git switch -c [username_branch] develop`.

Luego debe sincronizar las dependencias con:

```bash
uv lock

uv sync
```

A partir de aquí empieza el desarrollo que le corresponde y en su rama designada, luego para guardar cambios realiza `git add` y `git commit`. Con los cambios confirmados ejecuta `git push origin [username_branch]`, se envía al repositorio remoto; se apertura una _pull request_ (solo si se va integrar a la rama `main` o `develop`) y se espera la revisión por el **administrador**. Antes de iniciar cada jornada de desarrollo quizás sea necesario realizar un `git pull`.

Ahora corresponde continuar el desarrollo y la confirmación de cambios, el envío a servidor remoto, la apertura de _pull request_ y el _code review_. Este proceso ya es cíclico. Todos los detalles, inconvenientes o conflictos se resolverán con las guías oficiales de `git` y **GitHub**, documentación de `flet` y `uv`.

Se resume el proceso:
1. Clonación del repositorio con `git clone`.
2. Actualización de dependencias y creación de rama designada (`uv lock`, `uv sync`, `git switch -c branch1.1 branch1.0`)
3. Actualización del repositorio (`git pull origin main`)
4. Fase de desarrollo de la aplicación
5. Confirmación de etapa de desarrollo de código (`git add`, `git commit`, `git push origin`)
6. Apertura de _pull request_, solo si se requiere fusionar con `develop` o `main`.
7. Se repite los pasos **3**, **4**, **5** y **6** hasta obtener el desarrollo finalizado de la aplicación.

> [!IMPORTANT]
> Cada colaborador trabajará en su rama designada, y en cada periodo se realizará una fusión con la rama `develop`. Si el desarrollo es correcto y adecuado, el código de la rama `develop` se hará fusión final con la rama `main`.

### Comandos esenciales para la colaboración

He aquí la secuencia inicial (por lo general solo se hará una vez y al principio de la colaboración) de comandos:

```bash
git clone [url]

git switch -c [username_branch] develop # Intercambia [username_branch] por el designado

uv lock

uv sync
```

Para actualizar la rama antes de cualquier desarrollo:

```bash
git pull
```

Para verificar la rama en la que uno está ubicado:

```bash
git status
```

Para la prueba de la aplicación o ejecución de la misma:

```bash
uv run flet run
```

Por cada desarrollo, corrección o escritura de código que se requiera guardar y enviar al repositorio, ejecutar los siguientes comandos:

```bash
git add .

git commit -m "[m1]" -m "[m2]" # Intercambia [m1] y [m2] por los mensajes pertinentes.

git push origin [username_branch] # Envío de los datos al servidor en la rama asignada.
```

## Fuentes de consulta

- [Trabajo colaborativo en GitHub](REPOSITORIO.md)
- [Flujo de trabajo con Git](WORKFLOW.md)
- [uv](https://docs.astral.sh/uv/)
- [Flet](https://flet.dev/docs)
- [git](https://git-scm.com/docs)
- [GitHub](https://docs.github.com/en)

## Notas

Este documento ha sido elaborado y supervisado por **@rosendocamal**.