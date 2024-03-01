import glob
import os
import platform
import random
import re
import shutil
import string
import subprocess
from importlib import resources

import typer
import yaml
from rich import print
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn

SPECS_DIR = "./specs"
SH_FILE = "lin-package.sh"
BAT_FILE = "win-package.bat"


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def check_fission_directory():
    output = os.path.isdir(SPECS_DIR)
    return output


def enumerate_functions():
    pattern = f"{SPECS_DIR}/function-*.yaml"
    function_files = glob.glob(pattern)

    regex = r"function-(.*?)\.yaml"

    specific_parts = []

    for file in function_files:
        match = re.search(regex, file)
        if match:
            specific_part = match.group(1)
            specific_parts.append(specific_part)

    specific_parts.sort()
    return specific_parts


def bold_blue(data: str):
    return typer.style(data, fg=typer.colors.BLUE, bold=True)


def read_yaml_file(prefix: str, fn_name: str):
    try:
        with open(f"{SPECS_DIR}/{prefix}-{fn_name}.yaml", "r") as file:
            data = yaml.safe_load(file)
            return True, data
    except Exception:
        return False, None


def save_yaml_file(prefix: str, fn_name: str, data):
    try:
        with open(f"{SPECS_DIR}/{prefix}-{fn_name}.yaml", "w") as file:
            yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)
        return True
    except Exception:
        return False


def replace_route(yaml_data, new_route):
    if (
        not yaml_data
        or "spec" not in yaml_data
        or (
            "ingressconfig" not in yaml_data["spec"]
            and "relativeurl" not in yaml_data["spec"]
        )
    ):
        # Load the template file as the new base for YAML data
        yaml_data = get_yaml_from_template("route")
        print(
            "[bold yellow]New spec file is being generated since default naming convention is not "
            "followed or spec file is corrupt![/bold yellow]"
            "\n:heavy_exclamation_mark:[bold red]Make sure to modify the HTTP Methods"
        )

    if "spec" in yaml_data and "ingressconfig" in yaml_data["spec"]:
        yaml_data["spec"]["ingressconfig"]["path"] = ensure_leading_slash(new_route)

    if "spec" in yaml_data and "relativeurl" in yaml_data["spec"]:
        yaml_data["spec"]["relativeurl"] = ensure_leading_slash(new_route)

    return yaml_data


def ensure_leading_slash(s):
    trimmed = s.strip()
    if not trimmed.startswith("/"):
        return "/" + trimmed
    else:
        return trimmed


def get_yaml_from_template(template_name):
    with resources.open_text("fizz_cli.templates", f"{template_name}.yaml") as file:
        content = yaml.safe_load(file)

    return content


def get_fn_route_path(fn_name: str):
    file_name = f"route-{fn_name}.yaml"
    file_path = os.path.join(SPECS_DIR, file_name)

    if os.path.isfile(file_path):
        return file_path
    else:
        return None


def delete_file_if_exists(file_path):
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            print(f"[bold green]The file {file_path} has been deleted.[/bold green]")
        else:
            # The file does not exist, so do nothing
            print(f"[bold red]The file {file_path} does not exist.[/bold red]")
    except OSError as e:
        print(f"[bold red]Error: {e.strerror}, filename: {e.filename}[/bold red]")


def rename_folder(current_fn, new_fn):
    """
    Renames a folder from current_folder_path to new_folder_path.

    Parameters:
        current_folder_path (str): The current path to the folder.
        new_folder_path (str): The new path or new name for the folder.

    Returns:
        bool: True if the folder was successfully renamed, False otherwise.
    """
    try:
        # Rename the folder
        shutil.move(f"./{current_fn}", f"./{new_fn}")
        return True
    except OSError as e:
        print(f"Error: {e}")
        return False


def update_shell_scripts(fn_name, new_fn_name):
    try:
        pushd_pattern = re.compile(rf"pushd {re.escape(fn_name)}\b")
        zip_pattern = re.compile(rf"\b{re.escape(fn_name)}.zip")

        # Replace in .sh file
        with open(SH_FILE, "r") as file:
            sh_content = file.read()
        sh_content = pushd_pattern.sub(f"pushd {new_fn_name}", sh_content)
        sh_content = zip_pattern.sub(f"{new_fn_name}.zip", sh_content)
        with open(SH_FILE, "w") as file:
            file.write(sh_content)

        # Replace in .bat file
        with open(BAT_FILE, "r") as file:
            bat_content = file.read()
        bat_content = pushd_pattern.sub(f"pushd {new_fn_name}", bat_content)
        bat_content = zip_pattern.sub(f"{new_fn_name}.zip", bat_content)
        with open(BAT_FILE, "w") as file:
            file.write(bat_content)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            try:
                if platform.system().lower() == "windows":
                    print(f"[block green]Detected windows.[/block green]")

                    progress.add_task(
                        description="Running win-package.bat...", total=None
                    )
                    subprocess.run(
                        "./win-package.bat",
                        shell=True,
                        text=False,
                        capture_output=False,
                    )
                else:
                    progress.add_task(
                        description="Running lin-package.sh...", total=None
                    )
                    subprocess.run(
                        "./lin-package.sh",
                        shell=True,
                        text=False,
                        capture_output=False,
                    )

            except Exception:
                print(
                    f"[block red]Error while running scripts. Kindly check permissions.[/block red]"
                )

        return True
    except Exception:
        return False


def get_environment_from_package_config(fn_name):
    docs = None
    with open(os.path.join(SPECS_DIR, f"package-{fn_name}.yaml"), "r") as file:
        docs = list(yaml.load_all(file, Loader=yaml.FullLoader))

    config = docs[1] if len(docs) > 1 else None

    if config and "spec" in config and "environment" in config["spec"]:
        env_name = config["spec"]["environment"]["name"]
        return env_name

    return None


def rename_fn_in_specs(fn_name, new_fn_name):
    # Delete and generate new package
    env = get_environment_from_package_config(fn_name)
    delete_file_if_exists(os.path.join(SPECS_DIR, f"package-{fn_name}.yaml"))

    subprocess.run(
        f"fission package create --sourcearchive {new_fn_name}.zip --env {env} --buildcmd './build.sh'  --name {new_fn_name} --spec",
        shell=True,
        text=False,
        capture_output=False,
    )
    replace_build_cmd(new_fn_name)
    rename_file(
        os.path.join(SPECS_DIR, f"package-{fn_name}.yaml"),
        os.path.join(SPECS_DIR, f"package-{new_fn_name}.yaml"),
    )

    rename_fn_in_fn_spec(fn_name, new_fn_name)
    rename_file(
        os.path.join(SPECS_DIR, f"function-{fn_name}.yaml"),
        os.path.join(SPECS_DIR, f"function-{new_fn_name}.yaml"),
    )

    rename_fn_in_route_spec(fn_name, new_fn_name)
    rename_file(
        os.path.join(SPECS_DIR, f"route-{fn_name}.yaml"),
        os.path.join(SPECS_DIR, f"route-{new_fn_name}.yaml"),
    )


def replace_build_cmd(fn_name):
    docs = []
    # Load all documents from the YAML file
    with open(os.path.join(SPECS_DIR, f"package-{fn_name}.yaml"), "r") as file:
        docs = list(yaml.load_all(file, Loader=yaml.FullLoader))

    # Check if there's more than one document and the second document contains 'spec'
    if len(docs) > 1 and "spec" in docs[1]:
        config = docs[1]

        # Modify 'buildcmd' in the second document
        if "buildcmd" in config["spec"]:
            del config["spec"]["buildcmd"]

        # Add or modify the 'initContainers' entry in the second document
        config["spec"]["initContainers"] = [
            {"command": ["chmod +x build.sh", "./build.sh"]}
        ]

        # Replace the modified document in the list
        docs[1] = config

    # Write the modified list of documents back to the file
    save_yaml_file_multi("package", fn_name, docs)


def save_yaml_file_multi(prefix: str, fn_name: str, data):
    try:
        with open(os.path.join(SPECS_DIR, f"{prefix}-{fn_name}.yaml"), "w") as file:
            yaml.dump_all(
                data,
                file,
                Dumper=yaml.SafeDumper,
                default_flow_style=False,
                sort_keys=False,
            )
        return True
    except Exception as e:
        print(f"Error writing YAML file: {e}")
        return False


def rename_fn_in_fn_spec(fn_name, new_fn_name):
    _, config = read_yaml_file("function", fn_name)

    config["metadata"]["name"] = new_fn_name
    config["spec"]["package"]["packageref"]["name"] = new_fn_name

    save_yaml_file("function", fn_name, config)


def rename_fn_in_route_spec(fn_name, new_fn_name):
    _, data = read_yaml_file("route", fn_name)
    data = replace_route(data, new_fn_name)
    data["metadata"]["name"] = new_fn_name
    data["spec"]["functionref"]["name"] = new_fn_name
    save_yaml_file("route", fn_name, data)


def rename_file(old_file_path, new_file_path):
    try:
        if not os.path.exists(old_file_path):
            return False

        os.rename(old_file_path, new_file_path)
        return True

    except Exception:
        return False

def delete_function(function_name: str):
    """
    Deletes the function along with its associated files and configurations.

    Parameters:
        function_name (str): The name of the function to delete.

    Returns:
        bool: True if the function was successfully deleted, False otherwise.
    """
    try:
        # Delete function YAML file
        delete_file_if_exists(os.path.join(SPECS_DIR, f"function-{function_name}.yaml"))

        # Delete route YAML file
        delete_file_if_exists(os.path.join(SPECS_DIR, f"route-{function_name}.yaml"))

        # Delete package YAML file
        delete_file_if_exists(os.path.join(SPECS_DIR, f"package-{function_name}.yaml"))

        # Delete function folder
        shutil.rmtree(os.path.join(SPECS_DIR, function_name))

        print(
            f"[bold green]Function '{function_name}' and its associated files have been deleted successfully.[/bold green]"
        )
        return True
    except Exception as e:
        print(
            f"[bold red]Error occurred while deleting function '{function_name}': {e}[/bold red]"
        )
        return False


# Define Typer app
app = typer.Typer()


@app.command()
def new(function_name: str):
    """
    Creates a new function with the given name.
    """
    print(f"Creating new function: {function_name} \n")


@app.command()
def rename(function_name: str, new_name: str):
    """
    Renames an existing function to a new name.
    """
    typer.confirm(
        "Modify folder name? NOTE: bash/bat scripts will also be modified.",
        default=True,
        abort=True,
    )
    new_fn_name = typer.prompt(
        "New function name: ", default="", show_default=False, fg=typer.colors.YELLOW
    )
    success = rename_folder(function_name, new_fn_name)

    if success:
        print("[:white_check_mark:][block green]Folder renamed.[/block green]")
    else:
        print(
            "[:heavy_exclamation_mark:][block red] Folder name not found for the exact function name.\n"
            "[:heavy_exclamation_mark:] Default folder naming convention is not being used.[/block red]"
        )

    success = update_shell_scripts(function_name, new_fn_name)
    if success:
        print(f"[block green]sh/bat scripts updated[/block green]")
    else:
        print(
            f":heavy_exclamation_mark:[block red]failed to update sh/bat scripts[/block red]"
        )

    rename_fn_in_specs(function_name, new_fn_name)
    print(f"[block green]Function renaming in specs done.[/block green]")


@app.command()
def delete(function_name: str):
    """
    Deletes an existing function and its associated files and configurations.
    """
    delete_function(function_name)

@app.command()
def i():
    exit_cli = False
    while exit_cli is False:
        typer.clear()
        new_or_existing = styled_bullet(
            "[🧰] What would you like to do?",
            [
                "Modify Existing Function",
                "Create New Function",
                "Initialise Fission",
            ],
        )

        _, idx = new_or_existing.launch()

        if idx == 0:
            exists = check_fission_directory()

            if exists:
                func_list = enumerate_functions()
                modify_existing = styled_bullet(
                    "Existing Functions: ", func_list
                )
                function_name = typer.prompt(
                    modify_existing.title,
                    type=str,
                    default=None,
                    show_choices=False,
                )

                print(
                    f"[:hammer_and_wrench:] [bold green]{function_name}[/bold green] [bold blue]Modification Options:[/bold blue]"
                )
                modification_options = styled_bullet(
                    "",
                    [
                        "Rename Route",
                        "Delete Route",
                        "Rename Function",
                        "Delete Function",
                    ],
                )

                idx = typer.prompt(
                    modification_options.title,
                    type=int,
                    default=None,
                    show_choices=False,
                )
                if idx == 0:
                    new_route = typer.prompt(
                        "New route name: ",
                        default="",
                        show_default=False,
                        fg=typer.colors.YELLOW,
                    )

                    route_rename(function_name, new_route)
                elif idx == 1:
                    route_delete(function_name)
                elif idx == 2:
                    pass
            else:
                print(
                    ":boom: [bold red]Incorrect Directory![/bold red] [yellow]Navigate to the level where "
                    "the specs folder exists.[/yellow]"
                )
        else:
            typer.echo("New")

        time.sleep(2)


if __name__ == "__main__":
    app()
